"""
Kafka API routes for the Todo Chatbot application.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Path, status
from typing import Dict, Any, Generator
import logging
from sqlmodel import Session

from src.services.task_service import TaskService
from src.database.database import engine
from src.auth.middleware import JWTBearer
from src.kafka.producer import get_kafka_producer
from src.kafka.topics import TASK_CREATED_TOPIC, TASK_UPDATED_TOPIC, TASK_DELETED_TOPIC
from src.kafka.event_schemas import TaskCreatedEventSchema, TaskUpdatedEventSchema, TaskDeletedEventSchema


router = APIRouter(prefix="/kafka", tags=["kafka"])
logger = logging.getLogger(__name__)
security = JWTBearer()

def get_session_with_user_context(token: str = Depends(security)) -> Generator[Session, None, None]:
    """Dependency that provides a database session."""
    from ...auth.jwt import get_user_id_from_token

    # Extract user_id from token for validation in individual endpoints
    token_user_id = get_user_id_from_token(token)
    if not token_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Create and yield the session
    with Session(engine) as session:
        yield session


@router.get("/health")
async def kafka_health_check():
    """
    Health check for Kafka connectivity.
    """
    try:
        # Try to get a producer instance to verify connectivity
        producer = get_kafka_producer()

        # In a real implementation, we might try to send a test message
        # For now, just verify we can get a producer instance
        return {
            "status": "healthy",
            "service": "kafka-connectivity",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Kafka health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Kafka connection unhealthy: {str(e)}")


@router.get("/health/producer")
async def kafka_producer_health():
    """
    Health check specifically for Kafka producer.
    """
    try:
        producer = get_kafka_producer()

        # Verify producer is working by checking its status
        # In a real implementation, we might try a dry run of producing a message
        return {
            "status": "healthy",
            "service": "kafka-producer",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Kafka producer health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Kafka producer unhealthy: {str(e)}")


@router.post("/test-event")
async def send_test_event(event_type: str, payload: Dict[str, Any]):
    """
    Send a test event to Kafka for testing purposes.
    """
    try:
        producer = get_kafka_producer()

        # Create a test event based on the event_type
        import uuid
        test_event = {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "source": "test-endpoint",
            "userId": "test-user",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "headers": {
                "test": "true"
            }
        }

        # Send to an appropriate topic based on event type
        if "task" in event_type.lower():
            if "created" in event_type.lower():
                topic = TASK_CREATED_TOPIC
            elif "updated" in event_type.lower():
                topic = TASK_UPDATED_TOPIC
            elif "deleted" in event_type.lower():
                topic = TASK_DELETED_TOPIC
            else:
                topic = TASK_CREATED_TOPIC  # Default to created topic
        else:
            topic = "test.events"  # Default test topic

        producer.produce(
            topic=topic,
            message=test_event,
            key=str(test_event["eventId"])
        )

        # Flush to ensure delivery
        producer.flush(timeout=5)

        return {
            "status": "sent",
            "event_id": test_event["eventId"],
            "event_type": event_type,
            "topic": topic
        }

    except Exception as e:
        logger.error(f"Failed to send test event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test event: {str(e)}")


# Integrate with existing task operations
task_service = TaskService()


@router.post("/tasks/{task_id}/trigger-event")
async def trigger_task_event(
    task_id: int = Path(..., description="The task ID"),
    event_type: str = "task.updated",
    token: str = Depends(security),
    session: Session = Depends(get_session_with_user_context)
):
    """
    Trigger a specific task-related event based on task data.
    This endpoint is useful for replaying events or triggering specific workflows.
    """
    try:
        # Get user_id from token
        from ...auth.jwt import get_user_id_from_token
        user_id = get_user_id_from_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get the task from the database using the TaskService
        task_service = TaskService()

        # Retrieve the actual task from the database
        # This will only succeed if the user has permission to access this task
        task = task_service.get_task_by_id(task_id, user_id, session)

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found or you don't have permission to access it"
            )

        # Convert the task to a dictionary format suitable for event payload
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": "completed" if task.completed else "pending",
            "priority": getattr(task, 'priority', 'medium'),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "tags": getattr(task, 'tags', []),
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }

        # Create appropriate event based on event_type
        from ...kafka.producer import get_kafka_producer
        producer = get_kafka_producer()

        if event_type == "task.created":
            from ...kafka.event_schemas import TaskEventPayload

            event_payload_obj = TaskEventPayload(
                taskId=str(task_id),
                title=task_data["title"],
                description=task_data["description"],
                status=task_data["status"],
                priority=task_data["priority"],
                dueDate=task_data["due_date"],
                tags=task_data["tags"],
                userId=task_data["user_id"],
                createdAt=task_data["created_at"],
                updatedAt=task_data["updated_at"]
            )

            event = TaskCreatedEventSchema(
                userId=task_data["user_id"],
                payload=event_payload_obj
            )

            topic = TASK_CREATED_TOPIC

        elif event_type == "task.updated":
            from ...kafka.event_schemas import TaskUpdatedEventPayload

            event_payload_obj = TaskUpdatedEventPayload(
                taskId=str(task_id),
                previousState={"status": task_data["status"]},  # Use actual status as previous
                newState={"status": "completed" if not task.completed else "pending"},  # Toggle status as example
                userId=task_data["user_id"],
                updatedAt=task_data["updated_at"]
            )

            event = TaskUpdatedEventSchema(
                userId=task_data["user_id"],
                payload=event_payload_obj
            )

            topic = TASK_UPDATED_TOPIC

        elif event_type == "task.deleted":
            from ...kafka.event_schemas import TaskDeletedEventPayload

            event_payload_obj = TaskDeletedEventPayload(
                taskId=str(task_id),
                userId=task_data["user_id"],
                deletedAt=task_data["updated_at"]
            )

            event = TaskDeletedEventSchema(
                userId=task_data["user_id"],
                payload=event_payload_obj
            )

            topic = TASK_DELETED_TOPIC

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported event type: {event_type}")

        # Publish the event
        producer.produce(
            topic=topic,
            message=event.model_dump(),
            key=str(task_id)
        )

        producer.flush(timeout=5)

        return {
            "status": "event_published",
            "event_type": event_type,
            "task_id": task_id,
            "topic": topic,
            "message": f"{event_type.replace('.', ' ').title()} event published for task {task_id}"
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to trigger task event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger task event: {str(e)}")


@router.get("/metrics")
async def get_kafka_metrics():
    """
    Get Kafka-related metrics in Prometheus format.
    """
    try:
        # In a real implementation, we would collect actual metrics
        # For now, returning a placeholder response
        from prometheus_client import generate_latest, CollectorRegistry
        from ...monitoring.metrics import kafka_events_total, kafka_producer_errors_total, kafka_consumer_errors_total, dlq_events_total

        # Generate metrics in Prometheus format
        registry = CollectorRegistry()
        registry.register(kafka_events_total)
        registry.register(kafka_producer_errors_total)
        registry.register(kafka_consumer_errors_total)
        registry.register(dlq_events_total)

        metrics_data = generate_latest(registry)
        return metrics_data.decode('utf-8')

    except Exception as e:
        logger.error(f"Failed to retrieve Kafka metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Kafka metrics: {str(e)}")
