from sqlalchemy import Column, String
from database import Base

from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime, timezone


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    priority = Column(String(10), nullable=False)


class AuditRecord(Base):
    __tablename__ = "audit_records"

    record_id = Column(String(36), primary_key=True)
    decision = Column(String(30), nullable=False)
    execution = Column(String(30), nullable=False)
    verification = Column(String(30), nullable=False)
    outcome = Column(String(30), nullable=False)
    evidence = Column(Text, nullable=True)
    timestamp = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
