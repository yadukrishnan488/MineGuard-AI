from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import GrievanceCategory, GrievanceStatus, GrievancePriority


class Grievance(Base, UUIDMixin, TimestampMixin):
    """Worker and employee grievance record with confidentiality controls."""
    __tablename__ = "grievances"

    complaint_reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    worker_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    
    category: Mapped[GrievanceCategory] = mapped_column(SQLEnum(GrievanceCategory), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[GrievancePriority] = mapped_column(SQLEnum(GrievancePriority), default=GrievancePriority.MEDIUM, nullable=False, index=True)
    status: Mapped[GrievanceStatus] = mapped_column(SQLEnum(GrievanceStatus), default=GrievanceStatus.PENDING, nullable=False, index=True)
    
    assigned_officer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    worker: Mapped["User"] = relationship("User", foreign_keys=[worker_id], back_populates="grievances")
    mine: Mapped["Mine"] = relationship("Mine", back_populates="grievances")
    assigned_officer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_officer_id])
