from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .base import Base
import uuid

class ThreadItemBase(SQLModel):
    """Base class for ThreadItem with common fields."""
    user_id: str = Field(index=True)  # User ID from JWT token verification
    thread_id: str = Field(foreign_key="threads.id", index=True)
    role: str = Field(max_length=20)  # "user", "assistant", "system"
    content: str = Field(max_length=10000)  # Content of the thread item
    item_type: Optional[str] = Field(default="text", max_length=20)  # "text", "command", "response", "error"


class ThreadItem(ThreadItemBase, Base, table=True):
    """ThreadItem model with all required fields and relationships."""
    __tablename__ = "thread_items"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

    # Relationships
    thread: "Thread" = Relationship(back_populates="thread_items", sa_relationship_kwargs={"lazy": "select"})


class ThreadItemCreate(SQLModel):
    """Schema for creating a new thread item."""
    user_id: str
    thread_id: str
    role: str = Field(max_length=20)  # "user", "assistant", "system"
    content: str = Field(max_length=10000)
    item_type: Optional[str] = Field(default="text", max_length=20)


class ThreadItemRead(ThreadItemBase):
    """Schema for reading a thread item with its ID."""
    id: str
    timestamp: datetime


class ThreadItemUpdate(SQLModel):
    """Schema for updating a thread item."""
    content: Optional[str] = Field(default=None, max_length=10000)
    item_type: Optional[str] = Field(default=None, max_length=20)
    