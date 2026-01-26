"""
Kafka integration package for the Todo Chatbot application.
"""
from .producer import KafkaProducer, get_kafka_producer
from .config import get_kafka_producer_config, get_kafka_consumer_config
from .topics import (
    TASK_CREATED_TOPIC,
    TASK_UPDATED_TOPIC,
    TASK_DELETED_TOPIC,
    NOTIFICATION_TOPIC,
    TASK_REMINDER_TOPIC,
    AUDIT_LOG_TOPIC
)

__all__ = [
    'KafkaProducer',
    'get_kafka_producer',
    'get_kafka_producer_config',
    'get_kafka_consumer_config',
    'TASK_CREATED_TOPIC',
    'TASK_UPDATED_TOPIC',
    'TASK_DELETED_TOPIC',
    'NOTIFICATION_TOPIC',
    'TASK_REMINDER_TOPIC',
    'AUDIT_LOG_TOPIC'
]
