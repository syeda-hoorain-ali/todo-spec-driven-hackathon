"""
Event schemas for Kafka integration based on data model requirements.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class BaseEventSchema(BaseModel):
    """
    Base schema for all Kafka events.
    """
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    eventType: str
    source: str
    userId: str
    payload: Dict[str, Any]
    headers: Optional[Dict[str, str]] = {}


class TaskCreatedEventPayload(BaseModel):
    """
    Payload schema for task.created events.
    """
    taskId: str
    title: str
    description: Optional[str] = None
    status: str  # pending, completed, archived
    priority: str  # low, medium, high
    dueDate: Optional[str] = None  # ISO 8601 datetime
    tags: List[str] = []
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskCreatedEventSchema(BaseEventSchema):
    """
    Schema for task.created events.
    """
    eventType: str = "task.created"
    source: str = "task-service"
    payload: TaskCreatedEventPayload


class TaskUpdatedEventPayload(BaseModel):
    """
    Payload schema for task.updated events.
    """
    taskId: str
    previousState: Dict[str, Any]
    newState: Dict[str, Any]
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskUpdatedEventSchema(BaseEventSchema):
    """
    Schema for task.updated events.
    """
    eventType: str = "task.updated"
    source: str = "task-service"
    payload: TaskUpdatedEventPayload


class TaskDeletedEventPayload(BaseModel):
    """
    Payload schema for task.deleted events.
    """
    taskId: str
    deletedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskDeletedEventSchema(BaseEventSchema):
    """
    Schema for task.deleted events.
    """
    eventType: str = "task.deleted"
    source: str = "task-service"
    payload: TaskDeletedEventPayload


class TaskCompletedEventPayload(BaseModel):
    """
    Payload schema for task.completed events.
    """
    taskId: str
    completedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completedBy: str


class TaskCompletedEventSchema(BaseEventSchema):
    """
    Schema for task.completed events.
    """
    eventType: str = "task.completed"
    source: str = "task-service"
    payload: TaskCompletedEventPayload


class TaskReminderEventPayload(BaseModel):
    """
    Payload schema for task.reminder events.
    """
    taskId: str
    userId: str
    dueDate: str
    reminderTime: str
    reminderType: str  # email, push, in-app


class TaskReminderEventPayload(BaseModel):
    """
    Payload schema for task.reminder events.
    """
    taskId: str
    userId: str
    dueDate: str
    reminderTime: str
    reminderType: str  # email, push, in-app


class TaskReminderEventSchema(BaseEventSchema):
    """
    Schema for task.reminder events.
    """
    eventType: str = "task.reminder"
    source: str = "reminder-service"
    payload: TaskReminderEventPayload


class AuditLogEventPayload(BaseModel):
    """
    Payload schema for audit log events.
    """
    action: str
    userId: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    resourceType: str
    resourceId: str
    beforeState: Optional[Dict[str, Any]] = None
    afterState: Optional[Dict[str, Any]] = None


class AuditLogEventSchema(BaseEventSchema):
    """
    Schema for audit log events.
    """
    eventType: str  # varies (create, update, delete, etc.)
    source: str = "audit-service"
    payload: AuditLogEventPayload


# Validation functions
def validate_event_id(event_id: str) -> bool:
    """
    Validate that the event ID is a proper UUID.

    Args:
        event_id: The event ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        uuid.UUID(event_id)
        return True
    except ValueError:
        return False


def validate_timestamp(timestamp: str) -> bool:
    """
    Validate that the timestamp is in ISO 8601 format.

    Args:
        timestamp: The timestamp to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that all required fields are present in the data.

    Args:
        data: The data to validate
        required_fields: List of required field names

    Returns:
        True if all required fields are present, False otherwise
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True