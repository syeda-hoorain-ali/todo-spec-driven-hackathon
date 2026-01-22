from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from ...services.task_service import task_service
from ...kafka.producer import KafkaProducer
from ...kafka.topics import TASK_CREATED_TOPIC
from ...kafka.connection_pool import get_connection_pool


router = APIRouter(prefix="/kafka", tags=["kafka"])
logger = logging.getLogger(__name__)


@router.post("/produce/{topic}")
async def produce_message(topic: str, message: Dict[Any, Any]):
    """
    Generic endpoint to produce a message to a Kafka topic.

    Args:
        topic: The topic to publish to
        message: The message to publish

    Returns:
        Success response
    """
    try:
        connection_pool = get_connection_pool()

        def publish_msg():
            with connection_pool.get_producer("api-producer") as producer:
                producer.produce(topic=topic, message=message)
                producer.flush(timeout=5)

        connection_pool.execute_producer_operation_with_retry(
            publish_msg,
            f"produce message to topic {topic}"
        )

        return {"success": True, "topic": topic, "message": message}
    except Exception as e:
        logger.error(f"Error producing message to topic {topic}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/create")
async def create_task_endpoint(
    title: str,
    description: str = None,
    status: str = "pending",
    priority: str = "medium",
    due_date: str = None,
    tags: list = None,
    user_id: str = "anonymous"
):
    """
    Endpoint to create a task and publish a task.created event to Kafka.

    Args:
        title: The task title
        description: Optional task description
        status: Task status (default: pending)
        priority: Task priority (default: medium)
        due_date: Optional due date
        tags: Optional list of tags
        user_id: ID of the user creating the task

    Returns:
        Created task data
    """
    try:
        # Use the task service to create the task and publish the event
        task_data = task_service.create_task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            tags=tags,
            user_id=user_id
        )

        return task_data
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/update/{task_id}")
async def update_task_endpoint(
    task_id: str,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    due_date: str = None,
    tags: list = None,
    user_id: str = "anonymous"
):
    """
    Endpoint to update a task and publish a task.updated event to Kafka.

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
        Updated task data
    """
    try:
        # Use the task service to update the task and publish the event
        task_data = task_service.update_task(
            task_id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            tags=tags,
            user_id=user_id
        )

        return task_data
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def kafka_health_check():
    """
    Health check endpoint for Kafka connectivity.

    Returns:
        Health status
    """
    try:
        # Test Kafka connectivity by attempting to create a producer
        connection_pool = get_connection_pool()

        def test_connection():
            with connection_pool.get_producer("health-test") as producer:
                # Test by checking if producer is available (doesn't actually send message)
                return producer is not None

        result = connection_pool.execute_producer_operation_with_retry(
            test_connection,
            "test Kafka connection"
        )

        if result:
            return {"status": "healthy", "service": "kafka"}
        else:
            return {"status": "unhealthy", "service": "kafka"}

    except Exception as e:
        logger.error(f"Kafka health check failed: {str(e)}")
        return {"status": "unhealthy", "service": "kafka", "error": str(e)}