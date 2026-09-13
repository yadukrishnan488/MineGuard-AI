from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.enums import NotificationChannel


class Notification(Base, UUIDMixin, TimestampMixin):
    """User notifications across in-app, email, and mobile push channels."""
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(SQLEnum(NotificationChannel), default=NotificationChannel.IN_APP, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100), default="INFO", nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    delivery_status: Mapped[str] = mapped_column(String(50), default="DELIVERED", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
