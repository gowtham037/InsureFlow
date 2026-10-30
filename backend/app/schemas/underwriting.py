from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


class UnderwritingReviewRequest(BaseModel):
    decision: str  # APPROVED, APPROVED_WITH_CONDITIONS, DECLINED
    reviewer_name: str
    override_reason: Optional[str] = None
    conditions: Optional[List[str]] = None


class UnderwritingDecisionResponse(BaseModel):
    id: int
    business_id: str
    quote_id: int
    decision: str
    authority_level: str
    decision_reason: str
    conditions: Optional[List[str]] = None
    rule_identifiers: Optional[List[str]] = None
    reviewer_name: str
    reviewed_at: datetime
    is_override: bool
    override_reason: Optional[str] = None

    class Config:
        from_attributes = True


class ReferralItemResponse(BaseModel):
    quote_id: int
    quote_business_id: str
    applicant_name: str
    product_name: str
    coverage_amount: float
    risk_score: int
    risk_tier: str
    final_premium: float
    decision: str
    decision_reason: str
    authority_level: str
    created_at: datetime
