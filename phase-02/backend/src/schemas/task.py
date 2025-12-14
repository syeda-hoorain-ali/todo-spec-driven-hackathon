from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateTaskRequest(BaseModel):
    """Schema for creating a new task with title (required) and description (optional)."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder


class UpdateTaskRequest(BaseModel):
    """Schema for updating a task with optional title and description."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder


class TaskResponse(BaseModel):
    """Schema for task response with all required fields."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: str
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Schema for task list response with tasks array and count."""
    tasks: list[TaskResponse]
    count: int


class SearchFilterRequest(BaseModel):
    """Schema for search and filter parameters."""
    keyword: Optional[str] = None
    status: Optional[bool] = None  # completed status
    priority: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None