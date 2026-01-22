from typing import Dict, Any, Optional
from ..config import settings


def get_kafka_producer_config() -> Dict[str, Any]:
    """
    Get configuration for Kafka producer with SASL/SCRAM authentication.

    Returns:
        Dict[str, Any]: Configuration dictionary for Kafka producer
    """
    config = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'client.id': settings.kafka_client_id,
        'security.protocol': settings.kafka_security_protocol,
        'sasl.mechanism': settings.kafka_sasl_mechanism,
    }

    # Add SASL/SCRAM authentication if provided
    if settings.kafka_sasl_username and settings.kafka_sasl_password:
        config.update({
            'sasl.username': settings.kafka_sasl_username,
            'sasl.password': settings.kafka_sasl_password,
        })

    # Additional security configurations for production
    config.update({
        # Enable SSL endpoint identification
        'ssl.endpoint.identification.algorithm': 'https',
        # Configure retries for authentication failures
        'retries': 3,
        # Batch size for efficient throughput
        'batch.size': 16384,
        # Delay to batch messages
        'linger.ms': 5,
        # Buffer memory
        'buffer.memory': 33554432,
        # Acknowledgment level for reliability
        'acks': 'all',
        # Enable idempotence for exactly-once semantics
        'enable.idempotence': True,
        # Maximum inflight requests per connection
        'max.in.flight.requests.per.connection': 5,
    })

    return config


def get_kafka_consumer_config(group_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for Kafka consumer with SASL/SCRAM authentication.

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
    }

    # Add SASL/SCRAM authentication if provided
    if settings.kafka_sasl_username and settings.kafka_sasl_password:
        config.update({
            'sasl.username': settings.kafka_sasl_username,
            'sasl.password': settings.kafka_sasl_password,
        })

    # Additional consumer-specific configurations
    config.update({
        # Enable SSL endpoint identification
        'ssl.endpoint.identification.algorithm': 'https',
        # Session timeout for consumer group management
        'session.timeout.ms': 30000,
        # Heartbeat interval for consumer group management
        'heartbeat.interval.ms': 10000,
        # Max poll interval to handle long processing
        'max.poll.interval.ms': 300000,
        # Max poll records to control batch processing
        'max.poll.records': 100,
        # Enable auto commit
        'enable.auto.commit': True,
        # Auto commit interval
        'auto.commit.interval.ms': 5000,
        # Partition assignment strategy
        'partition.assignment.strategy': 'range',
        # Fetch min bytes to wait for data
        'fetch.min.bytes': 1024,
        # Fetch max wait time
        'fetch.max.wait.ms': 500,
        # Rebalance timeout
        'rebalance.timeout.ms': 60000,
    })

    return config


def get_kafka_admin_config() -> Dict[str, Any]:
    """
    Get configuration for Kafka admin client with SASL/SCRAM authentication.

    Returns:
        Dict[str, Any]: Configuration dictionary for Kafka admin client
    """
    config = {
        'bootstrap.servers': settings.kafka_bootstrap_servers,
        'security.protocol': settings.kafka_security_protocol,
        'sasl.mechanism': settings.kafka_sasl_mechanism,
    }

    # Add SASL/SCRAM authentication if provided
    if settings.kafka_sasl_username and settings.kafka_sasl_password:
        config.update({
            'sasl.username': settings.kafka_sasl_username,
            'sasl.password': settings.kafka_sasl_password,
        })

    # Additional admin-specific configurations
    config.update({
        # Enable SSL endpoint identification
        'ssl.endpoint.identification.algorithm': 'https',
        # Request timeout
        'request.timeout.ms': 30000,
        # Connection max idle time
        'connections.max.idle.ms': 540000,
    })

    return config