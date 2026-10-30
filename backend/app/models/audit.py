from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from backend.app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(64), index=True, nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, STATE_TRANSITION
    actor = Column(String(100), default="SYSTEM", nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
