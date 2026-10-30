from typing import Optional, List, Any
from datetime import date, datetime
import re
from pydantic import BaseModel, Field, field_validator


class InsuredAssetBase(BaseModel):
    asset_type: str
    identifier: str
    asset_value: float
    year_built_or_manufactured: int
    make_model: str
    location_tier: str
    details: Optional[dict] = None
    record_source: Optional[str] = "USER"


class InsuredAssetResponse(InsuredAssetBase):
    id: int
    business_id: str
    applicant_id: int
    record_source: Optional[str] = "USER"
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicantBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date
    gender: str = "NON_BINARY"
    address_line: str = "100 Main Street"
    city: str = "Austin"
    state: str = "TX"
    postal_code: str = "78701"
    country: str = "USA"
    annual_income: float = 75000.0
    credit_score: int = 700
    occupation: str = "Professional"
    employment_status: str = "EMPLOYED"
    claims_count_5yr: int = 0
    record_source: Optional[str] = "USER"


class InsuredAssetCreate(BaseModel):
    asset_type: str = "MOTOR_VEHICLE"
    identifier: Optional[str] = None
    asset_value: float = 35000.0
    year_built_or_manufactured: int = 2021
    make_model: str = "Standard Passenger Vehicle"
    location_tier: str = "TIER_1"
    details: Optional[dict] = None


class ApplicantCreate(ApplicantBase):
    initial_asset: Optional[InsuredAssetCreate] = None

    @field_validator("phone")
    @classmethod
    def validate_phone_10_digits(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        return digits


class ApplicantResponse(ApplicantBase):
    id: int
    business_id: str
    age: int
    record_source: Optional[str] = "USER"
    source: Optional[str] = None
    created_at: datetime
    assets: List[InsuredAssetResponse] = []

    class Config:
        from_attributes = True


class ApplicantListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ApplicantResponse]
