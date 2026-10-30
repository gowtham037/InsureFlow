from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin, RecordSourceMixin


class Quote(Base, TimestampMixin, RecordSourceMixin):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # QTE-2026-000001
    applicant_id = Column(Integer, ForeignKey("applicants.id", ondelete="RESTRICT"), nullable=False)
    asset_id = Column(Integer, ForeignKey("insured_assets.id", ondelete="RESTRICT"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    coverage_amount = Column(Numeric(12, 2), nullable=False)
    deductible = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False)  # DRAFT, EVALUATED, ACCEPTED, REJECTED, EXPIRED
    risk_score = Column(Integer, default=0, nullable=False)
    risk_tier = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    base_premium = Column(Numeric(10, 2), default=0.0, nullable=False)
    calculated_factors = Column(JSON, nullable=True)
    final_premium = Column(Numeric(10, 2), default=0.0, nullable=False)
    eligibility_passed = Column(Boolean, default=True, nullable=False)
    eligibility_reasons = Column(JSON, nullable=True)
    pricing_explanation = Column(Text, nullable=True)
    customer_accepted = Column(Boolean, default=False, nullable=False)
    customer_accepted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_baseline = Column(Boolean, default=False, nullable=False)

    # Relationships
    applicant = relationship("Applicant", back_populates="quotes")
    asset = relationship("InsuredAsset", back_populates="quotes")
    product = relationship("Product", back_populates="quotes")
    quote_coverages = relationship("QuoteCoverage", back_populates="quote", cascade="all, delete-orphan")
    underwriting_decision = relationship("UnderwritingDecision", back_populates="quote", uselist=False)
    policy = relationship("Policy", back_populates="quote", uselist=False)


class QuoteCoverage(Base):
    __tablename__ = "quote_coverages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    coverage_option_id = Column(Integer, ForeignKey("coverage_options.id", ondelete="RESTRICT"), nullable=False)
    limit_amount = Column(Numeric(12, 2), nullable=False)
    deductible_amount = Column(Numeric(10, 2), nullable=False)
    allocated_premium = Column(Numeric(10, 2), nullable=False)

    quote = relationship("Quote", back_populates="quote_coverages")
    coverage_option = relationship("CoverageOption")
