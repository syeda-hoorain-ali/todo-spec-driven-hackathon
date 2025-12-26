from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .base import Base
import uuid


class ThreadBase(SQLModel):
    """Base class for Thread with common fields."""
    title: Optional[str] = Field(default=None, max_length=255)
    user_id: str = Field(index=True)  # User ID from JWT token verification
    is_active: bool = Field(default=True)


class Thread(ThreadBase, Base, table=True):
    """Thread model with all required fields and relationships."""
    __tablename__ = "threads"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now(),
                                 sa_column_kwargs={"onupdate": datetime.now()})

    # Relationships
    thread_items: List["ThreadItem"] = Relationship(back_populates="thread", sa_relationship_kwargs={"lazy": "select"})


class ThreadCreate(SQLModel):
    """Schema for creating a new thread."""
    title: Optional[str] = Field(default=None, max_length=255)
    user_id: str
    is_active: bool = Field(default=True)


class ThreadRead(ThreadBase):
    """Schema for reading a thread with its ID."""
    id: str
    created_at: datetime
    updated_at: datetime
    item_count: Optional[int] = None  # Additional field for thread item count


class ThreadUpdate(SQLModel):
    """Schema for updating a thread."""
    title: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None
