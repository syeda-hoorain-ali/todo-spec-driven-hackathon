import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from ..kafka.producer import KafkaProducer
from ..kafka.topics import TASK_REMINDER_TOPIC
from ..kafka.event_schemas import TaskReminderEventSchema, TaskReminderEventPayload
from ..kafka.connection_pool import get_connection_pool


logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Service for scheduling and sending reminder notifications.
    """

    def __init__(self):
        """Initialize the reminder scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.connection_pool = get_connection_pool()
        self.scheduler.start()
        logger.info("Reminder Scheduler initialized")

    def schedule_reminder(
        self,
        task_id: str,
        user_id: str,
        due_date: str,
        reminder_time: str,
        reminder_types: list = ["email", "push", "in-app"]
    ) -> str:
        """
        Schedule a reminder for a task.

        Args:
            task_id: The ID of the task
            user_id: The ID of the user who owns the task
            due_date: The due date of the task (ISO 8601 format)
            reminder_time: When to send the reminder (ISO 8601 format)
            reminder_types: List of reminder types to send

        Returns:
            Job ID of the scheduled reminder
        """
        try:
            # Parse the reminder time
            reminder_datetime = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))

            # Create the job
            job = self.scheduler.add_job(
                func=self._send_reminder,
                trigger=DateTrigger(run_date=reminder_datetime),
                id=f"reminder_{task_id}_{reminder_time}",
                kwargs={
                    'task_id': task_id,
                    'user_id': user_id,
                    'due_date': due_date,
                    'reminder_time': reminder_time,
                    'reminder_types': reminder_types
                }
            )

            logger.info(f"Scheduled reminder for task {task_id} at {reminder_time}")

            return job.id

        except Exception as e:
            logger.error(f"Failed to schedule reminder for task {task_id}: {str(e)}")
            raise

    def cancel_reminder(self, job_id: str):
        """
        Cancel a scheduled reminder.

        Args:
            job_id: The ID of the scheduled job to cancel
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Cancelled reminder job {job_id}")
        except Exception as e:
            logger.error(f"Failed to cancel reminder job {job_id}: {str(e)}")
            raise

    async def _send_reminder(
        self,
        task_id: str,
        user_id: str,
        due_date: str,
        reminder_time: str,
        reminder_types: list
    ):
        """
        Internal method to send the reminder by publishing a Kafka event.

        Args:
            task_id: The ID of the task
            user_id: The ID of the user who owns the task
            due_date: The due date of the task
            reminder_time: When the reminder is being sent
            reminder_types: List of reminder types to send
        """
        try:
            # Create the reminder event payload
            event_payload = TaskReminderEventPayload(
                taskId=task_id,
                userId=user_id,
                dueDate=due_date,
                reminderTime=reminder_time,
                reminderType=",".join(reminder_types)
            )

            # Create the event schema
            event = TaskReminderEventSchema(
                userId=user_id,
                payload=event_payload
            )

            # Publish the event to Kafka using connection pool
            def publish_reminder_event():
                with self.connection_pool.get_producer("reminder-service") as producer:
                    producer.produce(
                        topic=TASK_REMINDER_TOPIC,
                        message=event.dict(),
                        key=task_id
                    )
                    producer.flush(timeout=5)  # Wait up to 5 seconds for delivery

            # Execute with retry logic
            self.connection_pool.execute_producer_operation_with_retry(
                publish_reminder_event,
                f"publish task.reminder event for task {task_id}"
            )

            logger.info(f"Reminder event published for task {task_id}")

        except Exception as e:
            logger.error(f"Failed to send reminder for task {task_id}: {str(e)}")
            raise

    def get_upcoming_reminders(self) -> list:
        """
        Get a list of upcoming reminders.

        Returns:
            List of upcoming reminder jobs
        """
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'next_run_time': job.next_run_time,
                'task_id': job.kwargs.get('task_id'),
                'user_id': job.kwargs.get('user_id'),
                'due_date': job.kwargs.get('due_date'),
                'reminder_time': job.kwargs.get('reminder_time')
            }
            for job in jobs
        ]

    def shutdown(self):
        """Shut down the scheduler."""
        self.scheduler.shutdown()


# Global instance of reminder scheduler
reminder_scheduler = ReminderScheduler()