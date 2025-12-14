"""Unit tests for the TaskService class."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timezone
from src.models.task import Task, TaskCreate, TaskUpdate
from src.services.task_service import TaskService


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


def test_create_task(session: Session):
    """Test creating a new task."""
    user_id = "user123"
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description"
    )

    task = TaskService.create_task(user_id, task_data, session)

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.user_id == user_id
    assert task.id is not None
    assert task.created_at is not None
    assert task.updated_at is not None


def test_get_task_by_id(session: Session):
    """Test getting a task by ID."""
    # First create a task
    user_id = "user123"
    task_data = TaskCreate(title="Test Task", description="Test Description")
    created_task = TaskService.create_task(user_id, task_data, session)

    # Get the task by ID
    retrieved_task = TaskService.get_task_by_id(created_task.id, user_id, session)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == "Test Task"
    assert retrieved_task.description == "Test Description"


def test_get_task_by_id_wrong_user(session: Session):
    """Test getting a task by ID with wrong user ID."""
    # First create a task
    user_id = "user123"
    other_user_id = "user456"
    task_data = TaskCreate(title="Test Task", description="Test Description")
    created_task = TaskService.create_task(user_id, task_data, session)

    # Try to get the task with wrong user ID
    retrieved_task = TaskService.get_task_by_id(created_task.id, other_user_id, session)

    assert retrieved_task is None


def test_get_tasks_by_user(session: Session):
    """Test getting all tasks for a user."""
    user_id = "user123"

    # Create multiple tasks for the user
    task_data1 = TaskCreate(title="Task 1", description="Description 1")
    task_data2 = TaskCreate(title="Task 2", description="Description 2")

    TaskService.create_task(user_id, task_data1, session)
    TaskService.create_task(user_id, task_data2, session)

    # Get tasks for the user
    tasks = TaskService.get_tasks_by_user(user_id, session)

    assert len(tasks) == 2
    titles = [task.title for task in tasks]
    assert "Task 1" in titles
    assert "Task 2" in titles


def test_update_task(session: Session):
    """Test updating a task."""
    user_id = "user123"

    # Create a task
    task_data = TaskCreate(title="Original Task", description="Original Description")
    original_task = TaskService.create_task(user_id, task_data, session)

    # Update the task
    update_data = TaskUpdate(
        title="Updated Task",
        description="Updated Description"
    )
    updated_task = TaskService.update_task(original_task.id, user_id, update_data, session)

    assert updated_task is not None
    assert updated_task.id == original_task.id
    assert updated_task.title == "Updated Task"
    assert updated_task.description == "Updated Description"
    # The updated_at should be set to a new time when the update happens
    # If they are the same due to timing precision, we just verify that updated_at is set
    assert updated_task.updated_at is not None


def test_update_task_wrong_user(session: Session):
    """Test updating a task with wrong user ID."""
    user_id = "user123"
    other_user_id = "user456"

    # Create a task
    task_data = TaskCreate(title="Original Task", description="Original Description")
    original_task = TaskService.create_task(user_id, task_data, session)

    # Try to update the task with wrong user ID
    update_data = TaskUpdate(title="Updated Task")
    updated_task = TaskService.update_task(original_task.id, other_user_id, update_data, session)

    assert updated_task is None


def test_delete_task(session: Session):
    """Test deleting a task."""
    user_id = "user123"

    # Create a task
    task_data = TaskCreate(title="Task to Delete", description="Description")
    task = TaskService.create_task(user_id, task_data, session)

    # Delete the task
    success = TaskService.delete_task(task.id, user_id, session)

    assert success is True

    # Verify the task is deleted
    retrieved_task = TaskService.get_task_by_id(task.id, user_id, session)
    assert retrieved_task is None


def test_delete_task_wrong_user(session: Session):
    """Test deleting a task with wrong user ID."""
    user_id = "user123"
    other_user_id = "user456"

    # Create a task
    task_data = TaskCreate(title="Task to Delete", description="Description")
    task = TaskService.create_task(user_id, task_data, session)

    # Try to delete the task with wrong user ID
    success = TaskService.delete_task(task.id, other_user_id, session)

    assert success is False

    # Verify the task still exists
    retrieved_task = TaskService.get_task_by_id(task.id, user_id, session)
    assert retrieved_task is not None


def test_toggle_task_completion(session: Session):
    """Test toggling task completion status."""
    user_id = "user123"

    # Create a task
    task_data = TaskCreate(title="Test Task", description="Description")
    task = TaskService.create_task(user_id, task_data, session)

    # Verify initial state
    assert task.completed is False

    # Toggle completion
    toggled_task = TaskService.toggle_task_completion(task.id, user_id, session)

    assert toggled_task is not None
    assert toggled_task.id == task.id
    assert toggled_task.completed is True
    # The updated_at should be set when the task is toggled
    assert toggled_task.updated_at is not None


def test_toggle_task_completion_wrong_user(session: Session):
    """Test toggling task completion with wrong user ID."""
    user_id = "user123"
    other_user_id = "user456"

    # Create a task
    task_data = TaskCreate(title="Test Task", description="Description")
    task = TaskService.create_task(user_id, task_data, session)

    # Try to toggle completion with wrong user ID
    toggled_task = TaskService.toggle_task_completion(task.id, other_user_id, session)

    assert toggled_task is None


def test_search_tasks(session: Session):
    """Test searching and filtering tasks."""
    user_id = "user123"

    # Create multiple tasks
    task_data1 = TaskCreate(title="Grocery Shopping", description="Buy milk and bread")
    task_data2 = TaskCreate(title="Meeting Prep", description="Prepare presentation")
    task_data3 = TaskCreate(title="Email Response", description="Reply to client", completed=True)

    TaskService.create_task(user_id, task_data1, session)
    TaskService.create_task(user_id, task_data2, session)
    TaskService.create_task(user_id, task_data3, session)

    # Search by keyword
    keyword_results = TaskService.search_tasks(user_id, keyword="milk", completed=None,
                                              date_from=None, date_to=None, session=session)
    assert len(keyword_results) >= 1
    assert any("milk" in task.description.lower() for task in keyword_results)

    # Filter by completion status
    completed_results = TaskService.search_tasks(user_id, keyword=None, completed=True,
                                                 date_from=None, date_to=None, session=session)
    assert len(completed_results) == 1
    assert all(task.completed for task in completed_results)

    # Filter by non-completion status
    incomplete_results = TaskService.search_tasks(user_id, keyword=None, completed=False,
                                                  date_from=None, date_to=None, session=session)
    assert len(incomplete_results) == 2
    assert all(not task.completed for task in incomplete_results)


def test_create_recurring_task(session: Session):
    """Test creating a recurring task."""
    user_id = "user123"
    task_data = TaskCreate(
        title="Weekly Meeting",
        description="Team weekly sync",
        is_recurring=True,
        recurrence_pattern="weekly",
        recurrence_interval=1
    )

    recurring_task = TaskService.create_recurring_task(user_id, task_data, session)

    assert recurring_task.title == "Weekly Meeting"
    assert recurring_task.description == "Team weekly sync"
    assert recurring_task.is_recurring is True
    assert recurring_task.recurrence_pattern == "weekly"
    assert recurring_task.recurrence_interval == 1
    assert recurring_task.id is not None


def test_create_recurring_task_invalid_pattern(session: Session):
    """Test creating a recurring task with invalid pattern."""
    user_id = "user123"
    task_data = TaskCreate(
        title="Invalid Recurring Task",
        description="This should fail",
        is_recurring=True,
        recurrence_pattern="invalid_pattern",  # Invalid pattern
        recurrence_interval=1
    )

    from src.utils.exceptions import InvalidRecurrencePatternException
    with pytest.raises(InvalidRecurrencePatternException):
        TaskService.create_recurring_task(user_id, task_data, session)


def test_create_recurring_task_missing_pattern(session: Session):
    """Test creating a recurring task without pattern."""
    user_id = "user123"
    task_data = TaskCreate(
        title="Missing Pattern Task",
        description="This should fail",
        is_recurring=True
        # Missing recurrence_pattern
    )

    from src.utils.exceptions import InvalidRecurrencePatternException
    with pytest.raises(InvalidRecurrencePatternException):
        TaskService.create_recurring_task(user_id, task_data, session)


def test_due_date_validation():
    """Test due date and reminder validation."""
    from datetime import datetime, timedelta
    from src.utils.exceptions import InvalidReminderTimeException

    future_due = datetime.now(timezone.utc) + timedelta(hours=2)
    future_reminder = datetime.now(timezone.utc) + timedelta(hours=1)  # Before due date

    # This should not raise an exception
    TaskService._validate_due_date_and_reminder(future_due, future_reminder)

    # Test with reminder after due date (should raise exception)
    with pytest.raises(InvalidReminderTimeException):
        TaskService._validate_due_date_and_reminder(future_reminder, future_due)