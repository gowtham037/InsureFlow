from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class EndorsementCreate(BaseModel):
    policy_id: int
    endorsement_type: str
    new_coverage_amount: float
    effective_date: date
    reason: str


class EndorsementResponse(BaseModel):
    id: int
    business_id: str
    policy_id: int
    endorsement_sequence: int
    endorsement_type: str
    effective_date: date
    prior_coverage_amount: float
    new_coverage_amount: float
    prior_premium: float
    new_premium: float
    premium_delta: float
    status: str
    reason: str
    is_baseline: Optional[bool] = False
    record_source: Optional[str] = "USER"
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
