from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.database import get_db
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.models.quote import Quote
from backend.app.schemas.underwriting import UnderwritingDecisionResponse, UnderwritingReviewRequest, ReferralItemResponse

router = APIRouter(prefix="/underwriting", tags=["Underwriting"])


@router.get("/decisions", response_model=List[UnderwritingDecisionResponse])
def list_decisions(
    decision: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(UnderwritingDecision)
    if decision:
        query = query.filter(UnderwritingDecision.decision == decision)
    return query.order_by(UnderwritingDecision.id.desc()).limit(limit).all()


@router.get("/referrals", response_model=List[ReferralItemResponse])
def list_referrals(db: Session = Depends(get_db)):
    referrals = (
        db.query(UnderwritingDecision)
        .filter(UnderwritingDecision.decision == "REFERRED")
        .order_by(UnderwritingDecision.id.desc())
        .all()
    )
    result = []
    for ref in referrals:
        q = ref.quote
        app = q.applicant if q else None
        prod = q.product if q else None
        result.append(ReferralItemResponse(
            quote_id=q.id if q else 0,
            quote_business_id=q.business_id if q else "",
            applicant_name=f"{app.first_name} {app.last_name}" if app else "Unknown",
            product_name=prod.name if prod else "Unknown",
            coverage_amount=float(q.coverage_amount) if q else 0.0,
            risk_score=q.risk_score if q else 0,
            risk_tier=q.risk_tier if q else "HIGH",
            final_premium=float(q.final_premium) if q else 0.0,
            decision=ref.decision,
            decision_reason=ref.decision_reason,
            authority_level=ref.authority_level,
            created_at=ref.reviewed_at
        ))
    return result


@router.post("/{id}/review", response_model=UnderwritingDecisionResponse)
def review_decision(
    id: int,
    payload: UnderwritingReviewRequest,
    db: Session = Depends(get_db)
):
    dec = db.query(UnderwritingDecision).filter(UnderwritingDecision.id == id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Underwriting decision record not found.")

    valid_decisions = ["APPROVED", "APPROVED_WITH_CONDITIONS", "DECLINED"]
    if payload.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Must be one of {valid_decisions}")

    dec.decision = payload.decision
    dec.reviewer_name = payload.reviewer_name
    dec.is_override = True
    dec.override_reason = payload.override_reason or "Manual underwriter workbench adjudication"
    dec.reviewed_at = datetime.utcnow()
    if payload.conditions:
        dec.conditions = payload.conditions

    # Update quote status accordingly
    quote = dec.quote
    if quote:
        if payload.decision == "DECLINED":
            quote.status = "REJECTED"
        elif payload.decision in ["APPROVED", "APPROVED_WITH_CONDITIONS"]:
            if quote.customer_accepted:
                quote.status = "ACCEPTED"
            else:
                quote.status = "EVALUATED"

    db.commit()
    db.refresh(dec)
    return dec
