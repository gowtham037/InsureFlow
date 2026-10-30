from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from backend.app.database import get_db
from backend.app.models.renewal import Renewal
from backend.app.models.policy import Policy, PolicyEvent
from backend.app.schemas.renewal import RenewalGenerateRequest, RenewalResponse
from backend.app.utils.sequence import generate_renewal_id
from backend.app.models.base import RecordSource

router = APIRouter(prefix="/renewals", tags=["Renewals"])


@router.get("", response_model=List[RenewalResponse])
def list_renewals(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Renewal)
    if status:
        query = query.filter(Renewal.status == status)
    return query.order_by(Renewal.id.desc()).limit(limit).all()


@router.post("/generate", response_model=RenewalResponse, status_code=201)
def generate_renewal_offer(
    payload: RenewalGenerateRequest,
    db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter(Policy.id == payload.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    # Core Lifecycle Invariant: Never generate renewal for cancelled policy
    if policy.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail=f"Ineligible for renewal: Policy {policy.business_id} is CANCELLED. Renewals cannot be generated for cancelled policies."
        )

    # Determine renewal cycle year
    existing_count = db.query(Renewal).filter(Renewal.previous_policy_id == policy.id).count()
    ren_year = 2027 + existing_count
    ren_id = generate_renewal_id(policy.business_id, ren_year)

    cur_prem = float(policy.annual_premium)
    claims = policy.applicant.claims_count_5yr if policy.applicant else 0
    change_pct = 4.0 if claims == 0 else 12.0
    new_prem = round(cur_prem * (1 + change_pct / 100.0), 2)

    eff_date = policy.expiration_date + timedelta(days=365 * existing_count)
    exp_date = eff_date + timedelta(days=365)

    renewal = Renewal(
        business_id=ren_id,
        previous_policy_id=policy.id,
        new_policy_id=None,
        renewal_cycle_year=ren_year,
        status="OFFERED",
        prior_premium=cur_prem,
        renewal_premium=new_prem,
        premium_change_percent=change_pct,
        effective_date=eff_date,
        expiration_date=exp_date,
        decision_reason=f"Standard renewal cycle {ren_year} offer ({change_pct}% rate revision).",
        is_baseline=False,
        record_source=RecordSource.USER
    )
    db.add(renewal)

    ev = PolicyEvent(
        policy_id=policy.id,
        event_type="RENEWAL_OFFERED",
        event_description=f"Renewal offer {ren_id} generated for year {ren_year} with premium ${new_prem:,.2f}.",
        actor="System Renewal Engine",
        metadata_json={"renewal_id": ren_id, "renewal_premium": new_prem},
        record_source=RecordSource.USER
    )
    db.add(ev)
    db.commit()
    db.refresh(renewal)
    return renewal


@router.post("/{id}/action", response_model=RenewalResponse)
def act_on_renewal(
    id: int,
    action: str = Query(..., pattern="^(ACCEPT|DECLINE)$"),
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(Renewal.id == id).first()
    if not renewal:
        raise HTTPException(status_code=404, detail="Renewal not found.")

    if renewal.status != "OFFERED":
        raise HTTPException(status_code=400, detail=f"Cannot act on renewal in status '{renewal.status}'.")

    if action == "ACCEPT":
        renewal.status = "ACCEPTED"
        renewal.decision_reason = "Customer accepted renewal offer terms and updated premium."
    else:
        renewal.status = "DECLINED"
        renewal.decision_reason = "Customer declined renewal offer."

    db.commit()
    db.refresh(renewal)
    return renewal
