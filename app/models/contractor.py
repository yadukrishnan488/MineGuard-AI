from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class Contractor(Base, UUIDMixin, TimestampMixin):
    """External contractor agency authorized for mining operations."""
    __tablename__ = "contractors"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    contact_person: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="contractors")
    contractor_workers: Mapped[List["ContractorWorker"]] = relationship("ContractorWorker", back_populates="contractor", cascade="all, delete-orphan")


class ContractorWorker(Base, UUIDMixin, TimestampMixin):
    """Contractual laborers engaged by licensed contractors."""
    __tablename__ = "contractor_workers"

    contractor_id: Mapped[str] = mapped_column(String(36), ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False, index=True)
    mine_id: Mapped[str] = mapped_column(String(36), ForeignKey("mines.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    trade: Mapped[str] = mapped_column(String(100), nullable=False)
    id_proof_number: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    contractor: Mapped["Contractor"] = relationship("Contractor", back_populates="contractor_workers")
