from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, UTC


class TaskBase(SQLModel):
    """
    Base model for Task with common fields.
    """
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    user_id: str = Field(min_length=1, max_length=255)  # ID of the user who owns this task
    completed: bool = Field(default=False)
    category: Optional[str] = Field(default="other", max_length=50)
    priority: Optional[str] = Field(default="medium", max_length=20)
    due_date: Optional[datetime] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)
    recurrence_interval: Optional[int] = Field(default=None, ge=1)  # Must be positive if provided
    next_occurrence: Optional[datetime] = Field(default=None)
    recurrence_end_date: Optional[datetime] = Field(default=None)
    max_occurrences: Optional[int] = Field(default=None, ge=1)  # Must be positive if provided


class Task(TaskBase, table=True):
    """
    Task model representing a user's todo item with comprehensive attributes for task management.
    """
    __tablename__ = "tasks"  # Use the same table as the backend with RLS policies

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)})


class AddTaskRequest(TaskBase):
    """
    Request model for adding a new task.
    """
    pass  # All fields inherited from TaskBase are required for add_task


class UpdateTaskRequest(SQLModel):
    """
    Request model for updating a task.
    All fields are optional to allow partial updates.
    """
    user_id: str = Field(min_length=1, max_length=255)
    task_id: int
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = Field(default=None)
    reminder_time: Optional[datetime] = Field(default=None)
    is_recurring: Optional[bool] = Field(default=None)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)
    recurrence_interval: Optional[int] = Field(default=None, ge=1)
    next_occurrence: Optional[datetime] = Field(default=None)
    recurrence_end_date: Optional[datetime] = Field(default=None)
    max_occurrences: Optional[int] = Field(default=None, ge=1)


class ListTasksRequest(SQLModel):
    """
    Request model for listing tasks with filtering options.
    """
    user_id: str = Field(min_length=1, max_length=255)
    status: Optional[str] = Field(default=None, regex="^(all|pending|completed)$")
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high)$")
    category: Optional[str] = Field(default=None, max_length=50)
    search: Optional[str] = Field(default=None, max_length=255)
    sort_by: Optional[str] = Field(default=None, regex="^(due_date|priority|title|created_at)$")
    sort_order: Optional[str] = Field(default="asc", regex="^(asc|desc)$")


class CompleteTaskRequest(SQLModel):
    """
    Request model for completing a task.
    """
    user_id: str = Field(min_length=1, max_length=255)
    task_id: int


class DeleteTaskRequest(SQLModel):
    """
    Request model for deleting a task.
    """
    user_id: str = Field(min_length=1, max_length=255)
    task_id: int
