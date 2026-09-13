import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative model with common serialization helpers."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize model columns to dictionary."""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }


def utcnow() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class UUIDMixin:
    """Mixin providing UUID primary key."""
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
