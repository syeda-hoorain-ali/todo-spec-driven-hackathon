"""add task fields

Revision ID: 910fed40876a
Revises: 90fec3fe8659
Create Date: 2025-12-14 07:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '910fed40876a'
down_revision: Union[str, Sequence[str], None] = '90fec3fe8659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add new fields to tasks table."""
    # Add due date and reminder fields
    op.add_column('tasks', sa.Column('due_date', sa.DateTime, nullable=True))
    op.add_column('tasks', sa.Column('reminder_time', sa.DateTime, nullable=True))

    # Add recurrence fields
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean, nullable=True, default=False))  # Allow null initially
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_interval', sa.Integer, nullable=True))
    op.add_column('tasks', sa.Column('next_occurrence', sa.DateTime, nullable=True))
    op.add_column('tasks', sa.Column('end_date', sa.DateTime, nullable=True))
    op.add_column('tasks', sa.Column('max_occurrences', sa.Integer, nullable=True))

    # Update existing rows to have False as default for is_recurring
    op.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")

    # Now make is_recurring non-nullable
    op.alter_column('tasks', 'is_recurring', nullable=False)


def downgrade() -> None:
    """Downgrade schema - remove new fields from tasks table."""
    # Remove recurrence fields
    op.drop_column('tasks', 'max_occurrences')
    op.drop_column('tasks', 'end_date')
    op.drop_column('tasks', 'next_occurrence')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')

    # Remove due date and reminder fields
    op.drop_column('tasks', 'reminder_time')
    op.drop_column('tasks', 'due_date')