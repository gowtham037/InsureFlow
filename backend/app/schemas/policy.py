from typing import Optional, List, Any
from datetime import date, datetime
from pydantic import BaseModel


class PolicyEventResponse(BaseModel):
    id: int
    event_type: str
    event_description: str
    actor: str
    metadata_json: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    id: int
    business_id: str
    quote_id: int
    applicant_id: int
    asset_id: int
    product_id: int
    status: str
    coverage_amount: float
    deductible: float
    annual_premium: float
    payment_status: str
    customer_accepted: bool
    effective_date: date
    expiration_date: date
    cancellation_date: Optional[date] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    events: List[PolicyEventResponse] = []

    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PolicyResponse]


class PolicyIssueRequest(BaseModel):
    payment_status: str = "PAID"


class PolicyCancelRequest(BaseModel):
    cancellation_reason: str
