import json
import logging
from typing import Callable, Any, Dict, Optional
from confluent_kafka import Consumer, Message
from ..config import settings
from .config import get_kafka_consumer_config
from .serialization import deserialize_message
from ..monitoring.metrics import increment_counter, record_histogram, start_timer, stop_timer


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """
    Base Kafka consumer class for consuming messages from Kafka topics.
    """

    def __init__(self, group_id: Optional[str] = None):
        """
        Initialize the Kafka consumer with configuration and rebalancing support.

        Args:
            group_id: Optional consumer group ID, defaults to settings value
        """
        # Add rebalancing callbacks to the configuration
        config = get_kafka_consumer_config(group_id)

        # Set up rebalancing callbacks
        config['rebalance_cb'] = self._rebalance_callback
        config['error_cb'] = self._error_callback

        self._consumer = Consumer(config)
        self.running = True
        self.assigned_partitions = set()
        logger.info(f"Initialized Kafka consumer for group: {group_id or 'default'}")

    def _rebalance_callback(self, consumer, partitions):
        """
        Callback function for handling consumer group rebalancing.

        Args:
            consumer: The consumer instance
            partitions: List of TopicPartition objects
        """
        try:
            if consumer.rebalanced():
                # Rebalancing is happening
                if partitions:
                    # Partitions are being assigned
                    partition_list = [f"{p.topic}[{p.partition}]" for p in partitions]
                    logger.info(f"Rebalancing: Assigning partitions to consumer: {partition_list}")

                    # Update our tracking
                    self.assigned_partitions.update([f"{p.topic}[{p.partition}]" for p in partitions])
                else:
                    # Partitions are being revoked
                    logger.info(f"Rebalancing: Revoking partitions from consumer")

                    # Clear our tracking
                    self.assigned_partitions.clear()

            # Perform the default assignment
            consumer.assign(partitions)
            logger.info(f"Current assignment: {[str(p) for p in consumer.assignment()]}")
        except Exception as e:
            logger.error(f"Error in rebalance callback: {str(e)}")
            # Increment error counter
            increment_counter("kafka_rebalance_error_total", {"error_type": type(e).__name__})

    def _error_callback(self, error):
        """
        Callback function for handling consumer errors.

        Args:
            error: The error object
        """
        logger.error(f"Consumer error: {error.str() if hasattr(error, 'str') else str(error)}")
        # Increment error counter
        increment_counter("kafka_consumer_error_total", {"error_type": "general_error"})

    def subscribe(self, topics: list):
        """
        Subscribe to the specified topics.

        Args:
            topics: List of topic names to subscribe to
        """
        self._consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")

    def poll(self, timeout: float = 1.0) -> Optional[Message]:
        """
        Poll for messages from subscribed topics.

        Args:
            timeout: Timeout in seconds

        Returns:
            Message object if available, None otherwise
        """
        return self._consumer.poll(timeout=timeout)

    def consume_messages(self, callback: Callable[[Dict[str, Any]], None], max_messages: Optional[int] = None):
        """
        Consume messages continuously and process them with the provided callback
        with comprehensive error logging and metrics collection.

        Args:
            callback: Function to call with each received message
            max_messages: Optional maximum number of messages to process
        """
        message_count = 0

        while self.running:
            if max_messages and message_count >= max_messages:
                break

            # Start timing the poll operation
            start_timer("kafka_poll_duration_seconds")

            msg = self.poll(timeout=1.0)

            # Record poll duration
            stop_timer("kafka_poll_duration_seconds")

            if msg is None:
                continue

            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                increment_counter("kafka_consumer_error_total", {
                    "error_type": "poll_error",
                    "topic": getattr(msg, 'topic', lambda: 'unknown')()
                })
                continue

            try:
                # Start timing message processing
                start_timer("kafka_message_process_duration_seconds", {
                    "topic": msg.topic()
                })

                # Record message received metric
                increment_counter("kafka_messages_received_total", {
                    "topic": msg.topic(),
                    "partition": str(msg.partition())
                })

                # Record message size
                message_size = len(msg.value()) if msg.value() else 0
                record_histogram("kafka_consumed_message_size_bytes", message_size, {
                    "topic": msg.topic()
                })

                # Deserialize the message value
                message_value = deserialize_message(msg.value().decode('utf-8'))

                # Create message dict with metadata
                message_dict = {
                    'value': message_value,
                    'key': msg.key().decode('utf-8') if msg.key() else None,
                    'topic': msg.topic(),
                    'partition': msg.partition(),
                    'offset': msg.offset(),
                    'timestamp': msg.timestamp()[1],
                    'headers': {h[0]: h[1].decode('utf-8') for h in msg.headers()} if msg.headers() else None
                }

                # Process the message
                callback(message_dict)

                # Commit the offset after successful processing
                self._consumer.commit(msg)

                # Record successful processing
                increment_counter("kafka_message_process_success_total", {
                    "topic": msg.topic()
                })

                message_count += 1

            except Exception as e:
                logger.error(
                    f"Error processing message from topic {msg.topic()}, partition {msg.partition()}, offset {msg.offset()}: {str(e)}",
                    extra={
                        "topic": msg.topic(),
                        "partition": msg.partition(),
                        "offset": msg.offset(),
                        "error_type": type(e).__name__,
                        "message_key": msg.key().decode('utf-8') if msg.key() else None
                    }
                )

                # Record processing error
                increment_counter("kafka_message_process_error_total", {
                    "topic": msg.topic(),
                    "error_type": type(e).__name__
                })

                # Here we could implement dead letter queue logic
                self.handle_message_error(msg, e)
            finally:
                # Record processing duration
                stop_timer("kafka_message_process_duration_seconds", {
                    "topic": msg.topic()
                })

    def handle_message_error(self, msg: Message, error: Exception):
        """
        Handle errors that occur during message processing.

        Args:
            msg: The message that caused the error
            error: The exception that occurred
        """
        logger.error(f"Error processing message from topic {msg.topic()}, partition {msg.partition()}: {str(error)}")
        # In a real implementation, this might send to a dead letter queue

    def close(self):
        """Close the consumer and clean up resources."""
        self.running = False
        self._consumer.close()
        logger.info("Kafka consumer closed")

    @property
    def consumer(self) -> Consumer:
        """Get the underlying confluent-kafka Consumer instance."""
        return self._consumer