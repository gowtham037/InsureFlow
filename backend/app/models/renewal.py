from datetime import date
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class Renewal(Base, TimestampMixin):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(64), unique=True, index=True, nullable=False)  # REN-POL-2026-000001-2027
    previous_policy_id = Column(Integer, ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False)
    new_policy_id = Column(Integer, ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)
    renewal_cycle_year = Column(Integer, nullable=False)
    status = Column(String(30), default="OFFERED", nullable=False)  # OFFERED, ACCEPTED, DECLINED, EXPIRED, INVALID_ATTEMPT
    prior_premium = Column(Numeric(10, 2), nullable=False)
    renewal_premium = Column(Numeric(10, 2), nullable=False)
    premium_change_percent = Column(Numeric(6, 2), default=0.0, nullable=False)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    decision_reason = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=True, nullable=False)

    previous_policy = relationship("Policy", foreign_keys=[previous_policy_id], back_populates="renewals")
    new_policy = relationship("Policy", foreign_keys=[new_policy_id])
