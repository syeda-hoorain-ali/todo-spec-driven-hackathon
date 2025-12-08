"""
Tests for User Story 3 - Delete Tasks

As a user, I want to remove tasks I no longer need so that my task list
stays organized and relevant.

Test Criteria:
- Can delete a task by ID
- Deleted task no longer appears in the task list
- Appropriate error message when trying to delete non-existent task
"""
import pytest
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager
from todo_app.ui.renderer import Renderer


class TestUserStory3:
    """Test cases for User Story 3 - Delete Tasks"""

    def test_delete_task_functionality(self):
        """T040: Implement delete_task method in managers/task_manager.py"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Task to delete")

        # Verify task exists
        assert len(tm.get_all_tasks()) == 1
        assert tm.get_task(task.id) is not None

        # Delete the task
        success = tm.delete_task(task.id)

        # Verify deletion
        assert success is True
        assert len(tm.get_all_tasks()) == 0
        assert tm.get_task(task.id) is None

    def test_delete_nonexistent_task(self):
        """T045, T046: Validate task ID exists and handle error for non-existent task"""
        tm = TaskManager()

        # Try to delete a non-existent task
        success = tm.delete_task(999)

        # Should return False
        assert success is False

    def test_multiple_task_deletion(self):
        """Test deleting multiple tasks"""
        tm = TaskManager()

        # Create multiple tasks
        task1 = tm.create_task("Task 1")
        task2 = tm.create_task("Task 2")
        task3 = tm.create_task("Task 3")

        # Verify all tasks exist
        assert len(tm.get_all_tasks()) == 3

        # Delete one task
        tm.delete_task(task2.id)
        assert len(tm.get_all_tasks()) == 2
        assert tm.get_task(task2.id) is None

        # Verify other tasks still exist
        assert tm.get_task(task1.id) is not None
        assert tm.get_task(task3.id) is not None

        # Delete another task
        tm.delete_task(task1.id)
        assert len(tm.get_all_tasks()) == 1
        assert tm.get_task(task1.id) is None
        assert tm.get_task(task3.id) is not None

    def test_delete_all_tasks(self):
        """Test deleting all tasks"""
        tm = TaskManager()

        # Create multiple tasks
        task1 = tm.create_task("Task 1")
        task2 = tm.create_task("Task 2")
        task3 = tm.create_task("Task 3")

        # Verify all tasks exist
        assert len(tm.get_all_tasks()) == 3

        # Delete all tasks
        tm.delete_task(task1.id)
        tm.delete_task(task2.id)
        tm.delete_task(task3.id)

        # Verify no tasks remain
        assert len(tm.get_all_tasks()) == 0
        assert tm.get_task(task1.id) is None
        assert tm.get_task(task2.id) is None
        assert tm.get_task(task3.id) is None

    def test_delete_task_then_add_new_task(self):
        """Test that after deletion, new tasks get appropriate IDs"""
        tm = TaskManager()

        # Create and delete a task
        task1 = tm.create_task("Task 1")
        original_id = task1.id
        tm.delete_task(task1.id)

        # Create a new task - it should get the next available ID
        task2 = tm.create_task("Task 2")
        # In our implementation, we keep incrementing IDs, so task2 should have a higher ID
        assert task2.id > original_id

    def test_task_not_in_list_after_deletion(self):
        """T043: Verify deleted task no longer appears in the task list"""
        tm = TaskManager()

        # Create multiple tasks
        task1 = tm.create_task("Task 1")
        task2 = tm.create_task("Task 2")
        task3 = tm.create_task("Task 3")

        # Verify all tasks in the list
        all_tasks = tm.get_all_tasks()
        assert len(all_tasks) == 3
        task_ids = [t.id for t in all_tasks]
        assert task1.id in task_ids
        assert task2.id in task_ids
        assert task3.id in task_ids

        # Delete one task
        tm.delete_task(task2.id)

        # Verify deleted task is not in the list
        remaining_tasks = tm.get_all_tasks()
        assert len(remaining_tasks) == 2
        remaining_ids = [t.id for t in remaining_tasks]
        assert task2.id not in remaining_ids
        assert task1.id in remaining_ids
        assert task3.id in remaining_ids

    def test_delete_task_with_different_statuses(self):
        """Test deleting tasks with different statuses"""
        tm = TaskManager()

        # Create tasks with different statuses
        pending_task = tm.create_task("Pending task")
        in_progress_task = tm.create_task("In-progress task")
        tm.update_task(in_progress_task.id, status="in-progress")
        completed_task = tm.create_task("Completed task")
        tm.mark_complete(completed_task.id)

        # Verify all tasks exist
        assert len(tm.get_all_tasks()) == 3

        # Delete the completed task
        success = tm.delete_task(completed_task.id)
        assert success is True

        # Verify only pending and in-progress tasks remain
        remaining = tm.get_all_tasks()
        assert len(remaining) == 2
        remaining_ids = [t.id for t in remaining]
        assert completed_task.id not in remaining_ids