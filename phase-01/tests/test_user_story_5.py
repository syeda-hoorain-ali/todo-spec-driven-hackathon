"""
Tests for User Story 5 - Search and Filter Tasks

As a user, I want to search and filter my tasks by keyword, status, or priority
so that I can quickly find relevant tasks.

Test Criteria:
- Can search tasks by keyword in title or description
- Can filter tasks by status
- Can filter tasks by priority
- Only matching tasks are displayed
"""
import pytest
from datetime import datetime
from todo_app.models.task import Task
from todo_app.managers.task_manager import TaskManager


class TestUserStory5:
    """Test cases for User Story 5 - Search and Filter Tasks"""

    def test_search_tasks_by_keyword_in_title(self):
        """T060, T070: Test searching tasks by keyword in title"""
        tm = TaskManager()

        # Create tasks with different titles
        task1 = tm.create_task("Buy groceries", description="Get milk and bread")
        task2 = tm.create_task("Complete project", description="Finish the todo app")
        task3 = tm.create_task("Call mom", description="Check on her health")

        # Search for tasks containing "project"
        results = tm.search_tasks("project")
        assert len(results) == 1
        assert results[0].id == task2.id
        assert "project" in results[0].title.lower()

        # Search for tasks containing "groceries"
        results = tm.search_tasks("groceries")
        assert len(results) == 1
        assert results[0].id == task1.id
        assert "groceries" in results[0].title.lower()

    def test_search_tasks_by_keyword_in_description(self):
        """T060, T070: Test searching tasks by keyword in description"""
        tm = TaskManager()

        # Create tasks with different descriptions
        task1 = tm.create_task("Task 1", description="This is about groceries")
        task2 = tm.create_task("Task 2", description="This is about projects")
        task3 = tm.create_task("Task 3", description="This is about family")

        # Search for tasks containing "groceries" in description
        results = tm.search_tasks("groceries")
        assert len(results) == 1
        assert results[0].id == task1.id
        assert "groceries" in results[0].description.lower()

    def test_search_case_insensitive(self):
        """T060, T070: Test that search is case insensitive"""
        tm = TaskManager()

        # Create a task
        task = tm.create_task("GROCERIES", description="buy milk and bread")

        # Search with different cases
        results1 = tm.search_tasks("groceries")
        results2 = tm.search_tasks("GROCERIES")
        results3 = tm.search_tasks("Groceries")

        # All should find the task
        assert len(results1) == 1
        assert len(results2) == 1
        assert len(results3) == 1
        assert results1[0].id == task.id
        assert results2[0].id == task.id
        assert results3[0].id == task.id

    def test_filter_tasks_by_status(self):
        """T061, T070: Test filtering tasks by status"""
        tm = TaskManager()

        # Create tasks with different statuses
        pending_task = tm.create_task("Pending task")
        in_progress_task = tm.create_task("In-progress task")
        tm.update_task(in_progress_task.id, status="in-progress")
        completed_task = tm.create_task("Completed task")
        tm.mark_complete(completed_task.id)

        # Filter by pending status
        pending_results = tm.filter_tasks(status="pending")
        pending_ids = [t.id for t in pending_results]
        assert len(pending_results) == 1
        assert pending_task.id in pending_ids
        assert in_progress_task.id not in pending_ids
        assert completed_task.id not in pending_ids

        # Filter by in-progress status
        in_progress_results = tm.filter_tasks(status="in-progress")
        in_progress_ids = [t.id for t in in_progress_results]
        assert len(in_progress_results) == 1
        assert in_progress_task.id in in_progress_ids
        assert pending_task.id not in in_progress_ids
        assert completed_task.id not in in_progress_ids

        # Filter by complete status
        completed_results = tm.filter_tasks(status="complete")
        completed_ids = [t.id for t in completed_results]
        assert len(completed_results) == 1
        assert completed_task.id in completed_ids
        assert pending_task.id not in completed_ids
        assert in_progress_task.id not in completed_ids

    def test_filter_tasks_by_priority(self):
        """T061, T070: Test filtering tasks by priority"""
        tm = TaskManager()

        # Create tasks with different priorities
        low_task = tm.create_task("Low priority task", priority="low")
        medium_task = tm.create_task("Medium priority task", priority="medium")
        high_task = tm.create_task("High priority task", priority="high")

        # Filter by low priority
        low_results = tm.filter_tasks(priority="low")
        low_ids = [t.id for t in low_results]
        assert len(low_results) == 1
        assert low_task.id in low_ids

        # Filter by medium priority
        medium_results = tm.filter_tasks(priority="medium")
        medium_ids = [t.id for t in medium_results]
        assert len(medium_results) == 1
        assert medium_task.id in medium_ids

        # Filter by high priority
        high_results = tm.filter_tasks(priority="high")
        high_ids = [t.id for t in high_results]
        assert len(high_results) == 1
        assert high_task.id in high_ids

    def test_combined_filtering_by_status_and_priority(self):
        """Test filtering by both status and priority"""
        tm = TaskManager()

        # Create tasks with different combinations
        task1 = tm.create_task("High priority pending task", priority="high")
        task2 = tm.create_task("High priority in-progress task", priority="high")
        tm.update_task(task2.id, status="in-progress")
        task3 = tm.create_task("Low priority pending task", priority="low")
        task4 = tm.create_task("Low priority complete task", priority="low")
        tm.mark_complete(task4.id)

        # Filter for high priority AND pending status
        results = tm.filter_tasks(status="pending", priority="high")
        result_ids = [t.id for t in results]
        assert len(results) == 1
        assert task1.id in result_ids
        assert task2.id not in result_ids
        assert task3.id not in result_ids
        assert task4.id not in result_ids

        # Filter for low priority AND complete status
        results = tm.filter_tasks(status="complete", priority="low")
        result_ids = [t.id for t in results]
        assert len(results) == 1
        assert task4.id in result_ids
        assert task1.id not in result_ids

    def test_search_and_filter_combined(self):
        """Test that search and filter can work together conceptually"""
        tm = TaskManager()

        # Create tasks
        task1 = tm.create_task("Urgent groceries", description="buy milk", priority="high", status="pending")
        task2 = tm.create_task("Regular groceries", description="buy bread", priority="medium", status="in-progress")
        task3 = tm.create_task("Non-grocery task", description="work project", priority="low", status="pending")

        # Get all tasks and manually filter for those containing "groceries" with high priority
        all_tasks = tm.get_all_tasks()
        groceries_high_priority = [
            t for t in all_tasks
            if "groceries" in t.title.lower() and t.priority == "high"
        ]

        assert len(groceries_high_priority) == 1
        assert groceries_high_priority[0].id == task1.id

    def test_sort_tasks_by_date(self):
        """T067, T070: Test sorting tasks by date"""
        tm = TaskManager()

        # Create tasks (they'll have sequential creation times)
        task1 = tm.create_task("First task")
        task2 = tm.create_task("Second task")
        task3 = tm.create_task("Third task")

        # Sort by date (default is ascending - oldest first)
        all_tasks = tm.get_all_tasks()
        sorted_tasks = tm.sort_tasks(all_tasks, "date")

        # Verify order is oldest to newest
        assert sorted_tasks[0].id == task1.id
        assert sorted_tasks[1].id == task2.id
        assert sorted_tasks[2].id == task3.id

        # Sort by date in reverse (newest first)
        sorted_tasks_reverse = tm.sort_tasks(all_tasks, "date", reverse=True)
        assert sorted_tasks_reverse[0].id == task3.id
        assert sorted_tasks_reverse[1].id == task2.id
        assert sorted_tasks_reverse[2].id == task1.id

    def test_sort_tasks_by_priority(self):
        """T067, T070: Test sorting tasks by priority"""
        tm = TaskManager()

        # Create tasks with different priorities
        low_task = tm.create_task("Low task", priority="low")
        high_task = tm.create_task("High task", priority="high")
        medium_task = tm.create_task("Medium task", priority="medium")

        # Sort by priority (high to low by default)
        all_tasks = tm.get_all_tasks()
        sorted_tasks = tm.sort_tasks(all_tasks, "priority")

        # Priority order should be high (3), medium (2), low (1)
        assert sorted_tasks[0].id == high_task.id  # high priority first
        assert sorted_tasks[1].id == medium_task.id  # medium priority second
        assert sorted_tasks[2].id == low_task.id  # low priority last

        # Sort by priority in reverse (low to high)
        sorted_tasks_reverse = tm.sort_tasks(all_tasks, "priority", reverse=True)
        assert sorted_tasks_reverse[0].id == low_task.id  # low priority first
        assert sorted_tasks_reverse[1].id == medium_task.id  # medium priority second
        assert sorted_tasks_reverse[2].id == high_task.id  # high priority last

    def test_sort_tasks_by_title(self):
        """T067, T070: Test sorting tasks by title"""
        tm = TaskManager()

        # Create tasks with titles that have a clear alphabetical order
        task_c = tm.create_task("Zebra task")
        task_a = tm.create_task("Apple task")
        task_b = tm.create_task("Banana task")

        # Sort by title (A to Z)
        all_tasks = tm.get_all_tasks()
        sorted_tasks = tm.sort_tasks(all_tasks, "title")

        assert sorted_tasks[0].id == task_a.id  # Apple first
        assert sorted_tasks[1].id == task_b.id  # Banana second
        assert sorted_tasks[2].id == task_c.id  # Zebra last

        # Sort by title in reverse (Z to A)
        sorted_tasks_reverse = tm.sort_tasks(all_tasks, "title", reverse=True)
        assert sorted_tasks_reverse[0].id == task_c.id  # Zebra first
        assert sorted_tasks_reverse[1].id == task_b.id  # Banana second
        assert sorted_tasks_reverse[2].id == task_a.id  # Apple last

    def test_sort_tasks_by_status(self):
        """T067, T070: Test sorting tasks by status"""
        tm = TaskManager()

        # Create tasks with different statuses
        completed_task = tm.create_task("Completed task")
        tm.mark_complete(completed_task.id)
        pending_task = tm.create_task("Pending task")
        in_progress_task = tm.create_task("In-progress task")
        tm.update_task(in_progress_task.id, status="in-progress")

        # Sort by status (complete to pending by default: complete=3, in-progress=2, pending=1)
        all_tasks = tm.get_all_tasks()
        sorted_tasks = tm.sort_tasks(all_tasks, "status")

        # Should be: completed, in-progress, pending
        assert sorted_tasks[0].id == completed_task.id  # complete first
        assert sorted_tasks[1].id == in_progress_task.id  # in-progress second
        assert sorted_tasks[2].id == pending_task.id  # pending last

        # Sort by status in reverse
        sorted_tasks_reverse = tm.sort_tasks(all_tasks, "status", reverse=True)
        assert sorted_tasks_reverse[0].id == pending_task.id  # pending first
        assert sorted_tasks_reverse[1].id == in_progress_task.id  # in-progress second
        assert sorted_tasks_reverse[2].id == completed_task.id  # complete last

    def test_empty_search_results(self):
        """T060, T070: Test search with no matching results"""
        tm = TaskManager()

        # Create some tasks
        tm.create_task("Task 1", description="Description 1")
        tm.create_task("Task 2", description="Description 2")

        # Search for something that doesn't exist
        results = tm.search_tasks("nonexistentkeyword")
        assert len(results) == 0

    def test_empty_filter_results(self):
        """T061, T070: Test filter with no matching results"""
        tm = TaskManager()

        # Create a pending task
        tm.create_task("Pending task", priority="high")

        # Filter for completed tasks when none exist
        results = tm.filter_tasks(status="complete")
        assert len(results) == 0

        # Filter for low priority tasks when none exist
        results = tm.filter_tasks(priority="low")
        assert len(results) == 0