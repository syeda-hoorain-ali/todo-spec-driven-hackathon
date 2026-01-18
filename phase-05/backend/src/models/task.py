from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from .base import Base


class TaskBase(SQLModel):
    """Base class for Task with common fields."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)  # User ID from JWT token verification
    # Category and priority fields
    category: Optional[str] = Field(default="other", max_length=50)  # Category: work, personal, health, etc.
    priority: Optional[str] = Field(default="medium", max_length=20)  # Priority: low, medium, high, urgent
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)  # daily, weekly, monthly, yearly
    recurrence_interval: Optional[int] = Field(default=None)  # How often to repeat (e.g., every 2 weeks)
    next_occurrence: Optional[datetime] = None  # When the next occurrence is due
    recurrence_end_date: Optional[datetime] = Field(default=None)  # When recurrence ends
    max_occurrences: Optional[int] = Field(default=None)  # Max number of occurrences
    # Timestamps - required for all tasks
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                 sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})



class Task(TaskBase, Base, table=True):
    """Task model with all required fields and relationships per data model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)


    # Relationships can be defined here if needed
    # For example, if we have a User model:
    # user: "User" = Relationship(back_populates="tasks")


class TaskCreate(SQLModel):
    """Schema for creating a new task with title (required) and description (optional)."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)  # Whether the task is completed
    # Category and priority fields
    category: Optional[str] = Field(default="other", max_length=50)  # Category: work, personal, health, etc.
    priority: Optional[str] = Field(default="medium", max_length=20)  # Priority: low, medium, high, urgent
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)  # daily, weekly, monthly, yearly
    recurrence_interval: Optional[int] = Field(default=None)  # How often to repeat (e.g., every 2 weeks)
    next_occurrence: Optional[datetime] = None  # When the next occurrence is due
    recurrence_end_date: Optional[datetime] = Field(default=None)  # When recurrence ends
    max_occurrences: Optional[int] = Field(default=None)  # Max number of occurrences


class TaskRead(TaskBase):
    """Schema for reading a task with its ID."""
    id: int


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    # Category and priority fields
    category: Optional[str] = Field(default=None, max_length=50)  # Category: work, personal, health, etc.
    priority: Optional[str] = Field(default=None, max_length=20)  # Priority: low, medium, high, urgent
    # Due date and reminder fields
    due_date: Optional[datetime] = None  # When the task is due
    reminder_time: Optional[datetime] = None  # When to send a reminder
    # Recurrence fields
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = Field(default=None, max_length=50)  # daily, weekly, monthly, yearly
    recurrence_interval: Optional[int] = None  # How often to repeat (e.g., every 2 weeks)
    next_occurrence: Optional[datetime] = None  # When the next occurrence is due
    recurrence_end_date: Optional[datetime] = Field(default=None)  # When recurrence ends
    max_occurrences: Optional[int] = None  # Max number of occurrences
    