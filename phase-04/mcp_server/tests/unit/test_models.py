import pytest
import sys
import os

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mcp_server.models import Task, AddTaskRequest


def test_task_creation():
    """Test creating a Task instance."""
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id="user123",
        completed=False
    )

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.user_id == "user123"
    assert task.completed is False
    assert task.category == "other"  # Default value
    assert task.priority == "medium"  # Default value


def test_add_task_request_validation():
    """Test validation of AddTaskRequest model."""
    # Test with valid data
    request = AddTaskRequest(
        title="Test Task",
        description="Test Description",
        user_id="user123",
        completed=False
    )

    assert request.title == "Test Task"
    assert request.user_id == "user123"


def test_add_task_request_title_validation():
    """Test that title validation works."""
    with pytest.raises(ValueError):
        AddTaskRequest(
            title="",  # Empty title should fail validation
            user_id="user123"
        )


def test_add_task_request_user_id_validation():
    """Test that user_id validation works."""
    with pytest.raises(ValueError):
        AddTaskRequest(
            title="Test Task",
            user_id=""  # Empty user_id should fail validation
        )
        