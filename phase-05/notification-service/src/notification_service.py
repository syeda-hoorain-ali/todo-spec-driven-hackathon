"""Notification service module for sending notifications via multiple channels."""
import logging
from typing import Dict, Any, Optional
import os
from sqlmodel import Session, select
from sqlalchemy import desc
from .database import DatabaseManager
from .models import Notification, NotificationChannelPreferences
from .notification_channels import EmailNotifier, PushNotifier, SMSNotifier, InAppNotifier


logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications via multiple channels."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.email_notifier = EmailNotifier()
        self.push_notifier = PushNotifier()
        self.sms_notifier = SMSNotifier()
        self.in_app_notifier = InAppNotifier()

    async def send_notification(self, notification_id: str):
        """Process and send a notification via all enabled channels."""
        try:
            # Get the notification from the database
            with Session(self.db_manager.engine) as session:
                notification_statement = select(Notification).where(Notification.notification_id == notification_id)
                notification_result = session.exec(notification_statement).first()

                if not notification_result:
                    logger.warning(f"Notification not found: {notification_id}")
                    return

                # Get user's channel preferences
                preferences_statement = select(NotificationChannelPreferences).where(
                    NotificationChannelPreferences.user_id == notification_result.user_id
                )
                preferences_results = session.exec(preferences_statement).all()

                # Create preference map for easy lookup
                pref_map = {pref.channel: pref for pref in preferences_results}

                # Send notification via each enabled channel
                if self._is_channel_enabled(pref_map, notification_result.channel, notification_result.user_id):
                    if notification_result.channel == "email":
                        await self._send_email_notification(notification_result, pref_map.get("email"))
                    elif notification_result.channel == "push":
                        await self._send_push_notification(notification_result, pref_map.get("push"))
                    elif notification_result.channel == "sms":
                        await self._send_sms_notification(notification_result, pref_map.get("sms"))
                    else:  # in_app
                        await self._send_in_app_notification(notification_result)

                # Update notification status
                notification_result.status = "sent"
                session.add(notification_result)
                session.commit()

                logger.info(f"Notification sent to user {notification_result.user_id} via {notification_result.channel}")

        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            # Update notification status to failed
            try:
                with Session(self.db_manager.engine) as session:
                    notification_statement = select(Notification).where(Notification.notification_id == notification_id)
                    notification_result = session.exec(notification_statement).first()
                    if notification_result:
                        notification_result.status = "failed"
                        session.add(notification_result)
                        session.commit()
            except Exception as update_error:
                logger.error(f"Error updating notification status for {notification_id}: {str(update_error)}")

    def _is_channel_enabled(self, pref_map: Dict[str, NotificationChannelPreferences], channel: str, user_id: str) -> bool:
        """Check if a channel is enabled for the user."""
        if channel in pref_map:
            return pref_map[channel].enabled
        # Default to enabled if no preference is set
        return True

    async def _send_email_notification(self, notification: Notification, email_pref: Optional[NotificationChannelPreferences]):
        """Send email notification to user."""
        if not email_pref or not email_pref.email_address:
            logger.warning(f"No email address found for user {notification.user_id}")
            return

        success = await self.email_notifier.send_email(notification, email_pref.email_address)
        if not success:
            raise Exception("Failed to send email notification")

    async def _send_push_notification(self, notification: Notification, push_pref: Optional[NotificationChannelPreferences]):
        """Send push notification to user."""
        if not push_pref or not push_pref.device_token:
            logger.warning(f"No device token found for user {notification.user_id}")
            return

        success = await self.push_notifier.send_push(notification, push_pref.device_token)
        if not success:
            raise Exception("Failed to send push notification")

    async def _send_sms_notification(self, notification: Notification, sms_pref: Optional[NotificationChannelPreferences]):
        """Send SMS notification to user."""
        if not sms_pref or not sms_pref.phone_number:  # Assuming we add phone_number field to preferences
            logger.warning(f"No phone number found for user {notification.user_id}")
            return

        success = await self.sms_notifier.send_sms(notification, sms_pref.phone_number)
        if not success:
            raise Exception("Failed to send SMS notification")

    async def _send_in_app_notification(self, notification: Notification):
        """Store in-app notification for user."""
        await self.in_app_notifier.send_in_app(notification)

    async def get_user_notifications(self, user_id: str, limit: int = 100, offset: int = 0):
        """Get notifications for a specific user."""
        try:
            with Session(self.db_manager.engine) as session:
                statement = select(Notification).where(
                    Notification.user_id == user_id
                ).order_by(desc(Notification.timestamp)).offset(offset).limit(limit)

                notifications = session.exec(statement).all()

                return [self._notification_to_dict(notification) for notification in notifications]
        except Exception as e:
            logger.error(f"Error getting notifications for user {user_id}: {str(e)}")
            return []

    async def mark_notification_as_read(self, notification_id: str, user_id: str):
        """Mark a notification as read."""
        try:
            with Session(self.db_manager.engine) as session:
                statement = select(Notification).where(
                    Notification.notification_id == notification_id,
                    Notification.user_id == user_id
                )

                notification = session.exec(statement).first()

                if notification:
                    # In a real implementation, we might have a separate 'read_status' field
                    # For now, we'll just log that it was marked as read
                    logger.info(f"Notification {notification_id} marked as read for user {user_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            return False

    def _notification_to_dict(self, notification: Notification) -> Dict[str, Any]:
        """Convert notification model to dictionary."""
        return {
            'id': notification.id,
            'notification_id': notification.notification_id,
            'user_id': notification.user_id,
            'notification_type': notification.notification_type,
            'content': notification.content,
            'status': notification.status,
            'priority': notification.priority,
            'channel': notification.channel,
            'related_entity_id': notification.related_entity_id,
            'timestamp': notification.timestamp
        }
