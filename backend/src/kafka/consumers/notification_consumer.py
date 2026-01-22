import logging
from typing import Dict, Any
from ...config import settings
from ..consumer import KafkaConsumer
from ..topics import TASK_CREATED_TOPIC, TASK_REMINDER_TOPIC
from ..dead_letter_queue import DeadLetterQueueHandler, create_dlq_handler
from ..producer import KafkaProducer
from ...services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class NotificationConsumer(KafkaConsumer):
    """
    Consumer for handling notification-related events.
    """

    def __init__(self, group_id: str = "notification-service-group"):
        """
        Initialize the notification consumer.

        Args:
            group_id: Consumer group ID for notification service
        """
        super().__init__(group_id)
        self.notification_service = NotificationService()
        self.dlq_handler = create_dlq_handler(KafkaProducer())
        self.running = True

    def process_task_created_event(self, message: Dict[str, Any]):
        """
        Process a task.created event for notifications.

        Args:
            message: The message containing task creation data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing notification for task created: {task_data.get('id', 'unknown')}")

            # Create notification for task creation
            user_id = task_data.get('user_id')
            task_title = task_data.get('title', 'Unknown Task')

            # In a real implementation, this would send actual notifications
            notification_content = f"A new task has been created: {task_title}"

            # Use notification service to send the notification
            self.notification_service.send_notification(
                user_id=user_id,
                content=notification_content,
                notification_type='task_created',
                related_entity_id=task_data.get('id')
            )

            logger.info(f"Notification sent for task creation: {task_title}")

        except Exception as e:
            logger.error(f"Error processing task.created notification: {str(e)}")
            self.dlq_handler.send_to_dead_letter_queue(
                message['value'],
                e,
                message['topic'],
                message.get('partition'),
                message.get('offset')
            )
            raise

    def process_task_reminder_event(self, message: Dict[str, Any]):
        """
        Process a task.reminder event.

        Args:
            message: The message containing reminder data
        """
        try:
            reminder_data = message['value']
            logger.info(f"Processing reminder notification: {reminder_data.get('task_id', 'unknown')}")

            # Create reminder notification
            user_id = reminder_data.get('user_id')
            task_title = reminder_data.get('task_title', 'Unknown Task')
            reminder_time = reminder_data.get('reminder_time')

            # In a real implementation, this would send actual reminder notifications
            notification_content = f"Reminder: Task '{task_title}' is due soon!"

            # Use notification service to send the reminder
            self.notification_service.send_notification(
                user_id=user_id,
                content=notification_content,
                notification_type='task_reminder',
                related_entity_id=reminder_data.get('task_id')
            )

            logger.info(f"Reminder notification sent for task: {task_title}")

        except Exception as e:
            logger.error(f"Error processing task.reminder notification: {str(e)}")
            self.dlq_handler.send_to_dead_letter_queue(
                message['value'],
                e,
                message['topic'],
                message.get('partition'),
                message.get('offset')
            )
            raise

    def process_task_updated_event(self, message: Dict[str, Any]):
        """
        Process a task.updated event for reminder adjustments.

        Args:
            message: The message containing task update data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing reminder adjustment for task updated: {task_data.get('id', 'unknown')}")

            # Get the new task state from the update
            new_state = task_data.get('payload', {}).get('newState', {})
            old_state = task_data.get('payload', {}).get('previousState', {})

            # Check if due date changed and adjust reminders accordingly
            old_due_date = old_state.get('due_date')
            new_due_date = new_state.get('due_date')

            if old_due_date != new_due_date:
                # Due date changed - need to adjust reminders
                user_id = new_state.get('user_id', task_data.get('userId'))
                task_title = new_state.get('title', 'Unknown Task')

                # Cancel old reminder and schedule new one
                notification_content = f"Reminder: Task '{task_title}' due date has been updated to {new_due_date}. Reminders adjusted accordingly."

                # Use notification service to send the reminder adjustment notice
                self.notification_service.send_notification(
                    user_id=user_id,
                    content=notification_content,
                    notification_type='task_reminder_adjustment',
                    related_entity_id=new_state.get('id')
                )

                logger.info(f"Reminder adjustment notification sent for task: {task_title}")

        except Exception as e:
            logger.error(f"Error processing task.updated reminder adjustment: {str(e)}")
            self.dlq_handler.send_to_dead_letter_queue(
                message['value'],
                e,
                message['topic'],
                message.get('partition'),
                message.get('offset')
            )
            raise

    def start_consuming(self):
        """
        Start consuming notification-related messages.
        """
        from ..topics import TASK_CREATED_TOPIC, TASK_REMINDER_TOPIC, TASK_UPDATED_TOPIC
        self.subscribe([TASK_CREATED_TOPIC, TASK_REMINDER_TOPIC, TASK_UPDATED_TOPIC])
        logger.info("Starting to consume notification-related messages...")

        def message_handler(message: Dict[str, Any]):
            topic = message['topic']
            if topic == TASK_CREATED_TOPIC:
                self.process_task_created_event(message)
            elif topic == TASK_REMINDER_TOPIC:
                self.process_task_reminder_event(message)
            elif topic == TASK_UPDATED_TOPIC:
                self.process_task_updated_event(message)
            else:
                logger.warning(f"Received unexpected topic: {topic}")

        try:
            self.consume_messages(callback=message_handler)
        except KeyboardInterrupt:
            logger.info("Stopping notification consumer...")
        finally:
            self.close()