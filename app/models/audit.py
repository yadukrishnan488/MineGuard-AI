from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin


class AuditLog(Base, UUIDMixin):
    """
    Append-only tamper-evident audit log.
    Records are cryptographically linked using a SHA-256 hash chain:
    current_hash = SHA256(prev_hash + actor_id + action + entity_type + entity_id + timestamp + change_metadata)
    """
    __tablename__ = "audit_logs"

    actor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    change_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string

    # Cryptographic hash chain pointers
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # Relationships
    actor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[actor_id])
