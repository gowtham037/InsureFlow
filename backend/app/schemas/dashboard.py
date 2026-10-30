from typing import List, Dict, Any
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_applicants: int
    total_quotes: int
    issued_policies: int
    active_policies: int
    pending_underwriting_reviews: int
    renewals: int
    total_anomalies: int
    approval_rate: float
    rejection_rate: float
    referral_rate: float


class DashboardMetrics(BaseModel):
    total_quotes_evaluated: int
    approval_rate: float
    decline_rate: float
    referral_rate: float
    total_policies_issued: int
    renewal_acceptance_rate: float
    cancellation_rate: float
    average_premium: float
    average_risk_score: float
    total_anomalies: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    dataset_validation_pass_rate: float


class ProductDistributionItem(BaseModel):
    product_code: str
    product_name: str
    line_of_business: str
    policy_count: int
    quote_count: int
    total_premium: float


class RiskDistributionItem(BaseModel):
    risk_tier: str
    quote_count: int
    policy_count: int
    average_score: float
