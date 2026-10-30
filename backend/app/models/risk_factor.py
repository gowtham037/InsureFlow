from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class RiskFactor(Base, TimestampMixin):
    __tablename__ = "risk_factors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factor_code = Column(String(50), unique=True, index=True, nullable=False)  # RF-AGE-YOUNG
    category = Column(String(50), nullable=False)  # APPLICANT, ASSET, LOCATION, HEALTH, BEHAVIOR
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    base_score_impact = Column(Integer, nullable=False)  # -50 to +50 points
    premium_multiplier = Column(Numeric(6, 4), default=1.0, nullable=False)


class ApplicantRiskFactor(Base):
    __tablename__ = "applicant_risk_factors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id", ondelete="CASCADE"), nullable=False)
    risk_factor_id = Column(Integer, ForeignKey("risk_factors.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    notes = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applicant = relationship("Applicant", back_populates="risk_factors")
    risk_factor = relationship("RiskFactor")


class AssetRiskFactor(Base):
    __tablename__ = "asset_risk_factors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("insured_assets.id", ondelete="CASCADE"), nullable=False)
    risk_factor_id = Column(Integer, ForeignKey("risk_factors.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False)
    notes = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    asset = relationship("InsuredAsset", back_populates="risk_factors")
    risk_factor = relationship("RiskFactor")
