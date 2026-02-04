import pytest
import sys
import os
from datetime import datetime, timedelta, timezone
from sqlmodel import select

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mcp_server.models import Task, AddTaskRequest, ListTasksRequest, UpdateTaskRequest
from src.mcp_server.tools import calculate_next_occurrence, create_task, list_tasks_filtered, complete_task_in_db, delete_task_from_db, update_task_in_db


def test_create_task(session):
    """Test creating a task."""
    task_data = AddTaskRequest(
        title="Test Task",
        description="Test Description",
        user_id="user123",
        completed=False,
        priority="high",
        category="work"
    )

    created_task = create_task(session, task_data)

    assert created_task.title == "Test Task"
    assert created_task.description == "Test Description"
    assert created_task.user_id == "user123"
    assert created_task.completed is False
    assert created_task.priority == "high"
    assert created_task.category == "work"
    assert created_task.id is not None


def test_create_task_with_validation(session):
    """Test that due date validation works in create_task."""
    future_date = datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 1)

    task_data = AddTaskRequest(
        title="Test Task",
        user_id="user123",
        due_date=future_date
    )

    created_task = create_task(session, task_data)

    assert created_task.title == "Test Task"
    # The database stores naive datetimes, so compare without timezone info
    assert created_task.due_date.replace(tzinfo=None) == future_date.replace(tzinfo=None)


def test_create_task_past_due_date(session):
    """Test that creating a task with past due date raises an exception."""
    past_date = datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year - 1)

    task_data = AddTaskRequest(
        title="Test Task",
        user_id="user123",
        due_date=past_date
    )

    with pytest.raises(Exception):  # This will be an HTTPException in the actual implementation
        create_task(session, task_data)


def test_list_tasks_filtered(session):
    """Test listing tasks with filters."""
    # Create some test tasks
    task1_data = AddTaskRequest(
        title="Task 1",
        user_id="user123",
        category="work",
        priority="high",
        completed=False
    )
    task1 = create_task(session, task1_data)

    task2_data = AddTaskRequest(
        title="Task 2",
        user_id="user123",
        category="personal",
        priority="low",
        completed=True
    )
    task2 = create_task(session, task2_data)

    task3_data = AddTaskRequest(
        title="Different User Task",
        user_id="user456",  # Different user
        category="work",
        priority="medium",
        completed=False
    )
    task3 = create_task(session, task3_data)

    # Test listing tasks for user123
    list_request = ListTasksRequest(
        user_id="user123"
    )
    user_tasks = list_tasks_filtered(session, list_request)

    assert len(user_tasks) == 2  # Should only see tasks for user123
    assert all(task.user_id == "user123" for task in user_tasks)

    # Test filtering by status
    list_request = ListTasksRequest(
        user_id="user123",
        status="pending"
    )
    pending_tasks = list_tasks_filtered(session, list_request)

    assert len(pending_tasks) == 1
    assert pending_tasks[0].completed is False

    # Test filtering by category
    list_request = ListTasksRequest(
        user_id="user123",
        category="work"
    )
    work_tasks = list_tasks_filtered(session, list_request)

    assert len(work_tasks) == 1
    assert work_tasks[0].category == "work"


def test_complete_task_in_db(session):
    """Test completing a task."""
    # Create a task
    task_data = AddTaskRequest(
        title="Test Task",
        user_id="user123",
        completed=False
    )
    task = create_task(session, task_data)

    assert task.completed is False

    # Complete the task
    completed_task = complete_task_in_db(session, task.id, "user123")

    assert completed_task.id == task.id
    assert completed_task.completed is True


def test_complete_task_wrong_user(session):
    """Test that completing another user's task fails."""
    # Create a task for user123
    task_data = AddTaskRequest(
        title="Test Task",
        user_id="user123"
    )
    task = create_task(session, task_data)

    # Try to complete it as user456 (should fail)
    with pytest.raises(Exception):  # This will be an HTTPException
        complete_task_in_db(session, task.id, "user456")


def test_update_task_in_db(session):
    """Test updating a task."""
    # Create a task
    task_data = AddTaskRequest(
        title="Original Task",
        user_id="user123",
        priority="low",
        category="personal"
    )
    task = create_task(session, task_data)

    assert task.title == "Original Task"
    assert task.priority == "low"

    # Update the task
    update_data = UpdateTaskRequest(
        title="Updated Task",
        priority="high"
    )
    updated_task = update_task_in_db(session, task.id, "user123", update_data)

    assert updated_task.id == task.id
    assert updated_task.title == "Updated Task"
    assert updated_task.priority == "high"
    assert updated_task.category == "personal"  # Should remain unchanged


