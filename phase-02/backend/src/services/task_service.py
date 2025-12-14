from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone
from ..models.task import Task, TaskCreate, TaskUpdate
from ..utils.exceptions import InvalidRecurrencePatternException, InvalidReminderTimeException, ValidationError


class TaskService:
    """Service class to handle task-related business logic."""

    @staticmethod
    def create_task(user_id: str, task_data: TaskCreate, session: Session) -> Task:
        """Create a new task for the specified user."""

        # Validate due date and reminder time
        TaskService._validate_due_date_and_reminder(task_data.due_date, task_data.reminder_time)

        # Create a new Task instance with the provided data
        task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=getattr(task_data, 'completed', False),  # Default to not completed
            user_id=user_id,
            due_date=getattr(task_data, 'due_date', None),
            reminder_time=getattr(task_data, 'reminder_time', None),
            is_recurring=getattr(task_data, 'is_recurring', False),
            recurrence_pattern=getattr(task_data, 'recurrence_pattern', None),
            recurrence_interval=getattr(task_data, 'recurrence_interval', None),
            next_occurrence=getattr(task_data, 'next_occurrence', None),
            end_date=getattr(task_data, 'end_date', None),
            max_occurrences=getattr(task_data, 'max_occurrences', None),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Add the task to the session and commit
        session.add(task)
        session.commit()
        session.refresh(task)  # Refresh to get the generated ID and timestamps

        return task

    @staticmethod
    def _validate_due_date_and_reminder(due_date: Optional[datetime], reminder_time: Optional[datetime]):
        """Validate due date and reminder time."""
        if due_date and reminder_time:
            if reminder_time > due_date:
                raise InvalidReminderTimeException()

        # Additional validation can be added here as needed
        # For example, ensuring dates are not in the past for certain types of tasks

    @staticmethod
    def create_recurring_task(user_id: str, task_data: TaskCreate, session: Session) -> Task:
        """Create a new recurring task for the specified user."""
        if not task_data.is_recurring:
            raise ValueError("Task must be marked as recurring")

        # Validate due date and reminder time
        TaskService._validate_due_date_and_reminder(task_data.due_date, task_data.reminder_time)

        # Validate recurrence fields
        if not task_data.recurrence_pattern:
            raise InvalidRecurrencePatternException("Pattern not provided")

        if task_data.recurrence_pattern not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise InvalidRecurrencePatternException(task_data.recurrence_pattern)

        if task_data.recurrence_interval is not None and task_data.recurrence_interval <= 0:
            raise ValidationError("Recurrence interval must be greater than 0")

        # Calculate next occurrence if not provided
        if not task_data.next_occurrence and task_data.recurrence_pattern:
            task_data.next_occurrence = TaskService._calculate_next_occurrence(
                datetime.now(timezone.utc),
                task_data.recurrence_pattern,
                task_data.recurrence_interval or 1
            )

        # Create the recurring task
        task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=getattr(task_data, 'completed', False),
            user_id=user_id,
            due_date=getattr(task_data, 'due_date', None),
            reminder_time=getattr(task_data, 'reminder_time', None),
            is_recurring=True,
            recurrence_pattern=task_data.recurrence_pattern,
            recurrence_interval=task_data.recurrence_interval or 1,
            next_occurrence=task_data.next_occurrence,
            end_date=task_data.end_date,
            max_occurrences=task_data.max_occurrences,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Add the task to the session and commit
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def _calculate_next_occurrence(current_date: datetime, pattern: str, interval: int) -> datetime:
        """Calculate the next occurrence date based on the recurrence pattern."""
        from datetime import timedelta
        if pattern == 'daily':
            return current_date + timedelta(days=interval)
        elif pattern == 'weekly':
            return current_date + timedelta(weeks=interval)
        elif pattern == 'monthly':
            # For monthly, we add months (not just days)
            # This is a simplified approach - in production, we'd handle month boundaries properly
            try:
                next_month = current_date.month + interval
                next_year = current_date.year
                if next_month > 12:
                    next_year += (next_month - 1) // 12
                    next_month = ((next_month - 1) % 12) + 1
                return current_date.replace(year=next_year, month=next_month)
            except ValueError:
                # Handle cases like Jan 31 -> Feb 31 (doesn't exist)
                # In this case, go to the last day of the target month
                target_month = current_date.month + interval
                target_year = current_date.year
                if target_month > 12:
                    target_year += (target_month - 1) // 12
                    target_month = ((target_month - 1) % 12) + 1

                # Find last day of target month
                import calendar
                max_day = calendar.monthrange(target_year, target_month)[1]
                day = min(current_date.day, max_day)
                return current_date.replace(year=target_year, month=target_month, day=day)
        elif pattern == 'yearly':
            return current_date.replace(year=current_date.year + interval)
        else:
            # Default to the same date
            return current_date

    @staticmethod
    def process_recurring_tasks(session: Session) -> int:
        """Process recurring tasks and create new instances when needed."""
        from sqlmodel import and_
        import calendar
        from datetime import datetime, timezone

        current_time = datetime.now(timezone.utc)
        processed_count = 0

        # Find all recurring tasks that should create a new occurrence
        recurring_tasks = session.exec(
            select(Task).where(
                and_(
                    Task.is_recurring == True,
                    Task.next_occurrence != None,
                    Task.next_occurrence <= current_time,
                    Task.completed == False  # Only process incomplete recurring tasks
                )
            )
        ).all()

        for task in recurring_tasks:
            # Check if the recurrence should continue
            should_continue = True

            # Check end date constraint
            if task.end_date and current_time > task.end_date:
                should_continue = False

            # Check max occurrences constraint
            if task.max_occurrences:
                # Count how many tasks with the same title pattern exist for this user
                # In a real system, we'd have a parent_id to track occurrences of the same recurring task
                # For simplicity, we'll just check if we've reached max occurrences
                # This is a simplified approach - a production system would need better tracking
                pass

            if should_continue:
                # Create a new occurrence of the task
                new_task = Task(
                    title=task.title,
                    description=task.description,
                    completed=False,
                    user_id=task.user_id,
                    is_recurring=task.is_recurring,
                    recurrence_pattern=task.recurrence_pattern,
                    recurrence_interval=task.recurrence_interval,
                    end_date=task.end_date,
                    max_occurrences=task.max_occurrences,
                    created_at=current_time,
                    updated_at=current_time
                )

                # Calculate the next occurrence
                if task.recurrence_pattern and task.recurrence_interval:
                    new_task.next_occurrence = TaskService._calculate_next_occurrence(
                        current_time,
                        task.recurrence_pattern,
                        task.recurrence_interval
                    )
                else:
                    new_task.next_occurrence = None  # Disable further recurrence if no pattern

                session.add(new_task)
                processed_count += 1

        # Update the next_occurrence for the original tasks that should continue
        for task in recurring_tasks:
            if task.next_occurrence and task.recurrence_pattern and task.recurrence_interval:
                task.next_occurrence = TaskService._calculate_next_occurrence(
                    current_time,
                    task.recurrence_pattern,
                    task.recurrence_interval
                )
                task.updated_at = current_time
                session.add(task)

        session.commit()
        return processed_count

    @staticmethod
    def get_task_by_id(task_id: int, user_id: str, session: Session) -> Optional[Task]:
        """Get a specific task by ID for the specified user."""
        # Ensure the task belongs to the user
        task = session.get(Task, task_id)
        if task and task.user_id == user_id:
            return task
        return None

    @staticmethod
    def get_tasks_by_user(user_id: str, session: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for the specified user."""
        statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
        tasks = session.exec(statement).all()
        return tasks

    @staticmethod
    def update_task(task_id: int, user_id: str, task_data: TaskUpdate, session: Session) -> Optional[Task]:
        """Update an existing task for the specified user."""
        # Get the existing task
        task = session.get(Task, task_id)

        # Check if the task exists and belongs to the user
        if not task or task.user_id != user_id:
            return None

        # Validate due date and reminder time if provided
        due_date = getattr(task_data, 'due_date', None)
        reminder_time = getattr(task_data, 'reminder_time', None)

        # Use existing values if not provided in update
        if due_date is None:
            due_date = task.due_date
        if reminder_time is None:
            reminder_time = task.reminder_time

        TaskService._validate_due_date_and_reminder(due_date, reminder_time)

        # Update the task with the provided data
        task_update_data = task_data.model_dump(exclude_unset=True)
        for field, value in task_update_data.items():
            setattr(task, field, value)

        # Update the updated_at timestamp
        task.updated_at = datetime.now(timezone.utc)

        # Commit the changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def delete_task(task_id: int, user_id: str, session: Session) -> bool:
        """Delete a task for the specified user."""
        # Get the existing task
        task = session.get(Task, task_id)

        # Check if the task exists and belongs to the user
        if not task or task.user_id != user_id:
            return False

        # Delete the task
        session.delete(task)
        session.commit()

        return True

    @staticmethod
    def toggle_task_completion(task_id: int, user_id: str, session: Session) -> Optional[Task]:
        """Toggle the completion status of a task for the specified user."""
        # Get the existing task
        task = session.get(Task, task_id)

        # Check if the task exists and belongs to the user
        if not task or task.user_id != user_id:
            return None

        # Toggle the completion status
        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        # Commit the changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    @staticmethod
    def search_tasks(user_id: str, keyword: Optional[str], completed: Optional[bool],
                     date_from: Optional[datetime],
                     date_to: Optional[datetime], session: Session) -> List[Task]:
        """Search and filter tasks for the specified user."""
        statement = select(Task).where(Task.user_id == user_id)

        if keyword:
            statement = statement.where(
                (Task.title.contains(keyword)) |
                (Task.description.contains(keyword))
            )

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if date_from:
            statement = statement.where(Task.created_at >= date_from)

        if date_to:
            statement = statement.where(Task.created_at <= date_to)

        tasks = session.exec(statement).all()
        return tasks