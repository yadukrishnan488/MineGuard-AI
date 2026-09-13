from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Text, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import RiskLevel


class SatelliteObservation(Base, UUIDMixin, TimestampMixin):
    """Satellite remote sensing and InSAR ground subsidence observation."""
    __tablename__ = "satellite_observations"

    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    observation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sensor: Mapped[str] = mapped_column(String(100), default="SENTINEL_1_SAR", nullable=False)
    subsidence_rate_mm_year: Mapped[float] = mapped_column(Float, nullable=False)  # negative indicates sinking ground
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False, index=True)
    
    # Coordinates of subsidence hotspots (GeoJSON array format)
    hotspot_coords_json: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    mine: Mapped["Mine"] = relationship("Mine", back_populates="satellite_observations")
