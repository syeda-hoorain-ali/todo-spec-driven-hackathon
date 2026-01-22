"""
Sample event types to demonstrate the extensibility pattern.
"""
from typing import Dict, Any
from .event_schemas import BaseEventSchema, BaseModel
from .event_handler import AbstractEventHandler
from .event_registry import register_event
from .topics import ALL_TOPICS


class UserLoggedInPayload(BaseModel):
    """
    Payload schema for user logged in events.
    """
    user_id: str
    session_id: str
    ip_address: str
    timestamp: str


class UserLoggedInEventSchema(BaseEventSchema):
    """
    Schema for user logged in events.
    """
    eventType: str = "user.logged.in"
    source: str = "authentication-service"
    payload: UserLoggedInPayload


@register_event(
    event_type="user.logged.in",
    schema_class=UserLoggedInEventSchema,
    metadata={
        "description": "Fired when a user successfully logs in",
        "version": "1.0.0",
        "category": "authentication"
    }
)
class UserLoggedInEventSchema(BaseEventSchema):
    """
    Schema for user logged in events.
    """
    eventType: str = "user.logged.in"
    source: str = "authentication-service"
    payload: UserLoggedInPayload


class UserLoggedInHandler(AbstractEventHandler):
    """
    Handler for user logged in events.
    """
    def handle(self, message: Dict[str, Any]) -> None:
        """
        Handle a user logged in event.

        Args:
            message: The event message to handle
        """
        event_data = message['value']
        user_id = event_data['payload']['user_id']
        session_id = event_data['payload']['session_id']
        ip_address = event_data['payload']['ip_address']

        print(f"User {user_id} logged in from {ip_address} with session {session_id}")

        # In a real implementation, you might:
        # - Update user activity tracking
        # - Send welcome notifications
        # - Log security events
        # - Update session management
        # - Trigger onboarding flows


class TaskAssignedPayload(BaseModel):
    """
    Payload schema for task assigned events.
    """
    task_id: str
    assignee_user_id: str
    assigned_by_user_id: str
    task_title: str
    timestamp: str


class TaskAssignedEventSchema(BaseEventSchema):
    """
    Schema for task assigned events.
    """
    eventType: str = "task.assigned"
    source: str = "task-management-service"
    payload: TaskAssignedPayload


@register_event(
    event_type="task.assigned",
    schema_class=TaskAssignedEventSchema,
    metadata={
        "description": "Fired when a task is assigned to a user",
        "version": "1.0.0",
        "category": "task-management"
    }
)
class TaskAssignedEventSchema(BaseEventSchema):
    """
    Schema for task assigned events.
    """
    eventType: str = "task.assigned"
    source: str = "task-management-service"
    payload: TaskAssignedPayload


class TaskAssignedHandler(AbstractEventHandler):
    """
    Handler for task assigned events.
    """
    def handle(self, message: Dict[str, Any]) -> None:
        """
        Handle a task assigned event.

        Args:
            message: The event message to handle
        """
        event_data = message['value']
        task_id = event_data['payload']['task_id']
        assignee_user_id = event_data['payload']['assignee_user_id']
        assigned_by_user_id = event_data['payload']['assigned_by_user_id']
        task_title = event_data['payload']['task_title']

        print(f"Task '{task_title}' (ID: {task_id}) assigned to user {assignee_user_id} by {assigned_by_user_id}")

        # In a real implementation, you might:
        # - Send notification to assignee
        # - Update user workload tracking
        # - Trigger assignment workflows
        # - Log assignment metrics


# Sample topic for user events
USER_EVENTS_TOPIC = "user.events"
TASK_EVENTS_TOPIC = "task.events"

# Add to all topics
ALL_TOPICS.extend([USER_EVENTS_TOPIC, TASK_EVENTS_TOPIC])