from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """Apex organization entity (e.g. Coal India Limited, Ministry of Coal)."""
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    subsidiaries: Mapped[List["Subsidiary"]] = relationship("Subsidiary", back_populates="organization", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    contractors: Mapped[List["Contractor"]] = relationship("Contractor", back_populates="organization")


class Subsidiary(Base, UUIDMixin, TimestampMixin):
    """Regional subsidiary company (e.g. ECL, BCCL, SECL, NCL, MCL)."""
    __tablename__ = "subsidiaries"

    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="subsidiaries")
    mines: Mapped[List["Mine"]] = relationship("Mine", back_populates="subsidiary", cascade="all, delete-orphan")
    users: Mapped[List["User"]] = relationship("User", back_populates="subsidiary")
