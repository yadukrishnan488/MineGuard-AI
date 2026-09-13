from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import SyncStatus


class OfflineSyncRecord(Base, UUIDMixin, TimestampMixin):
    """Audit and idempotency log for offline mobile synchronization batches."""
    __tablename__ = "offline_sync_records"

    client_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), default="INSPECTION", nullable=False)
    
    client_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    server_receipt_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.ACCEPTED, nullable=False, index=True)
    conflict_resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
