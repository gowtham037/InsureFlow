from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from backend.app.database import Base
from backend.app.models.base import TimestampMixin


class AnomalyRecord(Base, TimestampMixin):
    __tablename__ = "anomaly_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_id = Column(String(32), unique=True, index=True, nullable=False)  # ANM-2026-000001
    entity_type = Column(String(50), nullable=False)  # POLICY, PREMIUM, ENDORSEMENT, RENEWAL, POLICY_PERIOD
    entity_id = Column(String(64), index=True, nullable=False)  # POL-2026-000001
    issue_type = Column(String(50), index=True, nullable=False)
    # ISSUANCE_WITHOUT_ACCEPTANCE, PREMIUM_FORMULA_MISMATCH, ENDORSEMENT_LIMIT_EXCEEDED,
    # RENEWAL_ON_CANCELLED_POLICY, OVERLAPPING_POLICY_PERIOD
    severity = Column(String(20), default="HIGH", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    expected_outcome = Column(Text, nullable=False)
    actual_detected_outcome = Column(Text, nullable=False)
    is_detected = Column(Boolean, default=True, nullable=False)
    ground_truth_label = Column(Boolean, default=False, nullable=False)
    detection_rule = Column(String(100), nullable=False)
    detection_explanation = Column(Text, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
