from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import ActionStatus


class CorrectiveAction(Base, UUIDMixin, TimestampMixin):
    """Corrective action mandate stemming from an inspection finding or safety hazard."""
    __tablename__ = "corrective_actions"

    safety_observation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("safety_observations.id", ondelete="SET NULL"), nullable=True, index=True)
    inspection_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ActionStatus] = mapped_column(SQLEnum(ActionStatus), default=ActionStatus.PENDING, nullable=False, index=True)
    
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    safety_observation: Mapped[Optional["SafetyObservation"]] = relationship("SafetyObservation", back_populates="corrective_actions")
    inspection: Mapped[Optional["Inspection"]] = relationship("Inspection", back_populates="corrective_actions")
    mine: Mapped["Mine"] = relationship("Mine", back_populates="corrective_actions")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
