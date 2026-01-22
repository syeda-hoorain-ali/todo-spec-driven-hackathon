import logging
from typing import Dict, Any
from ...config import settings
from ..consumer import KafkaConsumer
from ..topics import TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC
from ..dead_letter_queue import DeadLetterQueueHandler, create_dlq_handler
from ..producer import KafkaProducer


logger = logging.getLogger(__name__)


class TaskConsumer(KafkaConsumer):
    """
    Consumer for handling task-related events (task.created, task.updated).
    """

    def __init__(self, group_id: str = "task-service-group"):
        """
        Initialize the task consumer.

        Args:
            group_id: Consumer group ID for task service
        """
        super().__init__(group_id)
        self.dlq_handler = create_dlq_handler(KafkaProducer())
        self.running = True

    def process_task_created_event(self, message: Dict[str, Any]):
        """
        Process a task.created event.

        Args:
            message: The message containing task creation data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing task created event: {task_data.get('id', 'unknown')}")

            # Process the task creation event
            # In a real implementation, this would update internal state, trigger workflows, etc.

            # Example processing logic:
            task_id = task_data.get('id')
            task_title = task_data.get('title', 'Unknown')

            logger.info(f"Task created: {task_title} (ID: {task_id})")

        except Exception as e:
            logger.error(f"Error processing task.created event: {str(e)}")
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
        Process a task.updated event.

        Args:
            message: The message containing task update data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing task updated event: {task_data.get('id', 'unknown')}")

            # Process the task update event
            # In a real implementation, this would update internal state, trigger workflows, etc.

            # Example processing logic:
            task_id = task_data.get('id')
            task_title = task_data.get('title', 'Unknown')

            logger.info(f"Task updated: {task_title} (ID: {task_id})")

        except Exception as e:
            logger.error(f"Error processing task.updated event: {str(e)}")
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
        Start consuming task-related messages.
        """
        self.subscribe([TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC])
        logger.info("Starting to consume task-related messages...")

        def message_handler(message: Dict[str, Any]):
            topic = message['topic']
            if topic == TASK_CREATED_TOPIC:
                self.process_task_created_event(message)
            elif topic == TASK_UPDATED_TOPIC:
                self.process_task_updated_event(message)
            else:
                logger.warning(f"Received unexpected topic: {topic}")

        try:
            self.consume_messages(callback=message_handler)
        except KeyboardInterrupt:
            logger.info("Stopping task consumer...")
        finally:
            self.close()