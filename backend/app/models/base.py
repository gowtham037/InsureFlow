from datetime import datetime
from sqlalchemy import Column, DateTime, String
from backend.app.database import Base


class RecordSource:
    GENERATED = "GENERATED"
    USER = "USER"
    INJECTED = "INJECTED"


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RecordSourceMixin:
    record_source = Column(String(30), default=RecordSource.USER, nullable=False, index=True)

    @property
    def source(self) -> str:
        return self.record_source

    @source.setter
    def source(self, value: str):
        self.record_source = value

