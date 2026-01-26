"""SQLModel models for Notification Service."""
from sqlmodel import SQLModel, Field, Column
from typing import Optional
import sqlalchemy.dialects.postgresql as pg


class NotificationBase(SQLModel):
    """Base model for notifications."""
    notification_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    user_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    notification_type: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False))
    content: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    status: str = Field(sa_column=Column(pg.VARCHAR(50), default="pending"))  # pending, sent, failed
    priority: str = Field(sa_column=Column(pg.VARCHAR(20), default="normal"))  # low, normal, high
    channel: str = Field(sa_column=Column(pg.VARCHAR(50), default="in_app"))  # in_app, email, push, sms
    related_entity_id: Optional[str] = Field(sa_column=Column(pg.VARCHAR(255), nullable=True))
    timestamp: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))


class Notification(NotificationBase, table=True):
    """Notification model with table configuration."""
    __tablename__: str = "notification"

    id: Optional[int] = Field(default=None, primary_key=True)


class NotificationChannelPreferencesBase(SQLModel):
    """Base model for notification channel preferences."""
    user_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    channel: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False))  # in_app, email, push, sms
    enabled: bool = Field(default=True)
    email_address: Optional[str] = Field(sa_column=Column(pg.VARCHAR(255), nullable=True))
    device_token: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    phone_number: Optional[str] = Field(sa_column=Column(pg.VARCHAR(20), nullable=True))  # For SMS notifications


class NotificationChannelPreferences(NotificationChannelPreferencesBase, table=True):
    """Notification channel preferences model with table configuration."""
    __tablename__: str = "notification_channel_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
