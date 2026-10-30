from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.database import get_db
from backend.app.models.endorsement import Endorsement
from backend.app.models.policy import Policy, PolicyEvent
from backend.app.schemas.endorsement import EndorsementCreate, EndorsementResponse
from backend.app.utils.sequence import generate_endorsement_id
from backend.app.models.base import RecordSource

router = APIRouter(prefix="/endorsements", tags=["Endorsements"])


@router.get("", response_model=List[EndorsementResponse])
def list_endorsements(
    policy_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Endorsement)
    if policy_id:
        query = query.filter(Endorsement.policy_id == policy_id)
    return query.order_by(Endorsement.id.desc()).limit(limit).all()


@router.post("", response_model=EndorsementResponse, status_code=201)
def create_endorsement(
    payload: EndorsementCreate,
    db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter(Policy.id == payload.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    if policy.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Cannot endorse a policy with status '{policy.status}'. Policy must be ACTIVE.")

    product = policy.product
    max_limit = float(product.max_coverage_limit)
    min_limit = float(product.min_coverage_limit)

    if payload.new_coverage_amount > max_limit or payload.new_coverage_amount < min_limit:
        raise HTTPException(
            status_code=400,
            detail=f"Requested coverage (${payload.new_coverage_amount:,.2f}) violates product limits [${min_limit:,.2f}, ${max_limit:,.2f}]."
        )

    # Calculate sequence
    existing_count = db.query(Endorsement).filter(Endorsement.policy_id == policy.id).count()
    seq = existing_count + 1
    end_id = generate_endorsement_id(policy.business_id, seq)

    prior_cov = float(policy.coverage_amount)
    new_cov = float(payload.new_coverage_amount)
    prior_prem = float(policy.annual_premium)
    new_prem = round(prior_prem * (new_cov / prior_cov), 2)
    delta = round(new_prem - prior_prem, 2)

    endorsement = Endorsement(
        business_id=end_id,
        policy_id=policy.id,
        endorsement_sequence=seq,
        endorsement_type=payload.endorsement_type,
        effective_date=payload.effective_date,
        prior_coverage_amount=prior_cov,
        new_coverage_amount=new_cov,
        prior_premium=prior_prem,
        new_premium=new_prem,
        premium_delta=delta,
        status="APPLIED",
        reason=payload.reason,
        is_baseline=False,
        record_source=RecordSource.USER
    )
    db.add(endorsement)

    # Update active policy parameters
    policy.coverage_amount = new_cov
    policy.annual_premium = new_prem

    # Record event
    ev = PolicyEvent(
        policy_id=policy.id,
        event_type="ENDORSED",
        event_description=f"Endorsement {end_id} applied: coverage updated to ${new_cov:,.2f}, premium updated to ${new_prem:,.2f} (delta: ${delta:,.2f}).",
        actor="Underwriting Operator",
        metadata_json={"endorsement_id": end_id, "delta": delta},
        record_source=RecordSource.USER
    )
    db.add(ev)
    db.commit()
    db.refresh(endorsement)
    return endorsement
