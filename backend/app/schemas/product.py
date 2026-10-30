from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel


class CoverageOptionResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    coverage_category: str
    default_limit: float
    min_limit: float
    max_limit: float
    premium_multiplier: float
    deductible_options: Optional[Any] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    product_code: str
    name: str
    line_of_business: str
    description: str
    min_coverage_limit: float
    max_coverage_limit: float
    min_applicant_age: int
    max_applicant_age: int
    base_premium: float
    is_active: bool
    created_at: datetime
    coverage_options: List[CoverageOptionResponse] = []

    class Config:
        from_attributes = True
