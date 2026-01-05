"""create tasks table

Revision ID: 90fec3fe8659
Revises:
Create Date: 2025-12-14 01:39:43.750843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '90fec3fe8659'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create tasks table with RLS policies."""
    op.create_table(
        'tasks',
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('completed', sa.Boolean, nullable=False, default=False),
        sa.Column('user_id', sa.String, nullable=False),
        sa.Column('id', sa.Integer, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True)
    )
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)

    # Enable Row Level Security
    op.execute("ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;")

    # Create RLS policy: users can only access their own tasks
    # For production with JWT, we'll use a function to extract user_id from JWT
    # In Neon DB, you can access JWT claims through current_setting if configured properly
    op.execute("CREATE POLICY tasks_user_isolation ON tasks FOR ALL USING (user_id = (current_setting('app.current_user_id', true))::text);")

    # This requires your application to set the current_user_id setting before each query
    # Example in your app: SET app.current_user_id = 'user123';
    # This can be done automatically by your connection pool or middleware


def downgrade() -> None:
    """Downgrade schema - drop RLS policies and tasks table."""
    # Drop the policy first
    op.execute("DROP POLICY IF EXISTS tasks_user_isolation ON tasks;")

    # Disable Row Level Security
    op.execute("ALTER TABLE tasks DISABLE ROW LEVEL SECURITY;")

    # Drop the index and table
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_table('tasks')
