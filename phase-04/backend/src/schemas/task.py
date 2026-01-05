from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateTaskRequest(BaseModel):
    """Schema for creating a new task with title (required) and description (optional)."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    # Category and priority fields
    category: Optional[str] = Field(default="other", max_length=50, description="Task category: work, personal, health, etc.")
    priority: Optional[str] = Field(default="medium", max_length=20, description="Task priority: low, medium, high, urgent")
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: bool = Field(default=False, description="Whether the task is recurring")
    recurrence_pattern: Optional[str] = Field(None, max_length=50, description="Recurrence pattern: daily, weekly, monthly, yearly")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Recurrence interval (e.g., every 2 weeks)")
    recurrence_end_date: Optional[datetime] = None  # When recurrence ends
    max_occurrences: Optional[int] = Field(None, ge=1, description="Maximum number of occurrences")


class UpdateTaskRequest(BaseModel):
    """Schema for updating a task with optional title and description."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    completed: Optional[bool] = Field(None, description="Task completion status")
    # Category and priority fields
    category: Optional[str] = Field(None, max_length=50, description="Task category: work, personal, health, etc.")
    priority: Optional[str] = Field(None, max_length=20, description="Task priority: low, medium, high, urgent")
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: Optional[bool] = Field(None, description="Whether the task is recurring")
    recurrence_pattern: Optional[str] = Field(None, max_length=50, description="Recurrence pattern: daily, weekly, monthly, yearly")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Recurrence interval (e.g., every 2 weeks)")
    recurrence_end_date: Optional[datetime] = None  # When recurrence ends
    max_occurrences: Optional[int] = Field(None, ge=1, description="Maximum number of occurrences")


class TaskResponse(BaseModel):
    """Schema for task response with all required fields."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: str
    # Category and priority fields
    category: Optional[str] = "other"  # Category: work, personal, health, etc.
    priority: Optional[str] = "medium"  # Priority: low, medium, high, urgent
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly, yearly
    recurrence_interval: Optional[int] = None  # How often to repeat (e.g., every 2 weeks)
    next_occurrence: Optional[datetime] = None  # When the next occurrence is due
    recurrence_end_date: Optional[datetime] = None  # When recurrence ends
    max_occurrences: Optional[int] = None  # Max number of occurrences
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
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