def test_delete_task_from_db(session):
    """Test deleting a task."""
    # Create a task
    task_data = AddTaskRequest(
        title="Test Task to Delete",
        user_id="user123"
    )
    task = create_task(session, task_data)

    # Verify task exists
    stmt = select(Task).where(Task.id == task.id)
    existing_task = session.exec(stmt).first()
    assert existing_task is not None

    # Delete the task
    result = delete_task_from_db(session, task.id, "user123")

    assert result is True

    # Verify task is deleted
    stmt = select(Task).where(Task.id == task.id)
    deleted_task = session.exec(stmt).first()
    assert deleted_task is None


def test_delete_task_wrong_user(session):
    """Test that deleting another user's task returns False."""
    # Create a task for user123
    task_data = AddTaskRequest(
        title="Test Task",
        user_id="user123"
    )
    task = create_task(session, task_data)

    # Try to delete it as user456 (should return False)
    result = delete_task_from_db(session, task.id, "user456")

    assert result is False

    # Task should still exist
    stmt = select(Task).where(Task.id == task.id)
    still_exists = session.exec(stmt).first()
    assert still_exists is not None


def test_recurrence_logic(session):
    """Test the recurrence logic functionality."""
    # Test calculate_next_occurrence function
    current_date = datetime(2025, 1, 15, 10, 0, 0)  # Jan 15, 2025

    # Test daily recurrence
    next_daily = calculate_next_occurrence(current_date, "daily", 1)
    expected_daily = current_date + timedelta(days=1)
    assert next_daily == expected_daily

    # Test weekly recurrence
    next_weekly = calculate_next_occurrence(current_date, "weekly", 1)
    expected_weekly = current_date + timedelta(weeks=1)
    assert next_weekly == expected_weekly

    # Test monthly recurrence
    next_monthly = calculate_next_occurrence(current_date, "monthly", 1)
    # Should be Feb 15, 2025
    expected_monthly = datetime(2025, 2, 15, 10, 0, 0)
    assert next_monthly == expected_monthly

    # Test yearly recurrence
    next_yearly = calculate_next_occurrence(current_date, "yearly", 1)
    # Should be Jan 15, 2026
    expected_yearly = datetime(2026, 1, 15, 10, 0, 0)
    assert next_yearly == expected_yearly

    # Test recurrence with interval
    next_daily_interval = calculate_next_occurrence(current_date, "daily", 3)
    expected_daily_interval = current_date + timedelta(days=3)
    assert next_daily_interval == expected_daily_interval


def test_recurring_task_completion_creates_next_occurrence(session):
    """Test that completing a recurring task creates the next occurrence."""
    # Create a recurring task
    future_date = datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 1)
    task_data = AddTaskRequest(
        title="Recurring Task",
        description="A task that repeats daily",
        user_id="user123",
        completed=False,
        is_recurring=True,
        recurrence_pattern="daily",
        recurrence_interval=1,
        due_date=future_date,
        priority="medium",
        category="work"
    )

    task = create_task(session, task_data)

    # Verify the original task exists
    assert task.title == "Recurring Task"
    assert task.is_recurring is True
    assert task.recurrence_pattern == "daily"

    # Mark the task as completed to trigger recurrence
    completed_task = complete_task_in_db(session, task.id, "user123")
    assert completed_task.completed is True

    # Get all tasks for the user to check if a new one was created
    list_request = ListTasksRequest(user_id="user123")
    all_tasks = list_tasks_filtered(session, list_request)

    # Should have 2 tasks now (original completed + new recurring one)
    assert len(all_tasks) == 2

    # Find the new recurring task (the one that's not completed)
    new_task = None
    for t in all_tasks:
        if t.id != completed_task.id and t.completed is False:
            new_task = t
            break

    assert new_task is not None
    assert new_task.title == "Recurring Task"
    assert new_task.completed is False
    assert new_task.user_id == "user123"
    assert new_task.priority == "medium"
    assert new_task.category == "work"
    # The new task should have an updated due date based on the recurrence pattern
    expected_next_date = completed_task.due_date + timedelta(days=1)  # Daily recurrence
    assert new_task.due_date == expected_next_date
    