"""SQLModel models for Reminder Service."""
from sqlmodel import SQLModel, Field, Column
from typing import Optional
import sqlalchemy.dialects.postgresql as pg


class ReminderBase(SQLModel):
    """Base model for reminders."""
    reminder_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    task_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    user_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    reminder_time: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    reminder_type: str = Field(sa_column=Column(pg.VARCHAR(50), default="in_app"))  # in_app, email, push, sms
    message: str = Field(sa_column=Column(pg.TEXT, nullable=True))
    status: str = Field(sa_column=Column(pg.VARCHAR(50), default="scheduled"))  # scheduled, sent, cancelled
    created_at: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    scheduled_job_id: Optional[str] = Field(sa_column=Column(pg.VARCHAR(255), nullable=True))


class Reminder(ReminderBase, table=True):
    """Reminder model with table configuration."""
    __tablename__: str = "reminder"

    id: Optional[int] = Field(default=None, primary_key=True)
