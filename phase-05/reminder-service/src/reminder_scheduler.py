"""Module for handling reminder scheduling and management."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy import desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from kafka import KafkaProducer

from .database import DatabaseManager
from .models import Reminder
from ...kafka_common.config import get_kafka_producer_config
from ...kafka_common.event_schemas import TaskReminderEventSchema, TaskReminderEventPayload


logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Manages scheduling and cancellation of reminders."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.scheduler = AsyncIOScheduler()
        self.producer: Optional[KafkaProducer] = None

    async def initialize(self):
        """Initialize the reminder scheduler and Kafka producer."""
        self.scheduler.start()

        # Initialize Kafka producer
        producer_config = get_kafka_producer_config("reminder-service")
        self.producer = KafkaProducer(**producer_config)

        logger.info("Reminder scheduler initialized")

    async def shutdown(self):
        """Shutdown the scheduler and close Kafka producer."""
        self.scheduler.shutdown()
        if self.producer:
            self.producer.flush()
            self.producer.close()

    async def schedule_reminder(self, task_id: str, user_id: str, reminder_time: str, reminder_type: str = "in_app", message: str = "") -> str:
        """Schedule a reminder for a specific time."""
        try:
            # Parse the reminder time
            parsed_reminder_time = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))

            # Create a unique job ID for this reminder
            job_id = f"reminder-{task_id}-{uuid.uuid4()}"

            # Schedule the reminder
            self.scheduler.add_job(
                self._trigger_reminder,
                DateTrigger(run_date=parsed_reminder_time),
                id=job_id,
                kwargs={
                    'task_id': task_id,
                    'user_id': user_id,
                    'reminder_type': reminder_type,
                    'message': message
                }
            )

            # Save reminder to database
            reminder = Reminder(
                reminder_id=job_id,
                task_id=task_id,
                user_id=user_id,
                reminder_time=reminder_time,
                reminder_type=reminder_type,
                message=message or f"Reminder for task {task_id}",
                status="scheduled",
                created_at=datetime.now(timezone.utc).isoformat(),
                scheduled_job_id=job_id
            )

            with Session(self.db_manager.engine) as session:
                session.add(reminder)
                session.commit()

            logger.info(f"Scheduled reminder for task {task_id} at {reminder_time}")

            return job_id
        except Exception as e:
            logger.error(f"Error scheduling reminder: {str(e)}")
            raise

    async def _trigger_reminder(self, task_id: str, user_id: str, reminder_type: str, message: str):
        """Function that gets called when a reminder is triggered."""
        try:
            # Create reminder event payload
            reminder_payload = TaskReminderEventPayload(
                taskId=task_id,
                userId=user_id,
                reminderType=reminder_type,
                message=message,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

            # Create the full event
            reminder_event = TaskReminderEventSchema(
                eventId=f"reminder-{task_id}-{uuid.uuid4()}",
                eventType="task.reminder",
                source="reminder-service",
                userId=user_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                payload=reminder_payload
            )

            # Send the event to Kafka
            if self.producer:
                self.producer.send('reminder.events', value=reminder_event.json().encode('utf-8'))

            # Update reminder status to sent
            await self._update_reminder_status(task_id, "sent")

            logger.info(f"Reminder event sent for task {task_id}")

        except Exception as e:
            logger.error(f"Error sending reminder event: {str(e)}")
            # Update reminder status to failed
            await self._update_reminder_status(task_id, "failed")

    async def _update_reminder_status(self, task_id: str, status: str):
        """Update the status of a reminder in the database."""
        try:
            with Session(self.db_manager.engine) as session:
                statement = select(Reminder).where(Reminder.task_id == task_id).order_by(desc(Reminder.created_at))
                reminder = session.exec(statement).first()

                if reminder:
                    reminder.status = status
                    session.add(reminder)
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating reminder status for task {task_id}: {str(e)}")

    async def cancel_reminder(self, job_id: str):
        """Cancel a scheduled reminder."""
        try:
            # Remove from scheduler
            self.scheduler.remove_job(job_id)

            # Update reminder status in database
            with Session(self.db_manager.engine) as session:
                statement = select(Reminder).where(Reminder.scheduled_job_id == job_id)
                reminder = session.exec(statement).first()

                if reminder:
                    reminder.status = "cancelled"
                    session.add(reminder)
                    session.commit()

            logger.info(f"Cancelled reminder with job ID: {job_id}")
        except Exception as e:
            logger.error(f"Error cancelling reminder {job_id}: {str(e)}")
            raise

    async def get_scheduled_reminders(self):
        """Get list of all scheduled reminders."""
        try:
            with Session(self.db_manager.engine) as session:
                statement = select(Reminder).where(Reminder.status == "scheduled").order_by(desc(Reminder.created_at))
                reminders = session.exec(statement).all()

                result = []
                for reminder in reminders:
                    # Get next run time from scheduler
                    job = self.scheduler.get_job(reminder.scheduled_job_id)
                    next_run_time = job.next_run_time.isoformat() if job and job.next_run_time else None

                    result.append({
                        "reminder_id": reminder.reminder_id,
                        "task_id": reminder.task_id,
                        "user_id": reminder.user_id,
                        "reminder_time": reminder.reminder_time,
                        "reminder_type": reminder.reminder_type,
                        "message": reminder.message,
                        "status": reminder.status,
                        "created_at": reminder.created_at,
                        "next_run_time": next_run_time
                    })

                return result
        except Exception as e:
            logger.error(f"Error getting scheduled reminders: {str(e)}")
            raise

    async def adjust_reminders_for_task(self, task_id: str, new_due_date: str):
        """Adjust scheduled reminders when a task's due date changes."""
        # In a real implementation, this would update scheduled jobs in the scheduler
        logger.info(f"Adjusting reminders for task {task_id} with new due date: {new_due_date}")

        # This would involve:
        # 1. Finding all scheduled reminders for this task
        # 2. Calculating new reminder times based on the new due date
        # 3. Cancelling old reminders and scheduling new ones
        # For now, we'll just log that this should happen

    async def cancel_reminders_for_task(self, task_id: str):
        """Cancel all scheduled reminders for a task."""
        try:
            # Find all scheduled reminders for this task
            with Session(self.db_manager.engine) as session:
                statement = select(Reminder).where(
                    Reminder.task_id == task_id,
                    Reminder.status == "scheduled"
                )
                reminders = session.exec(statement).all()

                # Cancel each reminder
                for reminder in reminders:
                    if reminder.scheduled_job_id:
                        self.scheduler.remove_job(reminder.scheduled_job_id)

                    # Update status in database
                    reminder.status = "cancelled"
                    session.add(reminder)

                session.commit()

            logger.info(f"Cancelled all reminders for task {task_id}")
        except Exception as e:
            logger.error(f"Error cancelling reminders for task {task_id}: {str(e)}")
