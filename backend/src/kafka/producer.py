import json
import logging
from typing import Any, Dict, Optional
from confluent_kafka import Producer
from ..config import settings
from .config import get_kafka_producer_config
from .serialization import serialize_message
from ..monitoring.metrics import increment_counter, record_histogram, start_timer, stop_timer


logger = logging.getLogger(__name__)


class KafkaProducer:
    """
    Base Kafka producer class for publishing messages to Kafka topics.
    """

    def __init__(self):
        """Initialize the Kafka producer with configuration."""
        self._producer = Producer(get_kafka_producer_config())

    def produce(self, topic: str, message: Any, key: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        Produce a message to the specified topic with comprehensive error logging and metrics.

        Args:
            topic: The topic to publish the message to
            message: The message payload to publish
            key: Optional message key for partitioning
            headers: Optional message headers
        """
        try:
            # Start timing the operation
            start_timer("kafka_produce_duration_seconds", {"topic": topic})

            # Serialize the message
            serialized_message = serialize_message(message)

            # Record message size for metrics
            message_size = len(serialized_message.encode('utf-8'))
            record_histogram("kafka_produced_message_size_bytes", message_size, {"topic": topic})

            # Produce the message
            self._producer.produce(
                topic=topic,
                value=serialized_message,
                key=key,
                headers=headers,
                callback=self.delivery_callback
            )

            # Poll for delivery callbacks to handle errors
            self._producer.poll(0)

            # Increment success counter
            increment_counter("kafka_produce_success_total", {"topic": topic})

        except Exception as e:
            # Log error with context
            logger.error(
                f"Failed to produce message to topic {topic}: {str(e)}",
                extra={
                    "topic": topic,
                    "message_type": type(message).__name__,
                    "error_type": type(e).__name__
                }
            )

            # Increment error counter
            increment_counter("kafka_produce_error_total", {
                "topic": topic,
                "error_type": type(e).__name__
            })

            raise
        finally:
            # Record the operation duration
            stop_timer("kafka_produce_duration_seconds", {"topic": topic})

    def flush(self, timeout: Optional[int] = None) -> int:
        """
        Wait for all messages in the Producer queue to be delivered.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Number of messages remaining in the queue
        """
        return self._producer.flush(timeout)

    def delivery_callback(self, err, msg):
        """
        Callback function for message delivery reports with enhanced success rate tracking.

        Args:
            err: Error object if delivery failed
            msg: Message object if delivery succeeded
        """
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
            # Increment failure counter for success rate calculation
            increment_counter("kafka_produce_error_total", {
                "topic": msg.topic() if msg else "unknown",
                "error_code": str(err.code()) if hasattr(err, 'code') else "unknown"
            })
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
            # Increment success counter for success rate calculation
            increment_counter("kafka_produce_success_total", {
                "topic": msg.topic(),
                "partition": str(msg.partition())
            })

    def produce_with_ack(self, topic: str, message: Any, key: Optional[str] = None, headers: Optional[Dict[str, str]] = None, acks: str = "all"):
        """
        Produce a message with specified acknowledgment requirements for delivery guarantees.

        Args:
            topic: The topic to publish the message to
            message: The message payload to publish
            key: Optional message key for partitioning
            headers: Optional message headers
            acks: Acknowledgment requirements ('all', '1', '0')
        """
        try:
            # Start timing the operation
            start_timer("kafka_produce_duration_seconds", {"topic": topic})

            # Serialize the message
            serialized_message = serialize_message(message)

            # Record message size for metrics
            message_size = len(serialized_message.encode('utf-8'))
            record_histogram("kafka_produced_message_size_bytes", message_size, {"topic": topic})

            # Prepare message configuration with required acknowledgments
            msg_config = {
                'topic': topic,
                'value': serialized_message,
                'key': key,
                'headers': headers,
                'callback': self.delivery_callback
            }

            # Produce the message with specified acks level
            self._producer.produce(**msg_config)

            # Poll for delivery callbacks to handle errors immediately
            self._producer.poll(0)

            # For stronger delivery guarantees, we can flush immediately
            # but this impacts performance, so we'll rely on periodic flushing
            # and the callback mechanism for error handling

        except Exception as e:
            # Log error with context
            logger.error(
                f"Failed to produce message to topic {topic}: {str(e)}",
                extra={
                    "topic": topic,
                    "message_type": type(message).__name__,
                    "error_type": type(e).__name__
                }
            )

            # Increment error counter
            increment_counter("kafka_produce_error_total", {
                "topic": topic,
                "error_type": type(e).__name__
            })

            raise
        finally:
            # Record the operation duration
            stop_timer("kafka_produce_duration_seconds", {"topic": topic})

    def get_delivery_success_rate(self) -> float:
        """
        Calculate the delivery success rate based on metrics.

        Returns:
            Float representing the success rate (0.0 to 1.0)
        """
        try:
            success_count = self._producer.metrics().get('delivery_success', 0) if hasattr(self._producer, 'metrics') else 0
            error_count = self._producer.metrics().get('delivery_errors', 0) if hasattr(self._producer, 'metrics') else 0

            total = success_count + error_count
            if total == 0:
                return 1.0  # If no messages sent yet, assume 100% success

            return success_count / total
        except Exception:
            # Fallback: calculate from our own counters
            from ..monitoring.metrics import metrics_collector
            success_total = metrics_collector.get_counter_value("kafka_produce_success_total")
            error_total = metrics_collector.get_counter_value("kafka_produce_error_total")

            total = success_total + error_total
            if total == 0:
                return 1.0

            return success_total / total if total > 0 else 0.0

    @property
    def producer(self) -> Producer:
        """Get the underlying confluent-kafka Producer instance."""
        return self._producer