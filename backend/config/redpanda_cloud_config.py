"""
Configuration for Redpanda Cloud connection in production.
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class RedpandaCloudConfig:
    """
    Configuration for connecting to Redpanda Cloud in production.
    """
    # Connection settings
    bootstrap_servers: str = os.getenv("REDPANDA_BOOTSTRAP_SERVERS", "localhost:9092")
    security_protocol: str = os.getenv("REDPANDA_SECURITY_PROTOCOL", "SASL_SSL")
    sasl_mechanism: str = os.getenv("REDPANDA_SASL_MECHANISM", "SCRAM-SHA-256")
    sasl_username: Optional[str] = os.getenv("REDPANDA_SASL_USERNAME")
    sasl_password: Optional[str] = os.getenv("REDPANDA_SASL_PASSWORD")

    # Client settings
    client_id: str = os.getenv("REDPANDA_CLIENT_ID", "todo-chatbot")
    group_id: str = os.getenv("REDPANDA_GROUP_ID", "todo-chatbot-group")

    # Performance settings
    batch_size: int = int(os.getenv("REDPANDA_BATCH_SIZE", "16384"))
    linger_ms: int = int(os.getenv("REDPANDA_LINGER_MS", "5"))
    buffer_memory: int = int(os.getenv("REDPANDA_BUFFER_MEMORY", "33554432"))
    max_in_flight_requests_per_connection: int = int(os.getenv("REDPANDA_MAX_IN_FLIGHT_REQUESTS", "5"))

    # Reliability settings
    acks: str = os.getenv("REDPANDA_ACKS", "all")
    retries: int = int(os.getenv("REDPANDA_RETRIES", "3"))
    enable_idempotence: bool = os.getenv("REDPANDA_ENABLE_IDEMPOTENCE", "true").lower() == "true"

    # Consumer settings
    auto_offset_reset: str = os.getenv("REDPANDA_AUTO_OFFSET_RESET", "latest")
    enable_auto_commit: bool = os.getenv("REDPANDA_ENABLE_AUTO_COMMIT", "true").lower() == "true"
    heartbeat_interval_ms: int = int(os.getenv("REDPANDA_HEARTBEAT_INTERVAL_MS", "3000"))
    session_timeout_ms: int = int(os.getenv("REDPANDA_SESSION_TIMEOUT_MS", "30000"))

    def get_kafka_config(self, client_type: str = "producer") -> dict:
        """
        Get the Kafka configuration dictionary based on the client type.

        Args:
            client_type: Either 'producer' or 'consumer'

        Returns:
            Dictionary with Kafka configuration parameters
        """
        config = {
            "bootstrap.servers": self.bootstrap_servers,
            "security.protocol": self.security_protocol,
            "sasl.mechanism": self.sasl_mechanism,
            "sasl.username": self.sasl_username,
            "sasl.password": self.sasl_password,
            "client.id": self.client_id,
        }

        if client_type == "producer":
            # Producer-specific settings
            config.update({
                "acks": self.acks,
                "retries": self.retries,
                "batch.size": self.batch_size,
                "linger.ms": self.linger_ms,
                "buffer.memory": self.buffer_memory,
                "max.in.flight.requests.per.connection": self.max_in_flight_requests_per_connection,
                "enable.idempotence": self.enable_idempotence,
            })
        elif client_type == "consumer":
            # Consumer-specific settings
            config.update({
                "group.id": self.group_id,
                "auto.offset.reset": self.auto_offset_reset,
                "enable.auto.commit": self.enable_auto_commit,
                "heartbeat.interval.ms": self.heartbeat_interval_ms,
                "session.timeout.ms": self.session_timeout_ms,
            })
        else:
            raise ValueError(f"Invalid client_type: {client_type}. Must be 'producer' or 'consumer'.")

        return config

    def validate(self) -> bool:
        """
        Validate that the configuration has all required values.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.sasl_username:
            raise ValueError("REDPANDA_SASL_USERNAME is required for Redpanda Cloud connection")

        if not self.sasl_password:
            raise ValueError("REDPANDA_SASL_PASSWORD is required for Redpanda Cloud connection")

        if not self.bootstrap_servers:
            raise ValueError("REDPANDA_BOOTSTRAP_SERVERS is required for Redpanda Cloud connection")

        return True


# Global instance of the configuration
redpanda_config = RedpandaCloudConfig()


def get_redpanda_config(client_type: str = "producer") -> dict:
    """
    Get the Redpanda Cloud configuration for the specified client type.

    Args:
        client_type: Either 'producer' or 'consumer'

    Returns:
        Dictionary with Kafka configuration parameters
    """
    return redpanda_config.get_kafka_config(client_type)