import pytest
import sys
import os
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta

# Add the src directory to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.task import TaskCreate
from src.services.task_service import TaskService


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


def test_search_by_keyword(session: Session):
    """Test searching tasks by keyword in title or description."""
    user_id = "1"

    # Create tasks
    task1_data = TaskCreate(title="Grocery shopping", description="Buy milk and bread")
    task2_data = TaskCreate(title="Meeting prep", description="Prepare presentation")
    task3_data = TaskCreate(title="Email response", description="Reply to client")

    TaskService.create_task(user_id, task1_data, session)
    TaskService.create_task(user_id, task2_data, session)
    TaskService.create_task(user_id, task3_data, session)

    # Search for tasks containing "milk"
    results = TaskService.search_tasks(
        user_id=user_id,
        keyword="milk",
        completed=None,
        date_from=None,
        date_to=None,
        session=session
    )

    assert len(results) == 1
    assert "milk" in results[0].description.lower()

    # Search for tasks containing "meeting"
    results = TaskService.search_tasks(
        user_id=user_id,
        keyword="meeting",
        completed=None,
        date_from=None,
        date_to=None,
        session=session
    )

    assert len(results) == 1
    assert "meeting" in results[0].title.lower()


def test_filter_by_status(session: Session):
    """Test filtering tasks by completion status."""
    user_id = "1"

    # Create tasks
    task1_data = TaskCreate(title="Completed task", description="This is done")
    task2_data = TaskCreate(title="Pending task", description="This needs to be done")

    task1 = TaskService.create_task(user_id, task1_data, session)
    TaskService.create_task(user_id, task2_data, session)

    # Mark first task as completed
    TaskService.toggle_task_completion(task1.id, user_id, session)

    # Get completed tasks
    completed_tasks = TaskService.search_tasks(
        user_id=user_id,
        keyword=None,
        completed=True,
        date_from=None,
        date_to=None,
        session=session
    )

    assert len(completed_tasks) == 1
    assert completed_tasks[0].completed is True

    # Get pending tasks
    pending_tasks = TaskService.search_tasks(
        user_id=user_id,
        keyword=None,
        completed=False,
        date_from=None,
        date_to=None,
        session=session
    )

    assert len(pending_tasks) == 1
    assert pending_tasks[0].completed is False


def test_filter_by_date_range(session: Session):
    """Test filtering tasks by date range."""
    user_id = "1"

    # Create tasks
    task1_data = TaskCreate(title="Old task", description="Created long ago")
    task2_data = TaskCreate(title="Recent task", description="Created recently")

    TaskService.create_task(user_id, task1_data, session)
    TaskService.create_task(user_id, task2_data, session)

    # Search for tasks created in the last day (should include both)
    yesterday = datetime.utcnow() - timedelta(days=1)
    future = datetime.utcnow() + timedelta(days=1)

    recent_tasks = TaskService.search_tasks(
        user_id=user_id,
        keyword=None,
        completed=None,
        date_from=yesterday,
        date_to=future,
        session=session
    )

    assert len(recent_tasks) >= 2  # Both tasks should be in this range


def test_combined_search_and_filter(session: Session):
    """Test combining search and filter criteria."""
    user_id = "1"

    # Create tasks
    task1_data = TaskCreate(title="Completed grocery", description="Buy food")
    task2_data = TaskCreate(title="Pending meeting", description="Schedule call")
    task3_data = TaskCreate(title="Completed meeting", description="Prepare agenda")

    task1 = TaskService.create_task(user_id, task1_data, session)
    task2 = TaskService.create_task(user_id, task2_data, session)
    task3 = TaskService.create_task(user_id, task3_data, session)

    # Mark tasks 1 and 3 as completed
    TaskService.toggle_task_completion(task1.id, user_id, session)
    TaskService.toggle_task_completion(task3.id, user_id, session)

    # Search for completed tasks with "meeting" in title
    results = TaskService.search_tasks(
        user_id=user_id,
        keyword="meeting",
        completed=True,
        date_from=None,
        date_to=None,
        session=session
    )

    assert len(results) == 1
    assert "meeting" in results[0].title.lower()
    assert results[0].completed is True
    