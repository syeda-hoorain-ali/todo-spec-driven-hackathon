from typing import List, Optional
from sqlmodel import Session, select
from .models import Task, AddTaskRequest, UpdateTaskRequest, ListTasksRequest
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import calendar


def get_user_tasks(session: Session, user_id: str) -> List[Task]:
    """
    Get all tasks for a specific user.

    Args:
        session: Database session
        user_id: ID of the user whose tasks to retrieve

    Returns:
        List of tasks belonging to the user
    """
    statement = select(Task).where(Task.user_id == user_id)
    results = session.exec(statement)
    return list(results.all())


def create_task(session: Session, task_data: AddTaskRequest) -> Task:
    """
    Create a new task in the database.

    Args:
        session: Database session
        task_data: Task data to create

    Returns:
        Created Task object
    """
    # Get current time in UTC
    now_utc = datetime.now(timezone.utc)
    
    # Ensure due_date is timezone-aware if provided
    due_date = task_data.due_date
    if due_date:
        if due_date.tzinfo is None:
            # Make it timezone-aware (assume UTC if no timezone)
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        # Validate that due_date is in the future
        if due_date < now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date must be in the future"
            )
    
    # Ensure reminder_time is timezone-aware if provided
    reminder_time = task_data.reminder_time
    if reminder_time:
        if reminder_time.tzinfo is None:
            # Make it timezone-aware (assume UTC if no timezone)
            reminder_time = reminder_time.replace(tzinfo=timezone.utc)
    
    # Validate that reminder_time is before due_date if both are provided
    if reminder_time and due_date and reminder_time > due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reminder time must be before due date"
        )

    task = Task(**task_data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task_in_db(session: Session, task_id: int, user_id: str, update_data: UpdateTaskRequest) -> Task:
    """
    Update a task in the database.

    Args:
        session: Database session
        task_id: ID of the task to update
        user_id: ID of the user (for validation)
        update_data: Update data

    Returns:
        Updated Task object
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    # Update task fields with provided values
    update_data_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_data_dict.items():
        if hasattr(task, field):
            setattr(task, field, value)

    # Update the updated_at timestamp
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task_from_db(session: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a task from the database.

    Args:
        session: Database session
        task_id: ID of the task to delete
        user_id: ID of the user (for validation)

    Returns:
        True if task was deleted, False if not found
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        return False

    session.delete(task)
    session.commit()
    return True


def complete_task_in_db(session: Session, task_id: int, user_id: str) -> Task:
    """
    Mark a task as complete in the database.

    Args:
        session: Database session
        task_id: ID of the task to complete
        user_id: ID of the user (for validation)

    Returns:
        Updated Task object
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )

    task.completed = True
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Process recurrence if this is a recurring task
    if task.is_recurring:
        process_recurrence_for_task(session, task)

    return task


