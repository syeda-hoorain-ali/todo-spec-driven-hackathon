"""
Shared event schemas for Kafka integration across all microservices.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, TypeVar, Generic
from datetime import datetime, timezone
import uuid


class BaseEventPayload(BaseModel):
    """
    Base payload for all events.
    """
    pass

PayloadType = TypeVar('PayloadType', bound=BaseEventPayload)


class BaseEventSchema(BaseModel, Generic[PayloadType]):
    """
    Base schema for all Kafka events.
    """
    eventId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventType: str
    source: str
    userId: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: PayloadType
    headers: Optional[Dict[str, str]] = None


class TaskEventPayload(BaseEventPayload):
    """
    Payload for task-related events.
    """
    taskId: str
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    dueDate: Optional[str] = None
    tags: Optional[list] = None
    userId: str
    createdAt: str
    updatedAt: str


class TaskCreatedEventSchema(BaseEventSchema[TaskEventPayload]):
    """
    Schema for task.created events.
    """
    eventType: str = "task.created"
    source: str = "task-service"
    payload: TaskEventPayload


class TaskUpdatedEventPayload(BaseEventPayload):
    """
    Payload for task.updated events.
    """
    taskId: str
    previousState: Dict[str, Any]
    newState: Dict[str, Any]
    userId: str
    updatedAt: str


class TaskUpdatedEventSchema(BaseEventSchema[TaskUpdatedEventPayload]):
    """
    Schema for task.updated events.
    """
    eventType: str = "task.updated"
    source: str = "task-service"
    payload: TaskUpdatedEventPayload


class TaskDeletedEventPayload(BaseEventPayload):
    """
    Payload for task.deleted events.
    """
    taskId: str
    userId: str
    deletedAt: str


class TaskDeletedEventSchema(BaseEventSchema[TaskDeletedEventPayload]):
    """
    Schema for task.deleted events.
    """
    eventType: str = "task.deleted"
    source: str = "task-service"
    payload: TaskDeletedEventPayload


class NotificationEventPayload(BaseEventPayload):
    """
    Payload for notification events.
    """
    notificationId: str
    userId: str
    notificationType: str
    content: str
    relatedEntityId: Optional[str] = None
    priority: str = "normal"


class NotificationEventSchema(BaseEventSchema[NotificationEventPayload]):
    """
    Schema for notification events.
    """
    eventType: str = "notification.sent"
    source: str = "notification-service"
    payload: NotificationEventPayload


class AuditEventPayload(BaseEventPayload):
    """
    Payload for audit events.
    """
    action: str
    userId: str
    entityType: str
    entityId: str
    timestamp: str
    details: Dict[str, Any]


class AuditEventSchema(BaseEventSchema[AuditEventPayload]):
    """
    Schema for audit events.
    """
    eventType: str = "audit.log"
    source: str = "audit-service"
    payload: AuditEventPayload


class TaskReminderEventPayload(BaseEventPayload):
    """
    Payload for task reminder events.
    """
    taskId: str
    userId: str
    reminderType: str = "in_app"  # in_app, email, push, sms
    message: str = ""
    timestamp: str
    relatedEntityId: Optional[str] = None


class TaskReminderEventSchema(BaseEventSchema[TaskReminderEventPayload]):
    """
    Schema for task reminder events.
    """
    eventType: str = "task.reminder"
    source: str = "reminder-service"
    payload: TaskReminderEventPayload
