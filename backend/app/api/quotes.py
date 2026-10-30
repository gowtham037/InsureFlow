from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from backend.app.database import get_db
from backend.app.models.quote import Quote
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.product import Product
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.schemas.quote import QuoteCreate, QuoteResponse, QuoteListResponse
from backend.app.rules.eligibility import evaluate_eligibility
from backend.app.rules.pricing import calculate_premium
from backend.app.rules.risk_scoring import calculate_risk_score
from backend.app.rules.underwriting_rules import determine_underwriting_decision
from backend.app.schemas.applicant import InsuredAssetCreate
from backend.app.utils.sequence import generate_quote_id, generate_decision_id, generate_asset_id
from backend.app.models.base import RecordSource

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.get("", response_model=QuoteListResponse)
def list_quotes(
    status: Optional[str] = None,
    risk_tier: Optional[str] = None,
    product_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Quote)
    if status:
        query = query.filter(Quote.status == status)
    if risk_tier:
        query = query.filter(Quote.risk_tier == risk_tier)
    if product_id:
        query = query.filter(Quote.product_id == product_id)
    if search:
        query = query.filter(Quote.business_id.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Quote.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return QuoteListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{id}", response_model=QuoteResponse)
def get_quote(id: int, db: Session = Depends(get_db)):
    q = db.query(Quote).filter(Quote.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail=f"Quote with ID {id} not found.")
    return q


@router.post("", response_model=QuoteResponse, status_code=201)
def create_quote(payload: QuoteCreate, db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == payload.applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found.")

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    asset = None
    if payload.asset_id:
        asset = db.query(InsuredAsset).filter(InsuredAsset.id == payload.asset_id).first()

    # If no valid asset_id provided or found, resolve via new_asset or auto-creation
    if not asset:
        ast_payload = payload.new_asset
        if not ast_payload:
            # Check if applicant has any matching existing asset
            matching = [
                a for a in applicant.assets
                if (product.line_of_business == "MOTOR" and a.asset_type == "MOTOR_VEHICLE")
                or (product.line_of_business == "HOME" and a.asset_type == "RESIDENTIAL_PROPERTY")
                or (product.line_of_business == "HEALTH" and a.asset_type == "INDIVIDUAL_HEALTH")
            ]
            if matching:
                asset = matching[0]
            elif applicant.assets:
                asset = applicant.assets[0]
            else:
                # Auto-generate default compatible asset
                if product.line_of_business == "MOTOR":
                    ast_payload = InsuredAssetCreate(
                        asset_type="MOTOR_VEHICLE",
                        make_model="Standard Passenger Vehicle",
                        asset_value=max(payload.coverage_amount * 0.9, 25000.0),
                        year_built_or_manufactured=2021,
                        location_tier="TIER_1"
                    )
                elif product.line_of_business == "HOME":
                    ast_payload = InsuredAssetCreate(
                        asset_type="RESIDENTIAL_PROPERTY",
                        make_model="Residential Single Family",
                        asset_value=max(payload.coverage_amount, 250000.0),
                        year_built_or_manufactured=2018,
                        location_tier="TIER_2"
                    )
                else:
                    ast_payload = InsuredAssetCreate(
                        asset_type="INDIVIDUAL_HEALTH",
                        make_model="Comprehensive Health Profile",
                        asset_value=payload.coverage_amount,
                        year_built_or_manufactured=applicant.date_of_birth.year,
                        location_tier="TIER_2"
                    )

        if not asset and ast_payload:
            existing_ast_bids = db.query(InsuredAsset.business_id).all()
            max_ast_seq = 5000
            for (bid,) in existing_ast_bids:
                try:
                    parts = bid.split("-")
                    if len(parts) == 3 and parts[2].isdigit():
                        max_ast_seq = max(max_ast_seq, int(parts[2]))
                except Exception:
                    pass
            ast_business_id = generate_asset_id(max_ast_seq + 1)
            ident = ast_payload.identifier or f"ID-{ast_payload.asset_type[:3]}-{max_ast_seq + 1:06d}"
            asset = InsuredAsset(
                business_id=ast_business_id,
                applicant_id=applicant.id,
                asset_type=ast_payload.asset_type,
                identifier=ident,
                asset_value=ast_payload.asset_value,
                year_built_or_manufactured=ast_payload.year_built_or_manufactured,
                make_model=ast_payload.make_model,
                location_tier=ast_payload.location_tier,
                details=ast_payload.details or {},
                record_source=RecordSource.USER
            )
            db.add(asset)
            db.commit()
            db.refresh(asset)

    if not asset:
        raise HTTPException(status_code=400, detail="Could not determine or create an insured asset for this quote.")

    # 1. Eligibility Check
    is_eligible, elig_reasons = evaluate_eligibility(
        product_line=product.line_of_business,
        applicant_age=applicant.age,
        applicant_claims_5yr=applicant.claims_count_5yr,
        asset_value=float(asset.asset_value),
        asset_year=asset.year_built_or_manufactured,
        coverage_amount=payload.coverage_amount,
        min_coverage=float(product.min_coverage_limit),
        max_coverage=float(product.max_coverage_limit),
        min_applicant_age=product.min_applicant_age,
        max_applicant_age=product.max_applicant_age,
        asset_details=asset.details or {}
    )

    # 2. Risk Score
    risk_score, risk_tier, risk_breakdown = calculate_risk_score(
        applicant_age=applicant.age,
        credit_score=applicant.credit_score,
        claims_count=applicant.claims_count_5yr,
        asset_value=float(asset.asset_value),
        location_tier=asset.location_tier,
        product_line=product.line_of_business,
        asset_details=asset.details or {}
    )

    # 3. Premium Calculation
    final_premium, factors, explanation = calculate_premium(
        product_line=product.line_of_business,
        base_premium=float(product.base_premium),
        applicant_age=applicant.age,
        asset_value=float(asset.asset_value),
        asset_year=asset.year_built_or_manufactured,
        location_tier=asset.location_tier,
        claims_count=applicant.claims_count_5yr,
        coverage_amount=payload.coverage_amount,
        deductible=payload.deductible,
        asset_details=asset.details or {}
    )

    # 4. Underwriting Decision
    uw_dec, authority, dec_reason, conditions, rule_ids, reviewer = determine_underwriting_decision(
        is_eligible=is_eligible,
        eligibility_reasons=elig_reasons,
        risk_score=risk_score,
        risk_tier=risk_tier,
        coverage_amount=payload.coverage_amount
    )

    # Non-colliding sequence for user quotes and decisions (reserve 1..5000 for baseline)
    existing_q_bids = db.query(Quote.business_id).all()
    max_q_seq = 5000
    for (bid,) in existing_q_bids:
        try:
            parts = bid.split("-")
            if len(parts) == 3 and parts[2].isdigit():
                max_q_seq = max(max_q_seq, int(parts[2]))
        except Exception:
            pass
    b_id = generate_quote_id(max_q_seq + 1)
    status = "REJECTED" if (not is_eligible or uw_dec == "DECLINED") else "EVALUATED"

    quote = Quote(
        business_id=b_id,
        applicant_id=applicant.id,
        asset_id=asset.id,
        product_id=product.id,
        coverage_amount=payload.coverage_amount,
        deductible=payload.deductible,
        status=status,
        risk_score=risk_score,
        risk_tier=risk_tier,
        base_premium=float(product.base_premium),
        calculated_factors=factors,
        final_premium=final_premium,
        eligibility_passed=is_eligible,
        eligibility_reasons=elig_reasons,
        pricing_explanation=explanation,
        customer_accepted=False,
        expires_at=datetime.utcnow() + timedelta(days=30),
        is_baseline=False,
        record_source=RecordSource.USER
    )
    db.add(quote)
    db.flush()

    # Create UW Decision
    dec = UnderwritingDecision(
        business_id=generate_decision_id(max_q_seq + 1),
        quote_id=quote.id,
        decision=uw_dec,
        authority_level=authority,
        decision_reason=dec_reason,
        conditions=conditions,
        rule_identifiers=rule_ids,
        reviewer_name=reviewer,
        reviewed_at=datetime.utcnow(),
        is_override=False,
        record_source=RecordSource.USER
    )
    db.add(dec)
    db.commit()
    db.refresh(quote)
    return quote


@router.post("/{id}/evaluate", response_model=QuoteResponse)
def evaluate_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")

    applicant = quote.applicant
    asset = quote.asset
    product = quote.product

    is_eligible, elig_reasons = evaluate_eligibility(
        product_line=product.line_of_business,
        applicant_age=applicant.age,
        applicant_claims_5yr=applicant.claims_count_5yr,
        asset_value=float(asset.asset_value),
        asset_year=asset.year_built_or_manufactured,
        coverage_amount=float(quote.coverage_amount),
        min_coverage=float(product.min_coverage_limit),
        max_coverage=float(product.max_coverage_limit),
        min_applicant_age=product.min_applicant_age,
        max_applicant_age=product.max_applicant_age,
        asset_details=asset.details or {}
    )

    risk_score, risk_tier, _ = calculate_risk_score(
        applicant_age=applicant.age,
        credit_score=applicant.credit_score,
        claims_count=applicant.claims_count_5yr,
        asset_value=float(asset.asset_value),
        location_tier=asset.location_tier,
        product_line=product.line_of_business,
        asset_details=asset.details or {}
    )

    final_premium, factors, explanation = calculate_premium(
        product_line=product.line_of_business,
        base_premium=float(product.base_premium),
        applicant_age=applicant.age,
        asset_value=float(asset.asset_value),
        asset_year=asset.year_built_or_manufactured,
        location_tier=asset.location_tier,
        claims_count=applicant.claims_count_5yr,
        coverage_amount=float(quote.coverage_amount),
        deductible=float(quote.deductible),
        asset_details=asset.details or {}
    )

    quote.risk_score = risk_score
    quote.risk_tier = risk_tier
    quote.final_premium = final_premium
    quote.calculated_factors = factors
    quote.eligibility_passed = is_eligible
    quote.eligibility_reasons = elig_reasons
    quote.pricing_explanation = explanation
    if not is_eligible:
        quote.status = "REJECTED"
    db.commit()
    db.refresh(quote)
    return quote


@router.post("/{id}/accept", response_model=QuoteResponse)
def accept_quote(id: int, db: Session = Depends(get_db)):
    quote = db.query(Quote).filter(Quote.id == id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if not quote.eligibility_passed:
        raise HTTPException(status_code=400, detail="Cannot accept an ineligible quote.")
    if quote.underwriting_decision and quote.underwriting_decision.decision == "DECLINED":
        raise HTTPException(status_code=400, detail="Cannot accept a declined quote.")

    quote.customer_accepted = True
    quote.customer_accepted_at = datetime.utcnow()
    quote.status = "ACCEPTED"
    db.commit()
    db.refresh(quote)
    return quote
