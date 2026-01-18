"""
Integration tests for the MCP server end-to-end functionality.
Tests the complete workflow of creating, listing, updating, completing, and deleting tasks.
"""
import sys
import os
from unittest.mock import patch

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.mcp_server.models import AddTaskRequest, ListTasksRequest, UpdateTaskRequest
from src.mcp_server.tools import create_task, list_tasks_filtered, update_task_in_db, complete_task_in_db, delete_task_from_db
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

def test_end_to_end_task_workflow():
    """
    Test the complete task workflow: create -> list -> update -> complete -> delete
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Mock the database session in the tools
        with patch('src.mcp_server.main.get_session', return_value=iter([session])):

            # 1. Create a task
            add_request = {
                "title": "Integration Test Task",
                "description": "Test task for end-to-end workflow",
                "user_id": "test_user_123",
                "priority": "high",
                "category": "testing"
            }

            # Since the functions in main.py are async, we need to test differently
            # For now, we'll test the tools module functions directly
            # Create the task using tools module
            task_data = AddTaskRequest(**add_request)
            created_task = create_task(session, task_data)

            # Verify task was created
            assert created_task.title == "Integration Test Task"
            assert created_task.user_id == "test_user_123"
            assert created_task.completed is False
            assert created_task.priority == "high"

            # 2. List tasks to verify it's there
            list_request = ListTasksRequest(user_id="test_user_123")
            tasks = list_tasks_filtered(session, list_request)

            assert len(tasks) == 1
            assert tasks[0].id == created_task.id
            assert tasks[0].title == "Integration Test Task"

            # 3. Update the task
            update_request = UpdateTaskRequest(
                title="Updated Integration Test Task",
                priority="medium",
                completed=False
            )
            updated_task = update_task_in_db(session, created_task.id, "test_user_123", update_request)

            assert updated_task.title == "Updated Integration Test Task"
            assert updated_task.priority == "medium"

            # 4. Complete the task
            completed_task = complete_task_in_db(session, created_task.id, "test_user_123")

            assert completed_task.id == created_task.id
            assert completed_task.completed is True

            # 5. Delete the task
            delete_success = delete_task_from_db(session, created_task.id, "test_user_123")

            assert delete_success is True

            # Verify task is deleted
            final_list = list_tasks_filtered(session, ListTasksRequest(user_id="test_user_123"))
            assert len(final_list) == 0


def test_user_isolation():
    """
    Test that users can only access their own tasks
    """
    # Use an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Create tasks for different users
        user1_task_data = AddTaskRequest(
            title="User 1 Task",
            user_id="user1",
            description="Task for user 1"
        )
        user1_task = create_task(session, user1_task_data)

        user2_task_data = AddTaskRequest(
            title="User 2 Task",
            user_id="user2",
            description="Task for user 2"
        )
        user2_task = create_task(session, user2_task_data)

        # Verify user isolation
        user1_tasks = list_tasks_filtered(session, ListTasksRequest(user_id="user1"))
        user2_tasks = list_tasks_filtered(session, ListTasksRequest(user_id="user2"))

        assert len(user1_tasks) == 1
        assert user1_tasks[0].user_id == "user1"

        assert len(user2_tasks) == 1
        assert user2_tasks[0].user_id == "user2"


if __name__ == "__main__":
    test_end_to_end_task_workflow()
    test_user_isolation()
    print("All integration tests passed!")
    