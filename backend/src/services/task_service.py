import logging
from typing import Optional, Dict, Any
from datetime import datetime
from ..config import settings
from ..kafka.producer import KafkaProducer
from ..kafka.topics import TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC
from ..kafka.event_schemas import TaskCreatedEventSchema, TaskUpdatedEventSchema, TaskCreatedEventPayload
from ..kafka.connection_pool import get_connection_pool


logger = logging.getLogger(__name__)


class TaskService:
    """
    Service for handling task operations with Kafka event publishing.
    """

    def __init__(self):
        """Initialize the task service."""
        self.connection_pool = get_connection_pool()
        logger.info("Task Service initialized with Kafka integration")

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: Optional[list] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Create a new task and publish a task.created event to Kafka.

        Args:
            title: The task title
            description: Optional task description
            status: Task status (default: pending)
            priority: Task priority (default: medium)
            due_date: Optional due date
            tags: Optional list of tags
            user_id: ID of the user creating the task

        Returns:
            Dictionary containing the created task data
        """
        try:
            # Generate a unique task ID
            import uuid
            task_id = str(uuid.uuid4())

            # Create the task data
            task_data = {
                "id": task_id,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "due_date": due_date,
                "tags": tags or [],
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Create the event payload
            event_payload = TaskCreatedEventPayload(
                taskId=task_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                dueDate=due_date,
                tags=tags or [],
                createdAt=task_data["created_at"],
                updatedAt=task_data["updated_at"]
            )

            # Create the event schema
            event = TaskCreatedEventSchema(
                userId=user_id,
                payload=event_payload
            )

            # Publish the event to Kafka using connection pool
            def publish_event():
                with self.connection_pool.get_producer("task-service") as producer:
                    producer.produce(
                        topic=TASK_CREATED_TOPIC,
                        message=event.dict(),
                        key=task_id
                    )
                    producer.flush(timeout=5)  # Wait up to 5 seconds for delivery

            # Execute with retry logic
            self.connection_pool.execute_producer_operation_with_retry(
                publish_event,
                f"publish task.created event for task {task_id}"
            )

            logger.info(f"Task created and event published: {task_id}")

            return task_data

        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[list] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Update a task and publish a task.updated event to Kafka.

        Args:
            task_id: The ID of the task to update
            title: New task title (optional)
            description: New task description (optional)
            status: New task status (optional)
            priority: New task priority (optional)
            due_date: New due date (optional)
            tags: New list of tags (optional)
            user_id: ID of the user updating the task

        Returns:
            Dictionary containing the updated task data
        """
        try:
            # In a real implementation, you would fetch the current task state first
            # For now, we'll simulate an update with dummy previous state
            previous_state = {
                "id": task_id,
                "title": "Previous Title",
                "description": "Previous Description",
                "status": "previous_status",
                "priority": "previous_priority",
                "due_date": "2023-01-01T00:00:00Z",
                "tags": ["previous", "tags"],
                "user_id": user_id,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }

            # Create the updated task data
            updated_task_data = {
                "id": task_id,
                "title": title or previous_state["title"],
                "description": description or previous_state["description"],
                "status": status or previous_state["status"],
                "priority": priority or previous_state["priority"],
                "due_date": due_date or previous_state["due_date"],
                "tags": tags or previous_state["tags"],
                "user_id": user_id,
                "created_at": previous_state["created_at"],
                "updated_at": datetime.utcnow().isoformat()
            }

            # Create the event payload for update
            event_payload = TaskUpdatedEventSchema(
                userId=user_id,
                payload={
                    "taskId": task_id,
                    "previousState": previous_state,
                    "newState": updated_task_data,
                    "updatedAt": updated_task_data["updated_at"]
                }
            )

            # Publish the event to Kafka using connection pool
            def publish_event():
                with self.connection_pool.get_producer("task-service") as producer:
                    producer.produce(
                        topic=TASK_UPDATED_TOPIC,
                        message=event_payload.dict(),
                        key=task_id
                    )
                    producer.flush(timeout=5)  # Wait up to 5 seconds for delivery

            # Execute with retry logic
            self.connection_pool.execute_producer_operation_with_retry(
                publish_event,
                f"publish task.updated event for task {task_id}"
            )

            logger.info(f"Task updated and event published: {task_id}")

            return updated_task_data

        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise


# Global instance of task service
task_service = TaskService()