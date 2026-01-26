"""Module for handling different notification channels."""
import logging
import os
from typing import Optional
import aiohttp
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import Notification, NotificationChannelPreferences


logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handles email notifications."""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

        # Check if email is properly configured
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, email notifications will be disabled")
            self.enabled = False
        else:
            self.enabled = True

    async def send_email(self, notification: Notification, email_address: str):
        """Send an email notification."""
        if not self.enabled:
            logger.warning("SMTP credentials not configured, skipping email notification")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username or 'noreply@example.com'
            msg['To'] = email_address
            msg['Subject'] = f"Todo App Notification: {notification.notification_type.replace('_', ' ').title()}"

            # Add content
            msg.attach(MIMEText(notification.content, 'plain'))

            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            sender_email = self.smtp_username or 'noreply@example.com'
            server.sendmail(sender_email, email_address, text)
            server.quit()

            logger.info(f"Email notification sent to {email_address}")
            return True
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False


class PushNotifier:
    """Handles push notifications."""

    def __init__(self):
        # Initialize push notification service (Firebase, APNs, etc.)
        self.fcm_server_key = os.getenv("FCM_SERVER_KEY")
        self.enabled = bool(self.fcm_server_key)

    async def send_push(self, notification: Notification, device_token: str):
        """Send a push notification."""
        if not self.enabled:
            logger.warning("Push notification service not configured, skipping push notification")
            return False

        try:
            # In a real implementation, this would use Firebase Cloud Messaging or Apple Push Notification Service

            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'to': device_token,
                'notification': {
                    'title': f'Todo App: {notification.notification_type.replace("_", " ").title()}',
                    'body': notification.content
                },
                'data': {
                    'notification_id': notification.notification_id,
                    'user_id': notification.user_id
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post('https://fcm.googleapis.com/fcm/send',
                                      headers=headers, json=payload) as response:
                    result = await response.json()

                    if response.status == 200:
                        logger.info(f"Push notification sent to device {device_token[:10]}...")
                        return True
                    else:
                        logger.error(f"Failed to send push notification: {result}")
                        return False

        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False


class SMSNotifier:
    """Handles SMS notifications."""

    def __init__(self):
        # Initialize SMS service (Twilio, AWS SNS, etc.)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.enabled = bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_phone_number)

    async def send_sms(self, notification: Notification, phone_number: str):
        """Send an SMS notification."""
        if not self.enabled:
            logger.warning("SMS service not configured, skipping SMS notification")
            return False

        try:
            # In a real implementation, this would use Twilio or another SMS service
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'To': phone_number,
                'From': self.twilio_phone_number,
                'Body': f'Todo App Notification: {notification.content}'
            }

            # Encode credentials in URL for basic auth
            credentials = base64.b64encode(f"{self.twilio_account_sid}:{self.twilio_auth_token}".encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'

            async with aiohttp.ClientSession() as session:
                async with session.post(f'https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json',
                                      headers=headers, data=data) as response:
                    result = await response.json()

                    if response.status == 201:
                        logger.info(f"SMS notification sent to {phone_number}")
                        return True
                    else:
                        logger.error(f"Failed to send SMS notification: {result}")
                        return False

        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
            return False


class InAppNotifier:
    """Handles in-app notifications."""

    def __init__(self):
        # Initialize WebSocket or real-time notification service
        pass

    async def send_in_app(self, notification: Notification):
        """Trigger in-app notification via WebSocket or similar."""
        # In a real implementation, this would trigger WebSocket updates for real-time delivery
        # This might involve sending to a WebSocket connection, Redis pub/sub, or similar

        logger.info(f"In-app notification stored for user {notification.user_id}: {notification.content}")

        # In a real system, we might:
        # 1. Publish to a WebSocket channel
        # 2. Send to a real-time messaging service
        # 3. Update a user's notification feed in real-time
        # For now, we just log that it's available
        return True
