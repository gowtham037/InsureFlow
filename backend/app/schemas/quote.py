from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


class QuoteCreate(BaseModel):
    applicant_id: int
    asset_id: int
    product_id: int
    coverage_amount: float
    deductible: float


class QuoteResponse(BaseModel):
    id: int
    business_id: str
    applicant_id: int
    asset_id: int
    product_id: int
    coverage_amount: float
    deductible: float
    status: str
    risk_score: int
    risk_tier: str
    base_premium: float
    calculated_factors: Optional[dict] = None
    final_premium: float
    eligibility_passed: bool
    eligibility_reasons: Optional[List[str]] = None
    pricing_explanation: Optional[str] = None
    customer_accepted: bool
    customer_accepted_at: Optional[datetime] = None
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class QuoteListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[QuoteResponse]
