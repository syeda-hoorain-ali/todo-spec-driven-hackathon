"""rename end_date column to recurrence_end_date

Revision ID: 27fb9ff82798
Revises: 11e8bef5d7c8
Create Date: 2025-12-14 02:36:02.574980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27fb9ff82798'
down_revision: Union[str, Sequence[str], None] = '11e8bef5d7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - rename end_date column to recurrence_end_date."""
    # Rename the end_date column to recurrence_end_date
    op.alter_column('tasks', 'end_date', new_column_name='recurrence_end_date')


def downgrade() -> None:
    """Downgrade schema - rename recurrence_end_date column back to end_date."""
    # Rename the recurrence_end_date column back to end_date
    op.alter_column('tasks', 'recurrence_end_date', new_column_name='end_date')
