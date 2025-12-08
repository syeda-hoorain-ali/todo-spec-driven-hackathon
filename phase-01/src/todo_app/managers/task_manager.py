"""
Task Manager for the todo application.

This module handles all task operations including CRUD operations,
searching, filtering, and validation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from todo_app.models.task import Task


class TaskManager:
    """
    Manages all task operations including creation, retrieval, updates, and deletion.
    Uses in-memory storage with dictionary for O(1) access.
    """

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def create_task(
        self,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        recurrence_pattern: str = "none"
    ) -> Task:
        """Create a new task with auto-generated ID."""
        task_id = self._next_id
        self._next_id += 1

        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            tags=tags,
            recurrence_pattern=recurrence_pattern
        )

        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    def update_task(self, task_id: int, **updates) -> Optional[Task]:
        """Update properties of an existing task."""
        task = self.get_task(task_id)
        if not task:
            return None

        # Validate updates before applying them
        if 'title' in updates:
            task.title = task._validate_title(updates['title'])
        if 'description' in updates:
            task.description = task._validate_description(updates['description'])
        if 'status' in updates:
            task.status = task._validate_status(updates['status'])
        if 'priority' in updates:
            task.priority = task._validate_priority(updates['priority'])
        if 'due_date' in updates:
            task.due_date = updates['due_date']
        if 'tags' in updates:
            task.tags = task.validate_tags(updates['tags'])
        if 'recurrence_pattern' in updates:
            task.recurrence_pattern = task._validate_recurrence_pattern(updates['recurrence_pattern'])

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks by keyword in title or description."""
        keyword_lower = keyword.lower()
        matching_tasks = []

        for task in self._tasks.values():
            if (keyword_lower in task.title.lower() or
                keyword_lower in task.description.lower()):
                matching_tasks.append(task)

        return matching_tasks

    def filter_tasks(self, **filters) -> List[Task]:
        """Filter tasks by various criteria."""
        filtered_tasks = list(self._tasks.values())

        if 'status' in filters and filters['status']:
            filtered_tasks = [task for task in filtered_tasks if task.status == filters['status']]

        if 'priority' in filters and filters['priority']:
            filtered_tasks = [task for task in filtered_tasks if task.priority == filters['priority']]

        if 'tags' in filters and filters['tags']:
            # Filter tasks that contain any of the specified tags
            tag_set = set(filters['tags'])
            filtered_tasks = [
                task for task in filtered_tasks
                if bool(tag_set & set(task.tags))
            ]

        return filtered_tasks

    def mark_complete(self, task_id: int) -> Optional[Task]:
        """Mark a task as complete."""
        task = self.get_task(task_id)
        if task:
            task.update_status("complete")
            return task
        return None

    def mark_incomplete(self, task_id: int) -> Optional[Task]:
        """Mark a task as incomplete (pending)."""
        task = self.get_task(task_id)
        if task:
            task.update_status("pending")
            return task
        return None

    def sort_tasks(self, tasks: List[Task], sort_by: str = "date", reverse: bool = False) -> List[Task]:
        """Sort tasks by various criteria."""
        if sort_by == "date":
            # Sort by creation date, with ID as tie-breaker for tasks created at the same time
            return sorted(tasks, key=lambda t: (t.created_date, t.id), reverse=reverse)
        elif sort_by == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            # For priority, default is high to low (reverse=True)
            actual_reverse = not reverse if reverse is False else reverse
            # Actually, let me just use the reverse parameter as-is, but change the logic to sort high priority first by default
            # The test expects high priority first when no reverse is specified, meaning reverse=True for priority
            # Actually, let me check: if reverse=True, it sorts in descending order
            # For priority, we want high first, which means descending order -> reverse=True
            # But the user can override with the reverse flag
            # So if user passes reverse=False, we want ascending (low, medium, high)
            # If user passes reverse=True, we want descending (high, medium, low)
            # Actually, looking at the test again: sort_tasks is called with default reverse=False
            # But test expects high priority first, which means descending order -> reverse=True should be used internally
            # This means we need to invert the reverse flag for priority and status sorting
            return sorted(tasks, key=lambda t: (priority_order[t.priority], t.id), reverse=not reverse)
        elif sort_by == "title":
            return sorted(tasks, key=lambda t: (t.title.lower(), t.id), reverse=reverse)
        elif sort_by == "due_date":
            # Sort by due date, with tasks without due dates at the end, ID as tie-breaker
            return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date, t.id), reverse=reverse)
        elif sort_by == "status":
            status_order = {"complete": 3, "in-progress": 2, "pending": 1}
            # For status, complete first, then in-progress, then pending -> descending order
            return sorted(tasks, key=lambda t: (status_order[t.status], t.id), reverse=not reverse)
        else:
            # Default to date sorting with ID tie-breaker
            return sorted(tasks, key=lambda t: (t.created_date, t.id), reverse=reverse)