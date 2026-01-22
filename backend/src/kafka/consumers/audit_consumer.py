import logging
from typing import Dict, Any
from datetime import datetime
from ...config import settings
from ..consumer import KafkaConsumer
from ..topics import TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC, AUDIT_LOG_TOPIC
from ..dead_letter_queue import DeadLetterQueueHandler, create_dlq_handler
from ..producer import KafkaProducer


logger = logging.getLogger(__name__)


class AuditConsumer(KafkaConsumer):
    """
    Consumer for handling audit logging events.
    """

    def __init__(self, group_id: str = "audit-service-group"):
        """
        Initialize the audit consumer.

        Args:
            group_id: Consumer group ID for audit service
        """
        super().__init__(group_id)
        self.dlq_handler = create_dlq_handler(KafkaProducer())
        self.running = True

    def process_task_created_event(self, message: Dict[str, Any]):
        """
        Process a task.created event for audit logging.

        Args:
            message: The message containing task creation data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing audit log for task created: {task_data.get('id', 'unknown')}")

            # Extract user identity and operation details
            user_id = task_data.get('user_id') or task_data.get('userId') or 'unknown'

            # Create audit entry for task creation
            audit_entry = {
                'entity_type': 'task',
                'entity_id': task_data.get('id') or task_data.get('payload', {}).get('taskId'),
                'operation': 'CREATE',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'title': task_data.get('title') or task_data.get('payload', {}).get('title'),
                    'description': task_data.get('description') or task_data.get('payload', {}).get('description'),
                    'status': task_data.get('status') or task_data.get('payload', {}).get('status'),
                    'due_date': task_data.get('due_date') or task_data.get('payload', {}).get('dueDate')
                },
                'source': 'task.created.event'
            }

            # Store the audit entry using the audit log service
            from ...services.audit_log_service import AuditEntry, audit_log_service
            audit_obj = AuditEntry(**{k: v for k, v in audit_entry.items() if k in ['entity_type', 'entity_id', 'operation', 'user_id', 'timestamp', 'details', 'source']})
            audit_log_service.save_audit_entry(audit_obj)

            logger.info(f"Audit log created for task creation: {audit_entry['entity_id']}")

        except Exception as e:
            logger.error(f"Error processing task.created audit log: {str(e)}")
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
        Process a task.updated event for audit logging.

        Args:
            message: The message containing task update data
        """
        try:
            task_data = message['value']
            logger.info(f"Processing audit log for task updated: {task_data.get('id', 'unknown')}")

            # Extract user identity and operation details
            user_id = task_data.get('user_id') or task_data.get('userId') or 'unknown'

            # Create audit entry for task update
            audit_entry = {
                'entity_type': 'task',
                'entity_id': task_data.get('id') or task_data.get('payload', {}).get('taskId'),
                'operation': 'UPDATE',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'details': {
                    'title': task_data.get('title') or task_data.get('payload', {}).get('title'),
                    'description': task_data.get('description') or task_data.get('payload', {}).get('description'),
                    'status': task_data.get('status') or task_data.get('payload', {}).get('status'),
                    'due_date': task_data.get('due_date') or task_data.get('payload', {}).get('dueDate')
                },
                'source': 'task.updated.event'
            }

            # Store the audit entry using the audit log service
            from ...services.audit_log_service import AuditEntry, audit_log_service
            audit_obj = AuditEntry(**{k: v for k, v in audit_entry.items() if k in ['entity_type', 'entity_id', 'operation', 'user_id', 'timestamp', 'details', 'source']})
            audit_log_service.save_audit_entry(audit_obj)

            logger.info(f"Audit log created for task update: {audit_entry['entity_id']}")

        except Exception as e:
            logger.error(f"Error processing task.updated audit log: {str(e)}")
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
        Start consuming audit-related messages.
        """
        from ..topics import TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC
        self.subscribe([TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC])
        logger.info("Starting to consume audit-related messages...")

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
            logger.info("Stopping audit consumer...")
        finally:
            self.close()