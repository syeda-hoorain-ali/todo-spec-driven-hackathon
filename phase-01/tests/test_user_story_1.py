"""
Tests for User Story 1 - Add and View Tasks

As a user, I want to add new tasks to my todo list and view them in the console
so that I can keep track of what I need to do.

Test Criteria:
- Can add a task through the command line
- Can view all tasks in the console with their status
- Task appears in the task list with a unique ID and pending status
"""
import pytest
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager
from todo_app.ui.renderer import Renderer
from io import StringIO
from contextlib import redirect_stdout


class TestUserStory1:
    """Test cases for User Story 1 - Add and View Tasks"""

    def test_task_creation_with_auto_generated_id(self):
        """T020: Implement Task creation with auto-generated ID in models/task.py"""
        # Create a task manager
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Test task")

        # Verify the task has an auto-generated ID
        assert task.id is not None
        assert task.id > 0
        assert task.title == "Test task"
        assert task.status == "pending"
        assert task.priority == "medium"

    def test_add_task_method(self):
        """T021: Implement add_task method in managers/task_manager.py"""
        tm = TaskManager()

        # Add a task
        task = tm.create_task("Test task", description="Test description")

        # Verify task was added
        assert len(tm.get_all_tasks()) == 1
        assert task.title == "Test task"
        assert task.description == "Test description"

        # Verify auto-incrementing ID
        task2 = tm.create_task("Second task")
        assert task2.id == task.id + 1

    def test_get_all_tasks_method(self):
        """T024: Implement get_all_tasks method in managers/task_manager.py"""
        tm = TaskManager()

        # Add some tasks
        tm.create_task("Task 1")
        tm.create_task("Task 2")
        tm.create_task("Task 3")

        # Get all tasks
        tasks = tm.get_all_tasks()

        # Verify all tasks are returned
        assert len(tasks) == 3
        titles = [task.title for task in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_task_creation_with_validation(self):
        """T029: Validate task title and description constraints"""
        tm = TaskManager()

        # Test title validation
        with pytest.raises(ValueError, match="Title cannot be empty"):
            tm.create_task("")

        with pytest.raises(ValueError, match="Title cannot exceed 200 characters"):
            tm.create_task("x" * 201)

        # Test description validation
        with pytest.raises(ValueError, match="Description cannot exceed 1000 characters"):
            tm.create_task("Valid title", description="x" * 1001)

        # Test valid creation
        task = tm.create_task("Valid task", description="Valid description")
        assert task.title == "Valid task"
        assert task.description == "Valid description"

    def test_rich_table_display(self):
        """T025: Implement rich table display for task list in ui/renderer.py"""
        # Create some tasks
        tm = TaskManager()
        task1 = tm.create_task("Task 1", priority="high")
        task2 = tm.create_task("Task 2", status="in-progress", priority="medium")
        task3 = tm.create_task("Task 3", status="complete", priority="low")

        # Test rendering
        renderer = Renderer()

        # Capture output
        f = StringIO()
        with redirect_stdout(f):
            renderer.display_tasks(tm.get_all_tasks())

        output = f.getvalue()

        # Verify that the output contains task information
        assert "Task 1" in output
        assert "Task 2" in output
        assert "Task 3" in output
        assert str(task1.id) in output

    def test_unique_id_generation(self):
        """Verify that each task gets a unique ID"""
        tm = TaskManager()

        task1 = tm.create_task("Task 1")
        task2 = tm.create_task("Task 2")
        task3 = tm.create_task("Task 3")

        # All IDs should be unique
        ids = [task1.id, task2.id, task3.id]
        assert len(ids) == len(set(ids))

        # IDs should be sequential
        assert task2.id == task1.id + 1
        assert task3.id == task2.id + 1

    def test_pending_status_default(self):
        """Verify that new tasks have pending status by default"""
        tm = TaskManager()
        task = tm.create_task("Test task")

        assert task.status == "pending"