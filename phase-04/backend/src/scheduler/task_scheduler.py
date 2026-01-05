"""
Background scheduler for handling recurring tasks and reminders.
This module contains functionality to periodically process recurring tasks
and send reminders at specified times.
"""

import asyncio
import logging
from datetime import datetime, timezone
from sqlmodel import Session, select
from ..database.database import engine
from ..services.task_service import TaskService
from ..models.task import Task


class TaskScheduler:
    """Background scheduler for recurring tasks and reminders."""

    def __init__(self, check_interval: int = 300):  # Default to checking every 5 minutes
        """
        Initialize the task scheduler.

        Args:
            check_interval: Interval in seconds between checks for recurring tasks
        """
        self.check_interval = check_interval
        self.is_running = False
        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Start the background scheduler."""
        self.is_running = True
        self.logger.info("Task scheduler started")

        while self.is_running:
            try:
                await self.process_recurring_tasks()
                await self.process_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in task scheduler: {e}")
                await asyncio.sleep(self.check_interval)  # Continue even if there's an error

        self.logger.info("Task scheduler stopped")

    async def stop(self):
        """Stop the background scheduler."""
        self.is_running = False

    async def process_recurring_tasks(self):
        """Process recurring tasks that need to be scheduled."""
        try:
            # Create a new session for this operation
            with Session(engine) as session:
                processed_count = TaskService.process_recurring_tasks(session)
                if processed_count > 0:
                    self.logger.info(f"Processed {processed_count} recurring tasks")
        except Exception as e:
            self.logger.error(f"Error processing recurring tasks: {e}")

    async def process_reminders(self):
        """Process tasks that need reminders sent."""
        try:
            current_time = datetime.now(timezone.utc)

            # Create a new session for this operation
            with Session(engine) as session:
                # Find tasks with reminder times that are due (not yet sent)
                # We'll use a simple approach: look for tasks where reminder_time is set and <= current time
                # and where we would need to send a reminder (in a real app, we'd track sent reminders)
                from sqlmodel import and_

                # Find tasks with due reminders
                reminder_tasks = session.exec(
                    select(Task).where(
                        and_(
                            Task.reminder_time != None,
                            Task.reminder_time <= current_time,
                            Task.completed == False  # Only send reminders for incomplete tasks
                        )
                    )
                ).all()

                # In a real application, we would send actual notifications here
                # For now, we'll just log that reminders are due
                for task in reminder_tasks:
                    self.logger.info(f"Reminder due for task {task.id}: {task.title}")
                    # Here you would implement the actual notification system
                    # e.g., send email, push notification, etc.

                if reminder_tasks:
                    self.logger.info(f"Processed reminders for {len(reminder_tasks)} tasks")

        except Exception as e:
            self.logger.error(f"Error processing reminders: {e}")

    async def run_once(self):
        """Run the recurring task processing once - useful for testing."""
        await self.process_recurring_tasks()
        await self.process_reminders()


# Global scheduler instance
scheduler = TaskScheduler()


async def start_scheduler():
    """Start the global scheduler."""
    await scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    scheduler.stop()


if __name__ == "__main__":
    # For testing the scheduler directly
    import sys
    import signal

    async def main():
        # Handle graceful shutdown
        def signal_handler():
            print("Shutting down scheduler...")
            scheduler.stop()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

        await start_scheduler()

    # Run the scheduler
    asyncio.run(main())