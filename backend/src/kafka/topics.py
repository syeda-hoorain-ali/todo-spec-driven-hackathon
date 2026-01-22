"""
Topic definitions for the Todo Chatbot Kafka integration.
"""

# Task-related topics
TASK_CREATED_TOPIC = "task.created"
TASK_UPDATED_TOPIC = "task.updated"
TASK_DELETED_TOPIC = "task.deleted"

# Notification-related topics
TASK_REMINDER_TOPIC = "task.reminder"
NOTIFICATION_TOPIC = "notifications"

# Audit-related topics
AUDIT_LOG_TOPIC = "audit.log"

# System topics
HEALTH_CHECK_TOPIC = "health.check"

# All defined topics
ALL_TOPICS = [
    TASK_CREATED_TOPIC,
    TASK_UPDATED_TOPIC,
    TASK_DELETED_TOPIC,
    TASK_REMINDER_TOPIC,
    NOTIFICATION_TOPIC,
    AUDIT_LOG_TOPIC,
    HEALTH_CHECK_TOPIC,
]


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
        TASK_REMINDER_TOPIC: 2,
        NOTIFICATION_TOPIC: 2,
        AUDIT_LOG_TOPIC: 3,
        HEALTH_CHECK_TOPIC: 1,
    }
    return partition_map.get(topic, 1)


def validate_topic_name(topic: str) -> bool:
    """
    Validate that a topic name is properly formatted.

    Args:
        topic: The topic name to validate

    Returns:
        True if valid, False otherwise
    """
    if not topic or not isinstance(topic, str):
        return False

    # Kafka topic naming rules:
    # - Must match [a-zA-Z0-9._-]+
    # - Cannot be "." or ".."
    # - Must be 1-249 characters
    import re
    if len(topic) > 249 or topic in [".", ".."]:
        return False

    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, topic))