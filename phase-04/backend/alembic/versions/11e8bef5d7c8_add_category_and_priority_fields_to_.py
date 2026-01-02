"""add category and priority fields to tasks table

Revision ID: 11e8bef5d7c8
Revises: 910fed40876a
Create Date: 2025-12-14 23:36:21.212100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '11e8bef5d7c8'
down_revision: Union[str, Sequence[str], None] = '910fed40876a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add category and priority fields to tasks table."""
    # Add category and priority columns to the existing tasks table
    op.add_column('tasks', sa.Column('category', sa.String(50), nullable=True, default="other"))
    op.add_column('tasks', sa.Column('priority', sa.String(20), nullable=True, default="medium"))

    # Update existing rows with default values
    op.execute("UPDATE tasks SET category = 'other' WHERE category IS NULL")
    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")

    # Now make the columns non-nullable
    op.alter_column('tasks', 'category', nullable=False)
    op.alter_column('tasks', 'priority', nullable=False)


def downgrade() -> None:
    """Downgrade schema - remove category and priority fields from tasks table."""
    # Remove category and priority columns from the tasks table
    op.drop_column('tasks', 'priority')
    op.drop_column('tasks', 'category')
