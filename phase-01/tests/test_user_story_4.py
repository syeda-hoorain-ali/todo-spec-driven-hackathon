"""
Tests for User Story 4 - Update Task Details

As a user, I want to modify existing tasks so that I can keep my todo list
accurate as my plans change.

Test Criteria:
- Can update task title and description
- Can update task priority
- Can update task due date
- Changes are reflected in the task list
"""
import pytest
from datetime import datetime
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager


class TestUserStory4:
    """Test cases for User Story 4 - Update Task Details"""

    def test_update_task_title_and_description(self):
        """T050, T055: Test updating task title and description"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Original Title", description="Original Description")

        # Update title and description
        updated_task = tm.update_task(task.id, title="New Title", description="New Description")

        # Verify updates
        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"

        # Verify the changes are reflected when getting the task again
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.title == "New Title"
        assert retrieved_task.description == "New Description"

    def test_update_task_priority(self):
        """T052, T055: Test updating task priority"""
        tm = TaskManager()

        # Create a task with default priority
        task = tm.create_task("Test Task")

        # Verify initial priority
        assert task.priority == "medium"

        # Update priority
        updated_task = tm.update_task(task.id, priority="high")

        # Verify priority change
        assert updated_task is not None
        assert updated_task.priority == "high"

        # Verify the change is persistent
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.priority == "high"

    def test_update_task_due_date(self):
        """T053, T055: Test updating task due date"""
        tm = TaskManager()
        test_date = datetime(2025, 12, 31)

        # Create a task without due date
        task = tm.create_task("Test Task")

        # Verify initial due date is None
        assert task.due_date is None

        # Update due date
        updated_task = tm.update_task(task.id, due_date=test_date)

        # Verify due date change
        assert updated_task is not None
        assert updated_task.due_date == test_date

        # Verify the change is persistent
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.due_date == test_date

    def test_update_multiple_fields_at_once(self):
        """Test updating multiple fields simultaneously"""
        tm = TaskManager()
        test_date = datetime(2025, 12, 25)

        # Create a task
        task = tm.create_task("Original Title", description="Original Description", priority="low")

        # Update multiple fields
        updated_task = tm.update_task(
            task.id,
            title="Updated Title",
            description="Updated Description",
            priority="high",
            due_date=test_date
        )

        # Verify all updates
        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == "high"
        assert updated_task.due_date == test_date

    def test_update_nonexistent_task(self):
        """T057: Handle error case when trying to update non-existent task"""
        tm = TaskManager()

        # Try to update a non-existent task
        result = tm.update_task(999, title="New Title")

        # Should return None
        assert result is None

    def test_update_validation_constraints(self):
        """T056: Validate updates against Task entity constraints"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Valid Task", description="Valid Description")

        # Test title validation
        with pytest.raises(ValueError, match="Title cannot exceed 200 characters"):
            tm.update_task(task.id, title="x" * 201)

        # Test description validation
        with pytest.raises(ValueError, match="Description cannot exceed 1000 characters"):
            tm.update_task(task.id, description="x" * 1001)

        # Test priority validation
        with pytest.raises(ValueError, match="Priority must be one of: low, medium, high"):
            tm.update_task(task.id, priority="invalid_priority")

        # Test status validation
        with pytest.raises(ValueError, match="Status must be one of: pending, in-progress, complete"):
            tm.update_task(task.id, status="invalid_status")

        # Verify task remains unchanged after failed validations
        unchanged_task = tm.get_task(task.id)
        assert unchanged_task.title == "Valid Task"
        assert unchanged_task.description == "Valid Description"
        assert unchanged_task.priority == "medium"
        assert unchanged_task.status == "pending"

    def test_update_partial_fields(self):
        """Test updating only some fields, leaving others unchanged"""
        tm = TaskManager()
        test_date = datetime(2025, 12, 20)

        # Create a task with specific values
        task = tm.create_task("Original Title", description="Original Description", priority="low", status="in-progress")

        # Update only the title
        updated_task = tm.update_task(task.id, title="New Title")

        # Verify only title changed, others remain the same
        assert updated_task.title == "New Title"
        assert updated_task.description == "Original Description"
        assert updated_task.priority == "low"
        assert updated_task.status == "in-progress"

        # Update only the priority
        updated_task2 = tm.update_task(task.id, priority="high")
        assert updated_task2.title == "New Title"  # Should still be the updated title
        assert updated_task2.priority == "high"
        assert updated_task2.status == "in-progress"

    def test_update_task_status(self):
        """Test updating task status"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Test Task")

        # Verify initial status
        assert task.status == "pending"

        # Update status to in-progress
        updated_task = tm.update_task(task.id, status="in-progress")
        assert updated_task.status == "in-progress"

        # Update status to complete
        updated_task2 = tm.update_task(task.id, status="complete")
        assert updated_task2.status == "complete"

    def test_update_with_empty_title(self):
        """Test validation when updating to empty title"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("Valid Title")

        # Try to update to empty title
        with pytest.raises(ValueError, match="Title cannot be empty"):
            tm.update_task(task.id, title="")

        # Try to update to whitespace-only title
        with pytest.raises(ValueError, match="Title cannot be empty"):
            tm.update_task(task.id, title="   ")

        # Task should remain unchanged
        unchanged_task = tm.get_task(task.id)
        assert unchanged_task.title == "Valid Title"