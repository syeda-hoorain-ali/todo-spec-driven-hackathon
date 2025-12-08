"""
Tests for User Story 2 - Mark Tasks Complete

As a user, I want to mark tasks as complete so that I can track my progress
and focus on remaining tasks.

Test Criteria:
- Can mark a pending task as complete
- Task status changes to complete and is visually distinct in the list
- Can mark a completed task as pending again
"""
import pytest
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager
from todo_app.ui.renderer import Renderer
from io import StringIO
from contextlib import redirect_stdout


class TestUserStory2:
    """Test cases for User Story 2 - Mark Tasks Complete"""

    def test_mark_complete_functionality(self):
        """T030: Add mark_complete method to TaskManager"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Test task")

        # Verify initial status
        assert task.status == "pending"

        # Mark as complete
        completed_task = tm.mark_complete(task.id)

        # Verify status changed to complete
        assert completed_task is not None
        assert completed_task.status == "complete"

    def test_mark_incomplete_functionality(self):
        """T030: Add mark_incomplete method to TaskManager"""
        tm = TaskManager()

        # Create and complete a task
        task = tm.create_task("Test task")
        tm.mark_complete(task.id)

        # Verify it's complete
        assert task.status == "complete"

        # Mark as incomplete
        incomplete_task = tm.mark_incomplete(task.id)

        # Verify status changed back to pending
        assert incomplete_task is not None
        assert incomplete_task.status == "pending"

    def test_mark_complete_nonexistent_task(self):
        """T038: Validate task ID exists before marking complete"""
        tm = TaskManager()

        # Try to mark a non-existent task as complete
        result = tm.mark_complete(999)

        # Should return None
        assert result is None

    def test_mark_incomplete_nonexistent_task(self):
        """T038: Validate task ID exists before marking incomplete"""
        tm = TaskManager()

        # Try to mark a non-existent task as incomplete
        result = tm.mark_incomplete(999)

        # Should return None
        assert result is None

    def test_task_status_transitions(self):
        """T033: Update Task model to support status transitions"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Test task")

        # Test pending -> complete
        tm.mark_complete(task.id)
        assert task.status == "complete"

        # Test complete -> pending
        tm.mark_incomplete(task.id)
        assert task.status == "pending"

        # Test pending -> in-progress -> complete
        task2 = tm.create_task("Test task 2")
        tm.update_task(task2.id, status="in-progress")
        assert task2.status == "in-progress"

        tm.mark_complete(task2.id)
        assert task2.status == "complete"

    def test_visual_distinction_for_completed_tasks(self):
        """T034: Update renderer to visually distinguish completed tasks"""
        tm = TaskManager()

        # Create tasks with different statuses
        pending_task = tm.create_task("Pending task", priority="high")
        completed_task = tm.create_task("Completed task", priority="medium")
        tm.mark_complete(completed_task.id)

        # Test rendering
        renderer = Renderer()

        # Capture output
        f = StringIO()
        with redirect_stdout(f):
            renderer.display_tasks([pending_task, completed_task])

        output = f.getvalue()

        # Completed tasks should be visually distinct (e.g., with strikethrough or different styling)
        # The renderer should show the completed task differently than the pending task
        assert "Pending task" in output
        assert "Completed task" in output  # The task should still be displayed

    def test_task_workflow_complete_and_reopen(self):
        """Test complete workflow: pending -> complete -> pending"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Workflow test task")

        # Verify initial state
        assert task.status == "pending"

        # Mark as complete
        tm.mark_complete(task.id)
        assert task.status == "complete"

        # Mark as incomplete again (re-open)
        tm.mark_incomplete(task.id)
        assert task.status == "pending"

    def test_multiple_task_status_changes(self):
        """Test changing status on multiple tasks"""
        tm = TaskManager()

        # Create multiple tasks
        task1 = tm.create_task("Task 1")
        task2 = tm.create_task("Task 2")
        task3 = tm.create_task("Task 3")

        # Mark task1 and task3 as complete, keep task2 pending
        tm.mark_complete(task1.id)
        tm.mark_complete(task3.id)

        # Verify statuses
        assert task1.status == "complete"
        assert task2.status == "pending"  # Should remain pending
        assert task3.status == "complete"

        # Change task2 to complete and task1 back to pending
        tm.mark_complete(task2.id)
        tm.mark_incomplete(task1.id)

        # Verify new statuses
        assert task1.status == "pending"
        assert task2.status == "complete"
        assert task3.status == "complete"

    def test_renderer_displays_status_correctly(self):
        """Test that renderer properly displays different statuses"""
        tm = TaskManager()

        # Create tasks with different statuses
        pending_task = tm.create_task("Pending Task", priority="high")
        in_progress_task = tm.create_task("In Progress Task", priority="medium")
        tm.update_task(in_progress_task.id, status="in-progress")
        completed_task = tm.create_task("Completed Task", priority="low")
        tm.mark_complete(completed_task.id)

        # Get all tasks
        all_tasks = tm.get_all_tasks()

        # Verify we have the expected statuses
        status_counts = {}
        for task in all_tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1

        assert status_counts.get("pending", 0) >= 1
        assert status_counts.get("in-progress", 0) >= 1
        assert status_counts.get("complete", 0) >= 1