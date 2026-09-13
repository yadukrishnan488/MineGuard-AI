from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class AttendanceRecord(Base, UUIDMixin, TimestampMixin):
    """Daily worker muster roll and biometric/manual attendance."""
    __tablename__ = "attendance_records"

    worker_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    shift: Mapped[str] = mapped_column(String(20), default="SHIFT_1", nullable=False)  # SHIFT_1 (Morning), SHIFT_2 (Evening), SHIFT_3 (Night)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT", nullable=False)  # PRESENT, ABSENT, ON_LEAVE, REST_DAY
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    worker: Mapped["User"] = relationship("User", foreign_keys=[worker_id])
    mine: Mapped["Mine"] = relationship("Mine")


class WageRecord(Base, UUIDMixin, TimestampMixin):
    """Monthly wage breakdown and statutory disbursement record."""
    __tablename__ = "wage_records"

    worker_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)   # e.g., 2026
    
    base_amount: Mapped[float] = mapped_column(Float, nullable=False)
    overtime_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    deductions: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), default="PAID", nullable=False)  # PAID, PENDING, DISPUTED

    # Relationships
    worker: Mapped["User"] = relationship("User", foreign_keys=[worker_id])
    mine: Mapped["Mine"] = relationship("Mine")
