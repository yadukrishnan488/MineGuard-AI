from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.enums import NotificationChannel
from app.models.notification import Notification


class NotificationService:
    @staticmethod
    def send_notification(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        notification_type: str = "INFO",
        cooldown_minutes: int = 15,
    ) -> Optional[Notification]:
        """
        Dispatch notification with deduplication to prevent alert storms.
        """
        now = datetime.now(timezone.utc)
        cooldown_threshold = now - timedelta(minutes=cooldown_minutes)

        # Deduplication check: Avoid spamming identical notifications
        recent = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.notification_type == notification_type,
            Notification.title == title,
            Notification.created_at >= cooldown_threshold,
        ).first()

        if recent:
            return None  # Duplicate suppressed within cooldown period

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            channel=channel,
            notification_type=notification_type,
            is_read=False,
            delivery_status="DELIVERED",
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
