"""SQLModel models for Audit Service."""
from sqlmodel import SQLModel, Field, Column
from typing import Optional
import sqlalchemy.dialects.postgresql as pg


class AuditLogBase(SQLModel):
    """Base model for audit logs."""
    event_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    event_type: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    user_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    entity_type: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    entity_id: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    operation: str = Field(sa_column=Column(pg.VARCHAR(50), nullable=False))
    timestamp: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    details: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    source: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))


class AuditLog(AuditLogBase, table=True):
    """Audit log model with table configuration."""
    __tablename__: str = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)


class DeadLetterQueueBase(SQLModel):
    """Base model for dead letter queue."""
    topic: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    partition: int = Field(nullable=False)
    offset_value: int = Field(nullable=False)
    key_val: Optional[str] = Field(sa_column=Column(pg.VARCHAR(255), nullable=True))
    value: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    error_message: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True))
    timestamp: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False))
    processed: bool = Field(default=False)


class DeadLetterQueue(DeadLetterQueueBase, table=True):
    """Dead letter queue model with table configuration."""
    __tablename__: str = "dead_letter_queue"

    id: Optional[int] = Field(default=None, primary_key=True)
