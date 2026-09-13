from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import RiskLevel


class RiskAssessment(Base, UUIDMixin, TimestampMixin):
    """AI and rule-based quantitative risk evaluation for a mine."""
    __tablename__ = "risk_assessments"

    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 100.0
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), nullable=False, index=True)
    
    # Explainability breakdown and prescriptive insights
    factors_breakdown_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    recommendations_json: Mapped[str] = mapped_column(Text, nullable=False)    # JSON string
    
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    calculated_by: Mapped[str] = mapped_column(String(100), default="SYSTEM_AI_ENGINE", nullable=False)

    # Relationships
    mine: Mapped["Mine"] = relationship("Mine", back_populates="risk_assessments")
