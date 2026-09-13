from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.db.geometry import CompatibleGeometry


class Mine(Base, UUIDMixin, TimestampMixin):
    """Operational coal mine entity."""
    __tablename__ = "mines"

    subsidiary_id: Mapped[str] = mapped_column(String(36), ForeignKey("subsidiaries.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mine_type: Mapped[str] = mapped_column(String(50), default="OPEN_CAST", nullable=False)  # OPEN_CAST, UNDERGROUND, MIXED
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, UNDER_MAINTENANCE, INACTIVE

    # PostGIS Polygon geometry for spatial boundary & center point
    boundary_geom: Mapped[Optional[str]] = mapped_column(CompatibleGeometry("POLYGON", 4326), nullable=True)
    center_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    center_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    subsidiary: Mapped["Subsidiary"] = relationship("Subsidiary", back_populates="mines")
    users: Mapped[List["User"]] = relationship("User", back_populates="mine")
    compliance_records: Mapped[List["ComplianceRecord"]] = relationship("ComplianceRecord", back_populates="mine", cascade="all, delete-orphan")
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="mine", cascade="all, delete-orphan")
    safety_observations: Mapped[List["SafetyObservation"]] = relationship("SafetyObservation", back_populates="mine", cascade="all, delete-orphan")
    grievances: Mapped[List["Grievance"]] = relationship("Grievance", back_populates="mine", cascade="all, delete-orphan")
    corrective_actions: Mapped[List["CorrectiveAction"]] = relationship("CorrectiveAction", back_populates="mine", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="mine", cascade="all, delete-orphan")
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship("RiskAssessment", back_populates="mine", cascade="all, delete-orphan")
    satellite_observations: Mapped[List["SatelliteObservation"]] = relationship("SatelliteObservation", back_populates="mine", cascade="all, delete-orphan")
