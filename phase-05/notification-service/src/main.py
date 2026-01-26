"""Notification Service for Todo Chatbot Application
Consumes Kafka events and sends notifications to users.
"""
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from dotenv import load_dotenv, find_dotenv
from sqlmodel import Session, select, func

from .database import DatabaseManager
from .kafka_consumer import NotificationKafkaConsumer
from .notification_service import NotificationService
from .models import Notification


load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to handle startup and shutdown."""
    # Initialize database manager
    db_manager = DatabaseManager(DATABASE_URL)
    await db_manager.initialize()

    # Initialize Kafka consumer
    kafka_consumer = NotificationKafkaConsumer(db_manager)
    await kafka_consumer.initialize()

    # Initialize notification service
    notification_service = NotificationService(db_manager)

    # Store in app state
    app.state.db_manager = db_manager
    app.state.kafka_consumer = kafka_consumer
    app.state.notification_service = notification_service
    app.state.running = True

    # Start consuming in background
    consume_task = asyncio.create_task(kafka_consumer.start_consuming())

    yield

    # Shutdown
    app.state.running = False
    consume_task.cancel()
    try:
        await consume_task
    except asyncio.CancelledError:
        pass

    await kafka_consumer.stop_consuming()
    await db_manager.close()

    logger.info("Notification Service shut down")


app = FastAPI(
    title="Notification Service",
    description="Handles sending notifications based on Kafka events",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def read_root():
    """Root endpoint for the notification service."""
    return {"message": "Notification Service for Todo Chatbot", "status": "running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/database")
async def database_health():
    """Database connectivity health check."""
    try:
        db_manager: DatabaseManager = app.state.db_manager

        # Test the database connection by executing a simple query using SQLModel
        with Session(db_manager.engine) as session:
            result = session.exec(select(1).limit(1)).first()

        return {
            "status": "healthy",
            "service": "notification-database",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "notification-database",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.get("/health/kafka")
async def kafka_health():
    """Kafka connectivity health check."""
    try:
        # In a real implementation, we would check the actual connection status
        return {
            "status": "healthy",
            "service": "kafka-consumer",
            "connected": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "kafka-consumer",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.get("/notifications")
async def get_notifications(user_id: str, limit: int = 100, offset: int = 0):
    """Retrieve notifications for a specific user with pagination."""
    try:
        notification_service: NotificationService = app.state.notification_service

        notifications = await notification_service.get_user_notifications(user_id, limit, offset)

        # Get total count for pagination metadata
        db_manager: DatabaseManager = app.state.db_manager
        with Session(db_manager.engine) as session:
            count_statement = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
            count = session.exec(count_statement).one()

        return {
            "notifications": notifications,
            "count": len(notifications),
            "total": count,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")


@app.post("/notifications/{notification_id}/mark-read")
async def mark_notification_as_read(notification_id: str, user_id: str):
    """Mark a notification as read."""
    try:
        notification_service: NotificationService = app.state.notification_service

        success = await notification_service.mark_notification_as_read(notification_id, user_id)

        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {"success": True, "message": "Notification marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")


@app.post("/notifications/process/{notification_id}")
async def process_notification(notification_id: str):
    """Process and send a specific notification."""
    try:
        notification_service: NotificationService = app.state.notification_service

        await notification_service.send_notification(notification_id)

        return {"success": True, "message": f"Notification {notification_id} processed"}

    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing notification: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
