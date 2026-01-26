"""
Kafka topic definitions for the Todo Chatbot application.
"""
from enum import Enum


# Task-related topics
TASK_CREATED_TOPIC = "task.created"
TASK_UPDATED_TOPIC = "task.updated"
TASK_DELETED_TOPIC = "task.deleted"

# Notification-related topics
NOTIFICATION_TOPIC = "notifications"
TASK_REMINDER_TOPIC = "task.reminder"

# Audit-related topics
AUDIT_LOG_TOPIC = "audit.log"

# System topics
HEALTH_CHECK_TOPIC = "health.check"
ERROR_TOPIC = "system.errors"

# All defined topics
ALL_KAFKA_TOPICS = [
    TASK_CREATED_TOPIC,
    TASK_UPDATED_TOPIC,
    TASK_DELETED_TOPIC,
    NOTIFICATION_TOPIC,
    TASK_REMINDER_TOPIC,
    AUDIT_LOG_TOPIC,
    HEALTH_CHECK_TOPIC,
    ERROR_TOPIC,
]


class TopicConfig:
    """
    Configuration for Kafka topics.
    """
    @staticmethod
    def get_topic_partitions(topic: str) -> int:
        """
        Get the recommended number of partitions for a given topic.

        Args:
            topic: The topic name

        Returns:
            Recommended number of partitions
        """
        partition_map = {
            TASK_CREATED_TOPIC: 3,
            TASK_UPDATED_TOPIC: 3,
            TASK_DELETED_TOPIC: 3,
            NOTIFICATION_TOPIC: 2,
            TASK_REMINDER_TOPIC: 2,
            AUDIT_LOG_TOPIC: 3,
            HEALTH_CHECK_TOPIC: 1,
            ERROR_TOPIC: 1,
        }
        return partition_map.get(topic, 1)

    @staticmethod
    def get_topic_retention_ms(topic: str) -> int:
        """
        Get the retention period in milliseconds for a given topic.

        Args:
            topic: The topic name

        Returns:
            Retention period in milliseconds
        """
        retention_map = {
            TASK_CREATED_TOPIC: 7 * 24 * 60 * 60 * 1000,  # 7 days
            TASK_UPDATED_TOPIC: 7 * 24 * 60 * 60 * 1000,  # 7 days
            TASK_DELETED_TOPIC: 7 * 24 * 60 * 60 * 1000,  # 7 days
            NOTIFICATION_TOPIC: 24 * 60 * 60 * 1000,      # 1 day
            TASK_REMINDER_TOPIC: 2 * 24 * 60 * 60 * 1000, # 2 days
            AUDIT_LOG_TOPIC: 90 * 24 * 60 * 60 * 1000,   # 90 days (compliance)
            HEALTH_CHECK_TOPIC: 1 * 24 * 60 * 60 * 1000,  # 1 day
            ERROR_TOPIC: 7 * 24 * 60 * 60 * 1000,        # 7 days
        }
        return retention_map.get(topic, 7 * 24 * 60 * 60 * 1000)  # Default to 7 days
