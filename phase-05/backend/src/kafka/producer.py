"""
Kafka producer for the Todo Chatbot application.
"""
import json
import logging
from typing import Dict, Any, Optional
from confluent_kafka import Producer
from .config import get_kafka_producer_config
from ..config.settings import settings


logger = logging.getLogger(__name__)


class KafkaProducer:
    """
    Wrapper class for Kafka producer with connection pooling and error handling.
    """

    def __init__(self):
        """
        Initialize the Kafka producer with configuration.
        """
        self._producer = Producer(get_kafka_producer_config())
        logger.info("KafkaProducer initialized with configuration")

    def produce(self, topic: str, message: Any, key: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        Produce a message to the specified topic.

        Args:
            topic: The topic to publish the message to
            message: The message payload to publish
            key: Optional message key for partitioning
            headers: Optional message headers
        """
        try:
            # Serialize the message
            if isinstance(message, dict):
                message_str = json.dumps(message, default=str)
            else:
                message_str = str(message)

            # Encode the message to bytes
            encoded_message = message_str.encode('utf-8') if isinstance(message_str, str) else message_str

            # Handle headers - convert dict to the format expected by confluent-kafka
            processed_headers = None
            if headers:
                processed_headers = []
                for h_key, h_value in headers.items():
                    if isinstance(h_value, str):
                        processed_headers.append((h_key, h_value.encode('utf-8')))
                    elif h_value is None:
                        processed_headers.append((h_key, None))
                    else:
                        processed_headers.append((h_key, h_value))

            # Produce the message
            self._producer.produce(
                topic=topic,
                value=encoded_message,
                key=key.encode('utf-8') if key else None,
                headers=processed_headers,
                callback=self.delivery_callback
            )

            # Poll for delivery reports to handle errors
            self._producer.poll(0)

        except Exception as e:
            logger.error(f"Failed to produce message to topic {topic}: {str(e)}")
            raise

    def flush(self, timeout: Optional[float] = None) -> int:
        """
        Wait for all messages in the Producer queue to be delivered.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Number of messages remaining in queue
        """
        # confluent-kafka flush doesn't accept None, so use a default value
        flush_timeout = timeout if timeout is not None else 30.0  # Default to 30 seconds
        return self._producer.flush(flush_timeout)

    def delivery_callback(self, err, msg):
        """
        Callback function for message delivery reports.

        Args:
            err: Error object if delivery failed
            msg: Message object if delivery succeeded
        """
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


# Global producer instance
_kafka_producer = None


def get_kafka_producer() -> KafkaProducer:
    """
    Get or create a global Kafka producer instance.

    Returns:
        KafkaProducer instance
    """
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer()
    return _kafka_producer
