from datetime import date
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class Endorsement(Base, TimestampMixin):
    __tablename__ = "endorsements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(64), unique=True, index=True, nullable=False)  # END-POL-2026-000001-001
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    endorsement_sequence = Column(Integer, default=1, nullable=False)
    endorsement_type = Column(String(50), nullable=False)  # COVERAGE_LIMIT_CHANGE, ASSET_VALUE_UPDATE, DEDUCTIBLE_CHANGE
    effective_date = Column(Date, nullable=False)
    prior_coverage_amount = Column(Numeric(12, 2), nullable=False)
    new_coverage_amount = Column(Numeric(12, 2), nullable=False)
    prior_premium = Column(Numeric(10, 2), nullable=False)
    new_premium = Column(Numeric(10, 2), nullable=False)
    premium_delta = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), default="APPLIED", nullable=False)  # APPROVED, APPLIED, REJECTED
    reason = Column(Text, nullable=False)
    is_baseline = Column(Boolean, default=True, nullable=False)

    policy = relationship("Policy", back_populates="endorsements")
