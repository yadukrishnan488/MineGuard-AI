from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.db.geometry import CompatibleGeometry
from app.models.enums import InspectionStatus, SeverityLevel


class Inspection(Base, UUIDMixin, TimestampMixin):
    """Field safety audit and statutory inspection."""
    __tablename__ = "inspections"

    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    inspector_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    inspection_type: Mapped[str] = mapped_column(String(100), default="ROUTINE_SAFETY", nullable=False)
    inspection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    
    # Geolocation coordinates
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geom: Mapped[Optional[str]] = mapped_column(CompatibleGeometry("POINT", 4326), nullable=True)

    status: Mapped[InspectionStatus] = mapped_column(
        SQLEnum(InspectionStatus),
        default=InspectionStatus.REPORTED,
        nullable=False,
        index=True,
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Mobile offline synchronization tracking
    client_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True, index=True)
    offline_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    mine: Mapped["Mine"] = relationship("Mine", back_populates="inspections")
    inspector: Mapped["User"] = relationship("User", foreign_keys=[inspector_id])
    observations: Mapped[List["SafetyObservation"]] = relationship("SafetyObservation", back_populates="inspection", cascade="all, delete-orphan")
    corrective_actions: Mapped[List["CorrectiveAction"]] = relationship("CorrectiveAction", back_populates="inspection", cascade="all, delete-orphan")


class SafetyObservation(Base, UUIDMixin, TimestampMixin):
    """Specific hazard, defect, or compliance violation identified in a mine."""
    __tablename__ = "safety_observations"

    inspection_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(SQLEnum(SeverityLevel), default=SeverityLevel.MEDIUM, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), default="HAUL_ROAD", nullable=False)  # ROOF_FALL, GAS_LEAK, DUST, ELECTRICAL, PPE, etc.
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geom: Mapped[Optional[str]] = mapped_column(CompatibleGeometry("POINT", 4326), nullable=True)
    
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False, index=True)  # OPEN, UNDER_REVIEW, RESOLVED

    # Relationships
    inspection: Mapped[Optional["Inspection"]] = relationship("Inspection", back_populates="observations")
    mine: Mapped["Mine"] = relationship("Mine", back_populates="safety_observations")
    reporter: Mapped["User"] = relationship("User", foreign_keys=[reporter_id])
    corrective_actions: Mapped[List["CorrectiveAction"]] = relationship("CorrectiveAction", back_populates="safety_observation", cascade="all, delete-orphan")
