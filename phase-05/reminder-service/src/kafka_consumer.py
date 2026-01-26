"""Kafka consumer module for Reminder Service."""
import logging
import json
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaConsumer
from .database import DatabaseManager
from .reminder_scheduler import ReminderScheduler
from ...kafka_common.config import get_kafka_consumer_config


logger = logging.getLogger(__name__)


class ReminderKafkaConsumer:
    """Manages Kafka consumption for reminder events."""

    def __init__(self, db_manager: DatabaseManager, scheduler: ReminderScheduler):
        self.db_manager = db_manager
        self.scheduler = scheduler
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

    async def initialize(self):
        """Initialize the Kafka consumer."""
        consumer_config = get_kafka_consumer_config("reminder-service")
        self.consumer = AIOKafkaConsumer(
            'task.events',  # Listen to task events that might affect reminders
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

                    if event_type in ['task.updated', 'task.deleted']:
                        await self.handle_task_change(event_data)

                except Exception as e:
                    logger.error(f"Error processing task update event: {str(e)}")

        except Exception as e:
            logger.error(f"Error in task update consumption loop: {str(e)}")
        finally:
            # Don't stop the consumer here as it should be managed by the application lifecycle
            pass

    async def stop_consuming(self):
        """Stop consuming Kafka events."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def handle_task_change(self, event_data: Dict[str, Any]):
        """Handle task update/deletion events to adjust reminders."""
        try:
            event_type = event_data.get('eventType', '')
            task_id = event_data.get('payload', {}).get('taskId') or event_data.get('payload', {}).get('entityId')

            if event_type == 'task.updated':
                # Check if due date changed and adjust reminders accordingly
                new_due_date = event_data.get('payload', {}).get('newState', {}).get('dueDate')
                old_due_date = event_data.get('payload', {}).get('previousState', {}).get('dueDate')

                if new_due_date != old_due_date:
                    logger.info(f"Task {task_id} due date changed from {old_due_date} to {new_due_date}, adjusting reminders")
                    await self.scheduler.adjust_reminders_for_task(task_id, new_due_date)

            elif event_type == 'task.deleted':
                # Cancel any scheduled reminders for this task
                logger.info(f"Task {task_id} deleted, cancelling reminders")
                await self.scheduler.cancel_reminders_for_task(task_id)

        except Exception as e:
            logger.error(f"Error handling task change event: {str(e)}")
