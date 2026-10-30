from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class RenewalGenerateRequest(BaseModel):
    policy_id: int


class RenewalResponse(BaseModel):
    id: int
    business_id: str
    previous_policy_id: int
    new_policy_id: Optional[int] = None
    renewal_cycle_year: int
    status: str
    prior_premium: float
    renewal_premium: float
    premium_change_percent: float
    effective_date: date
    expiration_date: date
    decision_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