def list_tasks_filtered(session: Session, list_request: ListTasksRequest) -> List[Task]:
    """
    List and search for tasks with filtering options.
    
    IMPORTANT: Use the 'search' parameter to find tasks by partial title or description match.
    You do NOT need the exact title - the search parameter uses fuzzy matching.
    
    Common use cases:
    - User says "I completed the hackathon" → Use search="hackathon" to find matching tasks
    - User asks "show my reports" → Use search="report" to find matching tasks
    - User says "what tasks are due today" → Use appropriate date filtering
    
    Parameters:
    - user_id: Required user identifier
    - status: Filter by "pending", "completed", or "all"
    - priority: Filter by "low", "medium", or "high"
    - category: Filter by category name
    - search: **USE THIS to find tasks by partial title/description match** (case-insensitive)
    - sort_by: Sort results by "due_date", "priority", "title", or "created_at"
    - sort_order: "asc" or "desc"
    
    Example workflow when user says "I submitted the hackathon":
    1. Call list_tasks(user_id="...", search="hackathon", status="pending")
    2. If found, use update_task to mark as completed
    3. If multiple found, ask user which specific task
    
    Returns:
        List of tasks matching the filters
    """
    
    statement = select(Task).where(Task.user_id == list_request.user_id)

    # Apply status filter
    if list_request.status:
        if list_request.status == "pending":
            statement = statement.where(Task.completed == False)
        elif list_request.status == "completed":
            statement = statement.where(Task.completed == True)

    # Apply priority filter
    if list_request.priority:
        statement = statement.where(Task.priority == list_request.priority)

    # Apply category filter
    if list_request.category:
        statement = statement.where(Task.category == list_request.category)

    # Apply search filter
    if list_request.search:
        search_term = f"%{list_request.search}%"
        statement = statement.where(
            (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
        )

    # Apply sorting
    if list_request.sort_by:
        sort_attribute = getattr(Task, list_request.sort_by)
        if list_request.sort_order == "desc":
            statement = statement.order_by(sort_attribute.desc())
        else:
            statement = statement.order_by(sort_attribute.asc())

    results = session.exec(statement)
    return list(results.all())


def process_recurrence_for_task(session: Session, task: Task) -> Optional[Task]:
    """
    Process recurrence for a completed task by creating the next occurrence if applicable.

    Args:
        session: Database session
        task: The completed task that may have recurrence

    Returns:
        New task instance if created, None if no recurrence or max occurrences reached
    """
    # Check if the task is recurring and was just completed
    if not task.is_recurring or not task.completed:
        return None

    # Check if we've reached the maximum number of occurrences
    if task.max_occurrences:
        # Count how many occurrences of this task already exist
        statement = select(Task).where(
            Task.user_id == task.user_id,
            Task.title == task.title,  # Same title indicates same recurring task
            Task.description == task.description
        )
        existing_occurrences = session.exec(statement).all()
        if len(existing_occurrences) >= task.max_occurrences:
            return None

    # Check if we've passed the recurrence end date
    if task.recurrence_end_date and datetime.now(timezone.utc) > task.recurrence_end_date:
        return None

    # Calculate the next occurrence based on the recurrence pattern
    if not task.recurrence_pattern:
        return None

    # Ensure the base date is timezone-aware for proper calculation
    base_date = task.due_date or task.created_at
    if base_date.tzinfo is None:
        # If the base date is naive, assume it's in UTC
        base_date = base_date.replace(tzinfo=timezone.utc)

    next_due_date = calculate_next_occurrence(
        base_date,
        task.recurrence_pattern,
        task.recurrence_interval or 1
    )

    # Check if the next occurrence is beyond the recurrence end date
    if task.recurrence_end_date and next_due_date > task.recurrence_end_date:
        return None

    # Create a new task with the next occurrence date
    new_task_data = AddTaskRequest(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        completed=False,
        category=task.category,
        priority=task.priority,
        due_date=next_due_date,
        reminder_time=task.reminder_time,
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern,
        recurrence_interval=task.recurrence_interval,
        recurrence_end_date=task.recurrence_end_date,
        max_occurrences=task.max_occurrences
    )

    new_task = create_task(session, new_task_data)
    return new_task


def calculate_next_occurrence(current_date: datetime, pattern: str, interval: int = 1) -> datetime:
    """
    Calculate the next occurrence date based on the recurrence pattern.

    Args:
        current_date: The current occurrence date
        pattern: The recurrence pattern (daily, weekly, monthly, yearly)
        interval: The interval between occurrences (e.g., every 2 weeks)

    Returns:
        The next occurrence date
    """
    if pattern == "daily":
        return current_date + timedelta(days=interval)
    elif pattern == "weekly":
        return current_date + timedelta(weeks=interval)
    elif pattern == "monthly":
        # For monthly recurrence, we need to handle month boundaries carefully
        # This implementation adds the interval in months by calculating days
        # A more sophisticated approach would handle day overflow (e.g., Jan 31 + 1 month)
        current_year = current_date.year
        current_month = current_date.month
        target_month = current_month + interval

        while target_month > 12:
            current_year += 1
            target_month -= 12

        # Handle day overflow (e.g., Jan 31 + 1 month should be Feb 28/29, not Mar 3)
        max_day = calendar.monthrange(current_year, target_month)[1]
        day = min(current_date.day, max_day)

        return current_date.replace(year=current_year, month=target_month, day=day)
    elif pattern == "yearly":
        return current_date.replace(year=current_date.year + interval)
    else:
        # For unknown patterns, default to daily
        return current_date + timedelta(days=interval)
    