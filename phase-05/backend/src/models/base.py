from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime, func
from datetime import datetime
from typing import Optional


class Base(SQLModel):
    """Base model with common attributes for all models."""
    pass


class TimestampMixin:
    """Mixin class to add created_at and updated_at timestamps to models."""
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": func.now()}
    )