import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .producer import KafkaProducer
from .topics import AUDIT_LOG_TOPIC, TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC, TASK_REMINDER_TOPIC
from ..monitoring.metrics import increment_counter, record_histogram


logger = logging.getLogger(__name__)


class DeadLetterQueueHandler:
    """
    Handler for managing dead letter queue functionality with monitoring and alerting.
    """

    def __init__(self, producer: KafkaProducer):
        """
        Initialize the dead letter queue handler.

        Args:
            producer: Kafka producer instance for sending dead letters
        """
        self._producer = producer
        self._dlq_topic = "system.dlq.events"  # Dedicated DLQ topic

    def send_to_dead_letter_queue(
        self,
        original_message: Dict[str, Any],
        error: Exception,
        topic: str,
        partition: Optional[int] = None,
        offset: Optional[int] = None
    ):
        """
        Send a failed message to the dead letter queue with monitoring.

        Args:
            original_message: The original message that failed processing
            error: The error that occurred during processing
            topic: The topic the original message came from
            partition: The partition the original message came from
            offset: The offset of the original message
        """
        try:
            # Create dead letter message with error details
            dead_letter_message = {
                'original_message': original_message,
                'error': str(error),
                'error_type': type(error).__name__,
                'topic': topic,
                'partition': partition,
                'offset': offset,
                'timestamp': datetime.utcnow().isoformat(),
                'processed_at': datetime.utcnow().isoformat(),
                'source_host': 'todo-chatbot-backend'
            }

            # Send to dedicated dead letter queue topic
            self._producer.produce(
                topic=self._dlq_topic,
                message=dead_letter_message,
                key=f"dlq-{topic}-{partition or 0}-{offset or 0}"
            )

            # Monitor the DLQ event
            self._monitor_dlq_event(topic, type(error).__name__)

            logger.warning(f"Sent message to dead letter queue: {topic}[{partition}] offset {offset}, error: {str(error)}")

        except Exception as dlq_error:
            logger.error(f"Failed to send message to dead letter queue: {str(dlq_error)}")
            # As a last resort, log the original error and dead letter message
            logger.error(f"Original message: {json.dumps(original_message, indent=2)}")
            logger.error(f"Processing error: {str(error)}")
            logger.error(f"DLQ error: {str(dlq_error)}")

            # Increment error counter for DLQ failures
            increment_counter("dlq_send_failures_total", {"error_type": type(dlq_error).__name__})

    def _monitor_dlq_event(self, topic: str, error_type: str):
        """
        Monitor and record metrics for dead letter queue events.

        Args:
            topic: The topic the failed message came from
            error_type: The type of error that occurred
        """
        # Increment DLQ event counter
        increment_counter("dlq_events_total", {
            "topic": topic,
            "error_type": error_type
        })

        # Record histogram for DLQ events
        record_histogram("dlq_event_size_bytes", len(json.dumps({
            "topic": topic,
            "error_type": error_type
        })))

        # In a real implementation, this could trigger alerts based on thresholds
        # For example, if DLQ events exceed a certain rate, send an alert
        logger.info(f"DLQ event monitored: topic={topic}, error_type={error_type}")

    def get_dlq_stats(self) -> Dict[str, Any]:
        """
        Get statistics about dead letter queue events.

        Returns:
            Dictionary with DLQ statistics
        """
        # In a real implementation, this would query metrics storage
        # For now, returning placeholder stats
        return {
            "total_dlq_events": 0,  # This would come from metrics
            "recent_errors": [],    # This would come from recent logs or metrics
            "error_types": {},      # This would come from aggregated metrics
        }


def create_dlq_handler(producer: KafkaProducer) -> DeadLetterQueueHandler:
    """
    Factory function to create a dead letter queue handler.

    Args:
        producer: Kafka producer instance for sending dead letters

    Returns:
        DeadLetterQueueHandler instance
    """
    return DeadLetterQueueHandler(producer)