from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin, RecordSourceMixin


class InsuredAsset(Base, TimestampMixin, RecordSourceMixin):
    __tablename__ = "insured_assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # AST-2026-000001
    applicant_id = Column(Integer, ForeignKey("applicants.id", ondelete="CASCADE"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # MOTOR_VEHICLE, RESIDENTIAL_PROPERTY, INDIVIDUAL_HEALTH
    identifier = Column(String(100), nullable=False)  # VIN / APN / Member ID
    asset_value = Column(Numeric(12, 2), nullable=False)
    year_built_or_manufactured = Column(Integer, nullable=False)
    make_model = Column(String(100), nullable=False)
    location_tier = Column(String(30), nullable=False)  # TIER_1, TIER_2, TIER_3, HIGH_RISK_ZONE
    details = Column(JSON, nullable=True)

    # Relationships
    applicant = relationship("Applicant", back_populates="assets")
    quotes = relationship("Quote", back_populates="asset")
    policies = relationship("Policy", back_populates="asset")
    risk_factors = relationship("AssetRiskFactor", back_populates="asset", cascade="all, delete-orphan")
