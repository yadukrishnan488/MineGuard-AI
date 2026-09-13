from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import ComplianceCategory, ComplianceStatus


class ComplianceRequirement(Base, UUIDMixin, TimestampMixin):
    """Statutory and institutional compliance mandates (DGMS, CPCB, Ministry of Coal)."""
    __tablename__ = "compliance_requirements"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[ComplianceCategory] = mapped_column(SQLEnum(ComplianceCategory), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    statutory_act: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g., Mines Act 1952, Coal Mines Regulations 2017
    frequency: Mapped[str] = mapped_column(String(50), default="ANNUAL", nullable=False)  # MONTHLY, QUARTERLY, ANNUAL, EVENT_BASED

    # Relationships
    records: Mapped[List["ComplianceRecord"]] = relationship("ComplianceRecord", back_populates="requirement", cascade="all, delete-orphan")


class ComplianceRecord(Base, UUIDMixin, TimestampMixin):
    """Mine-specific compliance submission and audit status."""
    __tablename__ = "compliance_records"

    requirement_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    submission_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ComplianceStatus] = mapped_column(SQLEnum(ComplianceStatus), default=ComplianceStatus.PENDING, nullable=False, index=True)
    assigned_officer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    requirement: Mapped["ComplianceRequirement"] = relationship("ComplianceRequirement", back_populates="records")
    mine: Mapped["Mine"] = relationship("Mine", back_populates="compliance_records")
    assigned_officer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_officer_id])
    document: Mapped[Optional["Document"]] = relationship("Document", foreign_keys=[document_id])
