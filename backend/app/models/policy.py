from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class Policy(Base, TimestampMixin):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # POL-2026-000001
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="RESTRICT"), unique=True, nullable=False)
    applicant_id = Column(Integer, ForeignKey("applicants.id", ondelete="RESTRICT"), nullable=False)
    asset_id = Column(Integer, ForeignKey("insured_assets.id", ondelete="RESTRICT"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(30), default="ISSUED", nullable=False)  # ISSUED, ACTIVE, SUSPENDED, CANCELLED, EXPIRED
    coverage_amount = Column(Numeric(12, 2), nullable=False)
    deductible = Column(Numeric(10, 2), nullable=False)
    annual_premium = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(30), default="PAID", nullable=False)  # PAID, PENDING, FAILED, REFUNDED
    customer_accepted = Column(Boolean, default=True, nullable=False)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    cancellation_date = Column(Date, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=True, nullable=False)

    # Relationships
    quote = relationship("Quote", back_populates="policy")
    applicant = relationship("Applicant", back_populates="policies")
    asset = relationship("InsuredAsset", back_populates="policies")
    product = relationship("Product", back_populates="policies")
    policy_coverages = relationship("PolicyCoverage", back_populates="policy", cascade="all, delete-orphan")
    events = relationship("PolicyEvent", back_populates="policy", cascade="all, delete-orphan")
    endorsements = relationship("Endorsement", back_populates="policy", cascade="all, delete-orphan")
    renewals = relationship(
        "Renewal", 
        foreign_keys="Renewal.previous_policy_id",
        back_populates="previous_policy",
        cascade="all, delete-orphan"
    )


class PolicyCoverage(Base):
    __tablename__ = "policy_coverages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    coverage_option_id = Column(Integer, ForeignKey("coverage_options.id", ondelete="RESTRICT"), nullable=False)
    limit_amount = Column(Numeric(12, 2), nullable=False)
    deductible_amount = Column(Numeric(10, 2), nullable=False)
    allocated_premium = Column(Numeric(10, 2), nullable=False)

    policy = relationship("Policy", back_populates="policy_coverages")
    coverage_option = relationship("CoverageOption")


class PolicyEvent(Base):
    __tablename__ = "policy_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # CREATED, ACCEPTED, PAYMENT_RECEIVED, ISSUED, ACTIVATED, ENDORSED, RENEWAL_OFFERED, CANCELLED
    event_description = Column(Text, nullable=False)
    actor = Column(String(100), default="SYSTEM", nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    policy = relationship("Policy", back_populates="events")
