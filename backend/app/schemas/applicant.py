from typing import Optional, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


class InsuredAssetBase(BaseModel):
    asset_type: str
    identifier: str
    asset_value: float
    year_built_or_manufactured: int
    make_model: str
    location_tier: str
    details: Optional[dict] = None


class InsuredAssetResponse(InsuredAssetBase):
    id: int
    business_id: str
    applicant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicantBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date
    gender: str
    address_line: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    annual_income: float
    credit_score: int
    occupation: str
    employment_status: str
    claims_count_5yr: int = 0


class ApplicantCreate(ApplicantBase):
    pass


class ApplicantResponse(ApplicantBase):
    id: int
    business_id: str
    age: int
    created_at: datetime
    assets: List[InsuredAssetResponse] = []

    class Config:
        from_attributes = True


class ApplicantListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ApplicantResponse]
