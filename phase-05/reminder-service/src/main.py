"""Reminder Service for Todo Chatbot Application
Manages task reminders and sends reminder events to Kafka.
"""
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List
import os
from dotenv import load_dotenv, find_dotenv
from sqlmodel import Session, select, func
from sqlalchemy import desc
from pydantic import BaseModel

from .database import DatabaseManager
from .reminder_scheduler import ReminderScheduler
from .kafka_consumer import ReminderKafkaConsumer
from .models import Reminder


class ReminderRequest(BaseModel):
    """Request model for scheduling reminders."""
    task_id: str
    user_id: str
    reminder_time: str  # ISO 8601 format
    reminder_type: str = "in_app"  # in_app, email, push, sms
    message: str = ""


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

    # Initialize reminder scheduler
    scheduler = ReminderScheduler(db_manager)
    await scheduler.initialize()

    # Initialize Kafka consumer
    kafka_consumer = ReminderKafkaConsumer(db_manager, scheduler)
    await kafka_consumer.initialize()

    # Store in app state
    app.state.db_manager = db_manager
    app.state.scheduler = scheduler
    app.state.kafka_consumer = kafka_consumer
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
    await scheduler.shutdown()
    await db_manager.close()

    logger.info("Reminder Service shut down")


app = FastAPI(
    title="Reminder Service",
    description="Handles scheduling and sending task reminders via Kafka events",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def read_root():
    """Root endpoint for the reminder service."""
    return {"message": "Reminder Service for Taskflow", "status": "running"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "reminder-service",
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
            "service": "reminder-database",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "reminder-database",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.post("/reminders/schedule")
async def schedule_reminder(reminder_request: ReminderRequest):
    """Schedule a reminder for a task."""
    try:
        scheduler: ReminderScheduler = app.state.scheduler

        job_id = await scheduler.schedule_reminder(
            task_id=reminder_request.task_id,
            user_id=reminder_request.user_id,
            reminder_time=reminder_request.reminder_time,
            reminder_type=reminder_request.reminder_type,
            message=reminder_request.message
        )

        return {
            "status": "scheduled",
            "job_id": job_id,
            "task_id": reminder_request.task_id,
            "scheduled_time": reminder_request.reminder_time
        }

    except Exception as e:
        logger.error(f"Error scheduling reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reminders/bulk-schedule")
async def bulk_schedule_reminders(reminders: List[ReminderRequest]):
    """Schedule multiple reminders at once."""
    results = []
    for reminder in reminders:
        try:
            result = await schedule_reminder(reminder)
            results.append({"status": "success", "reminder": result})
        except Exception as e:
            results.append({"status": "error", "reminder_id": reminder.task_id, "error": str(e)})

    return {"results": results}


@app.delete("/reminders/cancel/{job_id}")
async def cancel_reminder(job_id: str):
    """Cancel a scheduled reminder."""
    try:
        scheduler: ReminderScheduler = app.state.scheduler

        await scheduler.cancel_reminder(job_id)

        return {
            "status": "cancelled",
            "job_id": job_id
        }
    except Exception as e:
        logger.error(f"Error cancelling reminder {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reminders/scheduled")
async def get_scheduled_reminders():
    """Get list of all scheduled reminders."""
    try:
        scheduler: ReminderScheduler = app.state.scheduler

        reminders = await scheduler.get_scheduled_reminders()

        return {
            "scheduled_reminders": reminders,
            "count": len(reminders),
            "total": len(reminders)
        }
    except Exception as e:
        logger.error(f"Error getting scheduled reminders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reminders/task/{task_id}")
async def get_reminders_for_task(task_id: str):
    """Get all reminders for a specific task."""
    try:
        db_manager: DatabaseManager = app.state.db_manager

        with Session(db_manager.engine) as session:
            # Get total count for pagination metadata
            count_statement = select(func.count()).select_from(Reminder).where(Reminder.task_id == task_id)
            count = session.exec(count_statement).one()

            statement = select(Reminder).where(Reminder.task_id == task_id).order_by(desc(Reminder.created_at))
            reminders = session.exec(statement).all()

            reminder_list = []
            for reminder in reminders:
                reminder_list.append({
                    "reminder_id": reminder.reminder_id,
                    "task_id": reminder.task_id,
                    "user_id": reminder.user_id,
                    "reminder_time": reminder.reminder_time,
                    "reminder_type": reminder.reminder_type,
                    "message": reminder.message,
                    "status": reminder.status,
                    "created_at": reminder.created_at
                })

            return {
                "reminders": reminder_list,
                "count": len(reminder_list),
                "total": count
            }
    except Exception as e:
        logger.error(f"Error getting reminders for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )
