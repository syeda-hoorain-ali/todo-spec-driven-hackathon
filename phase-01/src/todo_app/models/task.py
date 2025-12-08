"""
Task model for the todo application.

This module defines the Task entity with all its properties and validation methods.
"""
from datetime import datetime
from typing import List, Optional


class Task:
    """
    Represents a todo task with all its properties.

    Attributes:
        id: Unique identifier for the task
        title: Task title (required, max 200 chars)
        description: Task description (optional, max 1000 chars)
        status: Task status (pending, in-progress, complete)
        priority: Task priority (low, medium, high)
        created_date: Timestamp when task was created
        due_date: Optional due date for the task
        tags: List of tags for the task (max 10 tags, max 50 chars each)
        recurrence_pattern: Recurrence pattern (daily, weekly, monthly, none)
    """

    def __init__(
        self,
        id: int,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        created_date: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        recurrence_pattern: str = "none"
    ):
        self.id = id
        self.title = self._validate_title(title)
        self.description = self._validate_description(description)
        self.status = self._validate_status(status)
        self.priority = self._validate_priority(priority)
        self.created_date = created_date or datetime.now()
        self.due_date = due_date
        self.tags = self.validate_tags(tags or [])
        self.recurrence_pattern = self._validate_recurrence_pattern(recurrence_pattern)

    def _validate_title(self, title: str) -> str:
        """Validate the task title."""
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        title = title.strip()
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return title

    def _validate_description(self, description: str) -> str:
        """Validate the task description."""
        if len(description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return description

    def _validate_status(self, status: str) -> str:
        """Validate the task status."""
        valid_statuses = ["pending", "in-progress", "complete"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return status

    def _validate_priority(self, priority: str) -> str:
        """Validate the task priority."""
        valid_priorities = ["low", "medium", "high"]
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority

    def _validate_recurrence_pattern(self, pattern: str) -> str:
        """Validate the recurrence pattern."""
        valid_patterns = ["daily", "weekly", "monthly", "none"]
        if pattern not in valid_patterns:
            raise ValueError(f"Recurrence pattern must be one of: {', '.join(valid_patterns)}")
        return pattern

    def validate_tags(self, tags: List[str]) -> List[str]:
        """Validate the task tags."""
        if len(tags) > 10:
            raise ValueError("A task cannot have more than 10 tags")
        for tag in tags:
            if not tag or not tag.strip():
                raise ValueError("Tags cannot be empty")
            if len(tag.strip()) > 50:
                raise ValueError("Each tag cannot exceed 50 characters")
        return [tag.strip() for tag in tags]

    def update_status(self, new_status: str):
        """Update the task status with validation."""
        self.status = self._validate_status(new_status)

    def to_dict(self) -> dict:
        """Convert the task to a dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags,
            "recurrence_pattern": self.recurrence_pattern
        }