from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class Applicant(Base, TimestampMixin):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # APP-2026-000001
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)  # MALE, FEMALE, NON_BINARY
    address_line = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), default="USA", nullable=False)
    annual_income = Column(Numeric(12, 2), nullable=False)
    credit_score = Column(Integer, nullable=False)  # 300 - 850
    occupation = Column(String(100), nullable=False)
    employment_status = Column(String(50), nullable=False)  # EMPLOYED, SELF_EMPLOYED, RETIRED, UNEMPLOYED
    claims_count_5yr = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    assets = relationship("InsuredAsset", back_populates="applicant", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="applicant")
    policies = relationship("Policy", back_populates="applicant")
    risk_factors = relationship("ApplicantRiskFactor", back_populates="applicant", cascade="all, delete-orphan")
