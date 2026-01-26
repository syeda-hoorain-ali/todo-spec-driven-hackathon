"""
Shared Kafka configuration for all microservices.
"""
from typing import Dict, Any, Optional
import os


def get_kafka_config(service_name: str) -> Dict[str, Any]:
    """
    Get Kafka configuration for a specific service.

    Args:
        service_name: Name of the service requesting config

    Returns:
        Dictionary containing Kafka configuration
    """
    return {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
        'sasl.mechanism': os.getenv('KAFKA_SASL_MECHANISM', ''),
        'sasl.username': os.getenv('KAFKA_SASL_USERNAME', ''),
        'sasl.password': os.getenv('KAFKA_SASL_PASSWORD', ''),
        'client.id': f'{service_name}-{os.getenv("HOSTNAME", "local")}',
        'group.id': f'{service_name}-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'max.poll.interval.ms': 300000,  # 5 minutes for long processing
        'session.timeout.ms': 10000,
        'heartbeat.interval.ms': 3000,
        'request.timeout.ms': 30000,
        'retry.backoff.ms': 1000,
    }


def get_kafka_producer_config(service_name: str) -> Dict[str, Any]:
    """
    Get Kafka producer configuration for a specific service.

    Args:
        service_name: Name of the service requesting config

    Returns:
        Dictionary containing Kafka producer configuration
    """
    base_config = get_kafka_config(service_name)
    producer_config = base_config.copy()
    producer_config.update({
        'acks': 'all',
        'retries': 3,
        'batch.size': 10000,
        'linger.ms': 5,
        'buffer.memory': 33554432,
        'max.in.flight.requests.per.connection': 5,
        'enable.idempotence': True,
    })
    return producer_config


def get_kafka_consumer_config(service_name: str, group_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Kafka consumer configuration for a specific service.

    Args:
        service_name: Name of the service requesting config
        group_id: Optional specific group ID

    Returns:
        Dictionary containing Kafka consumer configuration
    """
    base_config = get_kafka_config(service_name)
    consumer_config = base_config.copy()
    consumer_config.update({
        'group.id': group_id or f'{service_name}-group',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 5000,
        'max.poll.records': 100,
    })
    return consumer_config
