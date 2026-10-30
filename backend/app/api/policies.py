from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta
from backend.app.database import get_db
from backend.app.models.policy import Policy, PolicyEvent
from backend.app.models.quote import Quote
from backend.app.schemas.policy import (
    PolicyResponse,
    PolicyListResponse,
    PolicyIssueRequest,
    PolicyCancelRequest
)
from backend.app.models.base import RecordSource
from backend.app.utils.sequence import generate_policy_id

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("", response_model=PolicyListResponse)
def list_policies(
    status: Optional[str] = None,
    product_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Policy)
    if status:
        query = query.filter(Policy.status == status)
    if product_id:
        query = query.filter(Policy.product_id == product_id)
    if payment_status:
        query = query.filter(Policy.payment_status == payment_status)
    if search:
        query = query.filter(Policy.business_id.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Policy.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PolicyListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{id}", response_model=PolicyResponse)
def get_policy(id: int, db: Session = Depends(get_db)):
    pol = db.query(Policy).filter(Policy.id == id).first()
    if not pol:
        raise HTTPException(status_code=404, detail=f"Policy with ID {id} not found.")
    return pol


@router.post("/issue-from-quote/{quote_id}", response_model=PolicyResponse, status_code=201)
@router.post("/{quote_id}/issue", response_model=PolicyResponse, status_code=201)
def issue_policy(
    quote_id: int,
    payload: PolicyIssueRequest,
    db: Session = Depends(get_db)
):
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")

    # Core Policy Lifecycle Invariants
    if not quote.eligibility_passed:
        raise HTTPException(status_code=400, detail="Cannot issue policy for an ineligible quote.")

    if not quote.underwriting_decision or quote.underwriting_decision.decision not in ["APPROVED", "APPROVED_WITH_CONDITIONS"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot issue policy without underwriting approval (current decision: {quote.underwriting_decision.decision if quote.underwriting_decision else 'NONE'})."
        )

    if not quote.customer_accepted:
        raise HTTPException(status_code=400, detail="Cannot issue policy without customer acceptance.")

    if payload.payment_status != "PAID":
        raise HTTPException(status_code=400, detail="Payment must be PAID before policy issuance.")

    # Check if policy already exists for this quote
    existing = db.query(Policy).filter(Policy.quote_id == quote.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Policy {existing.business_id} has already been issued for this quote.")

    # Check duplicate overlapping active policy on same asset
    existing_overlap = db.query(Policy).filter(
        Policy.asset_id == quote.asset_id,
        Policy.status.in_(["ISSUED", "ACTIVE"])
    ).first()
    if existing_overlap:
        raise HTTPException(
            status_code=400,
            detail=f"Asset already has active policy {existing_overlap.business_id}. Overlapping coverage prohibited."
        )

    existing_p_bids = db.query(Policy.business_id).all()
    max_p_seq = 5000
    for (bid,) in existing_p_bids:
        try:
            parts = bid.split("-")
            if len(parts) == 3 and parts[2].isdigit():
                max_p_seq = max(max_p_seq, int(parts[2]))
        except Exception:
            pass
    pol_id = generate_policy_id(max_p_seq + 1)
    eff_date = date.today()
    exp_date = eff_date + timedelta(days=365)

    policy = Policy(
        business_id=pol_id,
        quote_id=quote.id,
        applicant_id=quote.applicant_id,
        asset_id=quote.asset_id,
        product_id=quote.product_id,
        status="ACTIVE",
        coverage_amount=quote.coverage_amount,
        deductible=quote.deductible,
        annual_premium=quote.final_premium,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=eff_date,
        expiration_date=exp_date,
        is_baseline=False,
        record_source=RecordSource.USER
    )
    db.add(policy)
    db.flush()

    ev = PolicyEvent(
        policy_id=policy.id,
        event_type="ISSUED",
        event_description=f"Policy {pol_id} issued upon customer acceptance and premium payment confirmation.",
        actor="System Underwriting Engine",
        metadata_json={"payment_amount": float(quote.final_premium), "status": "PAID"},
        record_source=RecordSource.USER
    )
    db.add(ev)
    db.commit()
    db.refresh(policy)
    return policy


@router.post("/{id}/cancel", response_model=PolicyResponse)
def cancel_policy(
    id: int,
    payload: PolicyCancelRequest,
    db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    if policy.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Policy is already cancelled.")

    policy.status = "CANCELLED"
    policy.cancellation_date = date.today()
    policy.cancellation_reason = payload.cancellation_reason

    # Preserve historical event
    ev = PolicyEvent(
        policy_id=policy.id,
        event_type="CANCELLED",
        event_description=f"Policy cancelled. Reason: {payload.cancellation_reason}",
        actor="Underwriter Operator",
        metadata_json={"cancellation_date": policy.cancellation_date.isoformat()}
    )
    db.add(ev)
    db.commit()
    db.refresh(policy)
    return policy
