from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class UnderwritingDecision(Base, TimestampMixin):
    __tablename__ = "underwriting_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # DEC-2026-000001
    quote_id = Column(Integer, ForeignKey("quotes.id", ondelete="CASCADE"), unique=True, nullable=False)
    decision = Column(String(30), nullable=False)  # APPROVED, APPROVED_WITH_CONDITIONS, REFERRED, DECLINED
    authority_level = Column(String(50), nullable=False)  # SYSTEM_AUTO, SENIOR_UNDERWRITER, CHIEF_UNDERWRITER, DECLINE_AUTOMATIC
    decision_reason = Column(Text, nullable=False)
    conditions = Column(JSON, nullable=True)
    rule_identifiers = Column(JSON, nullable=True)
    reviewer_name = Column(String(100), default="AutoUnderwrite Engine v1", nullable=False)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_override = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text, nullable=True)

    # Relationships
    quote = relationship("Quote", back_populates="underwriting_decision")
