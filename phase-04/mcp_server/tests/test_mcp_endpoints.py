import sys
import os

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the tools from the MCP server
from src.mcp_server.models import AddTaskRequest, ListTasksRequest, UpdateTaskRequest
from src.mcp_server.tools import create_task, list_tasks_filtered, complete_task_in_db, delete_task_from_db, update_task_in_db
from src.mcp_server.database import get_session, init_db

def test_mcp_endpoints():
    print("Testing MCP Server endpoints...")

    # Initialize the database
    init_db()

    # Test data
    user_id = "test_user_123"

    # Test creating a session
    with next(get_session()) as session:
        print("\n1. Testing add_task functionality...")

        # Create a test task
        task_data = AddTaskRequest(
            title="Test Task from MCP",
            description="This is a test task created via MCP server",
            user_id=user_id,
            completed=False,
            priority="medium",
            category="test"
        )

        created_task = create_task(session, task_data)
        print(f"✓ Created task with ID: {created_task.id}, Title: {created_task.title}")

        print("\n2. Testing list_tasks functionality...")

        # List tasks for the user
        list_request = ListTasksRequest(user_id=user_id)
        tasks = list_tasks_filtered(session, list_request)
        print(f"✓ Found {len(tasks)} tasks for user {user_id}")
        for task in tasks:
            print(f"  - Task ID: {task.id}, Title: {task.title}, Completed: {task.completed}")

        print("\n3. Testing update_task functionality...")

        # Update the task
        update_data = UpdateTaskRequest(title="Updated Test Task", priority="high")
        updated_task = update_task_in_db(session, created_task.id, user_id, update_data)
        print(f"✓ Updated task ID: {updated_task.id}, New Title: {updated_task.title}, Priority: {updated_task.priority}")

        print("\n4. Testing complete_task functionality...")

        # Complete the task
        completed_task = complete_task_in_db(session, created_task.id, user_id)
        print(f"✓ Completed task ID: {completed_task.id}, Status: {'Completed' if completed_task.completed else 'Pending'}")

        print("\n5. Testing delete_task functionality...")

        # Delete the task
        deleted = delete_task_from_db(session, created_task.id, user_id)
        if deleted:
            print(f"✓ Deleted task ID: {created_task.id}")
        else:
            print(f"✗ Failed to delete task ID: {created_task.id}")

    print("\n✓ All MCP server endpoint tests completed successfully!")

if __name__ == "__main__":
    test_mcp_endpoints()
