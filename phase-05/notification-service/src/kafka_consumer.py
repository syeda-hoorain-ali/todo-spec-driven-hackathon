"""Kafka consumer module for Notification Service."""
import logging
import json
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session
from .database import DatabaseManager
from .models import Notification
from ...kafka_common.config import get_kafka_consumer_config
from ...kafka_common.event_schemas import TaskCreatedEventSchema, TaskUpdatedEventSchema, TaskReminderEventSchema


logger = logging.getLogger(__name__)


class NotificationKafkaConsumer:
    """Manages Kafka consumption for notification events."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

    async def initialize(self):
        """Initialize the Kafka consumer."""
        consumer_config = get_kafka_consumer_config("notification-service")
        self.consumer = AIOKafkaConsumer(
            'task.events',  # Listen to task events
            'reminder.events',  # Listen to reminder events
            bootstrap_servers=consumer_config['bootstrap.servers'],
            group_id=consumer_config['group.id'],
            auto_offset_reset=consumer_config['auto.offset.reset'],
            enable_auto_commit=consumer_config['enable.auto.commit']
        )
        await self.consumer.start()
        logger.info("Kafka consumer initialized")

    async def start_consuming(self):
        """Start consuming Kafka events."""
        if not self.consumer:
            raise RuntimeError("Kafka consumer not initialized. Call initialize() first.")

        self.running = True
        try:
            # The consumer is already started in the initialize method, so we just consume messages
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    # Parse the message - handle case where message.value might be None
                    if message.value is None:
                        logger.warning(f"Received null message value from topic {message.topic} partition {message.partition} offset {message.offset}")
                        continue

                    event_data = json.loads(message.value.decode('utf-8'))

                    # Process the event based on type
                    event_type = event_data.get('eventType', '')

                    if event_type == 'task.created':
                        await self.handle_task_created(event_data)
                    elif event_type == 'task.updated':
                        await self.handle_task_updated(event_data)
                    elif event_type == 'task.reminder':
                        await self.handle_task_reminder(event_data)
                    else:
                        logger.info(f"Unknown event type: {event_type}")

                except Exception as e:
                    logger.error(f"Error processing notification event: {str(e)}")
                    # In a real implementation, we would send to a dead letter queue

        except Exception as e:
            logger.error(f"Error in notification event consumption loop: {str(e)}")
        finally:
            # Don't stop the consumer here as it should be managed by the application lifecycle
            pass

    async def stop_consuming(self):
        """Stop consuming Kafka events."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def handle_task_created(self, event_data: Dict[str, Any]):
        """Handle task.created events."""
        try:
            # Parse the event
            event = TaskCreatedEventSchema(**event_data)

            # Extract relevant information
            user_id = event.userId
            task_title = event.payload.title
            task_description = event.payload.description

            # Only send notification if user_id is available
            if user_id is None:
                logger.warning(f"No user_id found for task creation event: {event.eventId}")
                return

            # Create notification content
            notification_content = f"New task created: '{task_title}'"
            if task_description:
                notification_content += f"\nDescription: {task_description}"

            # Create and save notification
            notification = Notification(
                notification_id=event.eventId,
                user_id=user_id,
                notification_type="task_created",
                content=notification_content,
                status="pending",
                priority="normal",
                channel="in_app",
                related_entity_id=event.payload.taskId,
                timestamp=event.timestamp
            )

            # Save to database using SQLModel session
            with Session(self.db_manager.engine) as session:
                session.add(notification)
                session.commit()

            logger.info(f"Notification created for task creation: {event.payload.taskId}")

        except Exception as e:
            logger.error(f"Error handling task.created event: {str(e)}")

    async def handle_task_updated(self, event_data: Dict[str, Any]):
        """Handle task.updated events."""
        try:
            # Parse the event
            event = TaskUpdatedEventSchema(**event_data)

            # Extract relevant information
            user_id = event.userId
            task_id = event.payload.taskId
            changes = event.payload.newState

            # Only send notification if user_id is available
            if user_id is None:
                logger.warning(f"No user_id found for task updated event: {event.eventId}")
                return

            # Create notification about the update
            changes_desc = ", ".join(changes.keys()) if changes else "unknown fields"
            notification_content = f"Task {task_id} has been updated: {changes_desc}"

            # Create and save notification
            notification = Notification(
                notification_id=event.eventId,
                user_id=user_id,
                notification_type="task_updated",
                content=notification_content,
                status="pending",
                priority="normal",
                channel="in_app",
                related_entity_id=task_id,
                timestamp=event.timestamp
            )

            # Save to database using SQLModel session
            with Session(self.db_manager.engine) as session:
                session.add(notification)
                session.commit()

            logger.info(f"Notification created for task update: {task_id}")

        except Exception as e:
            logger.error(f"Error handling task.updated event: {str(e)}")

    async def handle_task_reminder(self, event_data: Dict[str, Any]):
        """Handle task.reminder events."""
        try:
            # Parse the event
            event = TaskReminderEventSchema(**event_data)

            # Extract relevant information
            user_id = event.userId or event_data.get('userId')
            task_title = event.payload.message or event_data.get('payload', {}).get('taskTitle', 'Unknown Task')
            reminder_type = event.payload.reminderType

            # Only send notification if user_id is available
            if user_id is None:
                logger.warning(f"No user_id found for task reminder event: {event.eventId}")
                return

            # Create reminder notification
            notification_content = f"Reminder: Task '{task_title}' is due soon!"

            # Create and save notification
            notification = Notification(
                notification_id=event.eventId,
                user_id=user_id,
                notification_type="task_reminder",
                content=notification_content,
                status="pending",
                priority="high",
                channel=reminder_type,
                related_entity_id=event.payload.taskId,
                timestamp=event.timestamp
            )

            # Save to database using SQLModel session
            with Session(self.db_manager.engine) as session:
                session.add(notification)
                session.commit()

            logger.info(f"Reminder notification created for task: {event.payload.taskId}")

        except Exception as e:
            logger.error(f"Error handling task.reminder event: {str(e)}")
