from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import UserRole


class User(Base, UUIDMixin, TimestampMixin):
    """User account with Role-Based Access Control and organizational scoping."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.WORKER, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Scoping attributes (org -> subsidiary -> mine)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    subsidiary_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("subsidiaries.id", ondelete="SET NULL"), nullable=True, index=True)
    mine_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("mines.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    subsidiary: Mapped[Optional["Subsidiary"]] = relationship("Subsidiary", back_populates="users")
    mine: Mapped[Optional["Mine"]] = relationship("Mine", back_populates="users")
    worker_profile: Mapped[Optional["WorkerProfile"]] = relationship("WorkerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    grievances: Mapped[List["Grievance"]] = relationship("Grievance", foreign_keys="[Grievance.worker_id]", back_populates="worker")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class WorkerProfile(Base, UUIDMixin, TimestampMixin):
    """Extended profile for mine workers and labourers."""
    __tablename__ = "worker_profiles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    trade: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., Heavy Earth Moving Machinery Operator, Miner
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="worker_profile")
