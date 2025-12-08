"""
Tests for User Story 7 - Recurring Tasks and Due Dates

As a user, I want to set recurring tasks and due dates so that I can manage
time-sensitive and repetitive tasks effectively.

Test Criteria:
- Can set due date when creating a task
- Can set recurrence pattern when creating a task
- Due dates are displayed in the task list
- Recurring tasks are properly stored
"""
import pytest
from datetime import datetime
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager


class TestUserStory7:
    """Test cases for User Story 7 - Recurring Tasks and Due Dates"""

    def test_set_due_date_when_creating_task(self):
        """T081, T086: Test setting due date when creating a task"""
        tm = TaskManager()
        test_date = datetime(2025, 12, 31)

        # Create a task with a due date
        task = tm.create_task("Task with due date", due_date=test_date)

        # Verify due date is set correctly
        assert task.due_date == test_date

        # Create a task without due date (should default to None)
        task2 = tm.create_task("Task without due date")
        assert task2.due_date is None

    def test_set_recurrence_pattern_when_creating_task(self):
        """T080, T086: Test setting recurrence pattern when creating a task"""
        tm = TaskManager()

        # Create tasks with different recurrence patterns
        daily_task = tm.create_task("Daily task", recurrence_pattern="daily")
        weekly_task = tm.create_task("Weekly task", recurrence_pattern="weekly")
        monthly_task = tm.create_task("Monthly task", recurrence_pattern="monthly")
        none_task = tm.create_task("Non-recurring task", recurrence_pattern="none")

        # Verify recurrence patterns are set correctly
        assert daily_task.recurrence_pattern == "daily"
        assert weekly_task.recurrence_pattern == "weekly"
        assert monthly_task.recurrence_pattern == "monthly"
        assert none_task.recurrence_pattern == "none"

    def test_recurrence_pattern_validation(self):
        """T082: Test recurrence pattern validation"""
        tm = TaskManager()

        # Test invalid recurrence pattern
        with pytest.raises(ValueError, match="Recurrence pattern must be one of: daily, weekly, monthly, none"):
            tm.create_task("Task with invalid recurrence", recurrence_pattern="yearly")

        # Valid recurrence patterns should work
        valid_patterns = ["daily", "weekly", "monthly", "none"]
        for pattern in valid_patterns:
            task = tm.create_task(f"Task with {pattern} recurrence", recurrence_pattern=pattern)
            assert task.recurrence_pattern == pattern

    def test_update_task_due_date(self):
        """Test updating due date of existing task"""
        tm = TaskManager()
        test_date = datetime(2025, 12, 25)

        # Create a task without due date
        task = tm.create_task("Task to update")

        # Verify initial due date is None
        assert task.due_date is None

        # Update due date
        updated_task = tm.update_task(task.id, due_date=test_date)
        assert updated_task.due_date == test_date

        # Verify the change is persistent
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.due_date == test_date

    def test_update_task_recurrence_pattern(self):
        """Test updating recurrence pattern of existing task"""
        tm = TaskManager()

        # Create a task with default recurrence pattern
        task = tm.create_task("Task to update")

        # Verify initial recurrence pattern is "none"
        assert task.recurrence_pattern == "none"

        # Update recurrence pattern
        updated_task = tm.update_task(task.id, recurrence_pattern="weekly")
        assert updated_task.recurrence_pattern == "weekly"

        # Verify the change is persistent
        retrieved_task = tm.get_task(task.id)
        assert retrieved_task.recurrence_pattern == "weekly"

    def test_multiple_tasks_with_due_dates_and_recurrence(self):
        """Test multiple tasks with various due date and recurrence combinations"""
        tm = TaskManager()
        test_date = datetime(2025, 11, 30)

        # Create tasks with different combinations
        task1 = tm.create_task("Daily recurring task with due date",
                              due_date=test_date,
                              recurrence_pattern="daily")
        task2 = tm.create_task("Weekly recurring task without due date",
                              recurrence_pattern="weekly")
        task3 = tm.create_task("Non-recurring task with due date",
                              due_date=test_date,
                              recurrence_pattern="none")

        # Verify all properties are correctly set
        assert task1.due_date == test_date
        assert task1.recurrence_pattern == "daily"

        assert task2.due_date is None
        assert task2.recurrence_pattern == "weekly"

        assert task3.due_date == test_date
        assert task3.recurrence_pattern == "none"

    def test_update_task_with_due_date_and_recurrence_simultaneously(self):
        """Test updating both due date and recurrence at the same time"""
        tm = TaskManager()
        test_date = datetime(2025, 10, 15)

        # Create a task with initial values
        task = tm.create_task("Initial task",
                             due_date=datetime(2024, 1, 1),
                             recurrence_pattern="none")

        # Update both due date and recurrence pattern
        updated_task = tm.update_task(
            task.id,
            due_date=test_date,
            recurrence_pattern="monthly"
        )

        assert updated_task.due_date == test_date
        assert updated_task.recurrence_pattern == "monthly"

    def test_task_with_past_due_date(self):
        """Test creating a task with a past due date (should be allowed)"""
        tm = TaskManager()
        past_date = datetime(2020, 1, 1)  # Past date

        task = tm.create_task("Task with past due date", due_date=past_date)

        # Should accept past due dates
        assert task.due_date == past_date

    def test_task_with_future_due_date(self):
        """Test creating a task with a future due date"""
        tm = TaskManager()
        future_date = datetime(2030, 12, 31)  # Future date

        task = tm.create_task("Task with future due date", due_date=future_date)

        # Should accept future due dates
        assert task.due_date == future_date

    def test_task_with_same_due_date_multiple_tasks(self):
        """Test multiple tasks can have the same due date"""
        tm = TaskManager()
        shared_date = datetime(2025, 6, 15)

        task1 = tm.create_task("Task 1", due_date=shared_date)
        task2 = tm.create_task("Task 2", due_date=shared_date)
        task3 = tm.create_task("Task 3", due_date=shared_date)

        # All should have the same due date
        assert task1.due_date == shared_date
        assert task2.due_date == shared_date
        assert task3.due_date == shared_date