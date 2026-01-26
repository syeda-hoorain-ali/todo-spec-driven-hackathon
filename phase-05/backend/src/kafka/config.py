"""
Kafka configuration for the Todo Chatbot application.
"""
from typing import Dict, Any
from ..config.settings import settings


def get_kafka_producer_config() -> Dict[str, Any]:
    """
    Get configuration for Kafka producer.

    Returns:
        Dict[str, Any]: Configuration dictionary for Kafka producer
    """
    config = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'client.id': settings.kafka_client_id,
        'security.protocol': settings.kafka_security_protocol,
        'sasl.mechanism': settings.kafka_sasl_mechanism,
        'acks': 'all',  # Wait for all replicas to acknowledge
        'retries': 3,
        'batch.size': 16384,
        'linger.ms': 5,
        'buffer.memory': 33554432,
        'max.in.flight.requests.per.connection': 5,
        'enable.idempotence': True,  # Exactly-once semantics
    }

    # Add authentication if provided
    if settings.kafka_sasl_username and settings.kafka_sasl_password:
        config.update({
            'sasl.username': settings.kafka_sasl_username,
            'sasl.password': settings.kafka_sasl_password,
        })

    return config


def get_kafka_consumer_config(group_id: str = None) -> Dict[str, Any]:
    """
    Get configuration for Kafka consumer.

    Args:
        group_id: Optional consumer group ID, defaults to settings value

    Returns:
        Dict[str, Any]: Configuration dictionary for Kafka consumer
    """
    config = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'group.id': group_id or settings.kafka_group_id,
        'auto.offset.reset': settings.kafka_auto_offset_reset,
        'enable.auto.commit': settings.kafka_enable_auto_commit,
        'security.protocol': settings.kafka_security_protocol,
        'sasl.mechanism': settings.kafka_sasl_mechanism,
        'session.timeout.ms': 30000,
        'heartbeat.interval.ms': 10000,
        'max.poll.interval.ms': 300000,  # 5 minutes for long processing
        'max.poll.records': 100,
    }

    # Add authentication if provided
    if settings.kafka_sasl_username and settings.kafka_sasl_password:
        config.update({
            'sasl.username': settings.kafka_sasl_username,
            'sasl.password': settings.kafka_sasl_password,
        })

    return config