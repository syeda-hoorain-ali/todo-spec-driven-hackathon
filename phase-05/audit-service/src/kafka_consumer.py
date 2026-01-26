"""Kafka consumer module for Audit Service."""
import logging
import json
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session
from .database import DatabaseManager
from .models import AuditLog, DeadLetterQueue
from ...kafka_common.config import get_kafka_consumer_config
from ...kafka_common.event_schemas import BaseEventSchema


logger = logging.getLogger(__name__)


class AuditKafkaConsumer:
    """Manages Kafka consumption for audit events."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

    async def initialize(self):
        """Initialize the Kafka consumer."""
        consumer_config = get_kafka_consumer_config("audit-service")
        self.consumer = AIOKafkaConsumer(
            'task.events',  # Listen to all task events
            'notification.events',  # Listen to notification events
            'user.events',  # Listen to user events
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

                    # Create audit entry based on event type
                    await self._create_audit_entry(event_data)

                    logger.info(f"Audit entry created for event: {event_data.get('eventId', 'unknown')}")

                except Exception as e:
                    logger.error(f"Error processing audit event: {str(e)}")
                    # Send failed message to dead letter queue
                    await self._send_to_dead_letter_queue(message, str(e))

        except Exception as e:
            logger.error(f"Error in audit event consumption loop: {str(e)}")
        finally:
            # Don't stop the consumer here as it should be managed by the application lifecycle
            pass

    async def stop_consuming(self):
        """Stop consuming Kafka events."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def _create_audit_entry(self, event_data: Dict[str, Any]):
        """Create an audit entry from an event."""
        try:
            # Parse the event using the base schema
            event = BaseEventSchema(**event_data)

            # Determine the operation type based on the event type
            operation = self._derive_operation_from_event_type(event.eventType)

            # Create the audit entry
            audit_entry = AuditLog(
                event_id=event.eventId,
                event_type=event.eventType,
                user_id=event.userId or event_data.get('userId', 'system'),
                entity_type=self._derive_entity_type_from_event_type(event.eventType),
                entity_id=self._extract_entity_id_from_payload(event.payload),
                operation=operation,
                timestamp=event.timestamp,
                details=json.dumps(event.payload.dict() if hasattr(event.payload, 'dict') else event.payload),
                source=event.source
            )

            # Save to database using SQLModel session
            with Session(self.db_manager.engine) as session:
                session.add(audit_entry)
                session.commit()

        except Exception as e:
            logger.error(f"Error creating audit entry: {str(e)}")

    def _derive_operation_from_event_type(self, event_type: str) -> str:
        """Derive operation type from event type."""
        if 'created' in event_type.lower():
            return 'CREATE'
        elif 'updated' in event_type.lower():
            return 'UPDATE'
        elif 'deleted' in event_type.lower():
            return 'DELETE'
        elif 'reminder' in event_type.lower():
            return 'REMIND'
        elif 'notification' in event_type.lower():
            return 'NOTIFY'
        else:
            return 'OTHER'

    def _derive_entity_type_from_event_type(self, event_type: str) -> str:
        """Derive entity type from event type."""
        if 'task' in event_type.lower():
            return 'task'
        elif 'user' in event_type.lower():
            return 'user'
        elif 'notification' in event_type.lower():
            return 'notification'
        else:
            return 'other'

    def _extract_entity_id_from_payload(self, payload: Any) -> str:
        """Extract entity ID from event payload."""
        if hasattr(payload, '__dict__'):
            payload_dict = payload.__dict__
        elif isinstance(payload, dict):
            payload_dict = payload
        else:
            payload_dict = {}

        # Look for common ID fields in the payload
        for field_name in ['taskId', 'userId', 'notificationId', 'id', 'entityId']:
            if field_name in payload_dict:
                return str(payload_dict[field_name])

        return 'unknown'

    async def _send_to_dead_letter_queue(self, message, error_message: str):
        """Send a failed message to the dead letter queue."""
        from datetime import datetime
        try:
            # Prepare the message data for insertion
            message_value = message.value.decode('utf-8') if isinstance(message.value, bytes) else str(message.value)
            message_key = message.key.decode('utf-8') if message.key and isinstance(message.key, bytes) else str(message.key) if message.key else None

            # Create the dead letter queue entry
            dlq_entry = DeadLetterQueue(
                topic=message.topic,
                partition=message.partition,
                offset_value=message.offset,
                key_val=message_key,
                value=message_value,
                error_message=error_message,
                timestamp=datetime.utcnow().isoformat()
            )

            # Save to database using SQLModel session
            with Session(self.db_manager.engine) as session:
                session.add(dlq_entry)
                session.commit()

            logger.info(f"Message sent to dead letter queue: {message.topic}[{message.partition}:{message.offset}]")

        except Exception as e:
            logger.error(f"Error sending message to dead letter queue: {str(e)}")
