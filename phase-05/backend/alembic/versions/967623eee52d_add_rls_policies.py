"""Add Row Level Security policies to threads and thread_items tables

Revision ID: 967623eee52d
Revises: 967623eee52c
Create Date: 2025-12-26 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '967623eee52d'
down_revision = '967623eee52c'
branch_labels = None
depends_on = None


def upgrade():
    # Enable Row Level Security on threads table
    op.execute("ALTER TABLE threads ENABLE ROW LEVEL SECURITY;")

    # Create policy for threads: users can only access their own threads
    # Application should set app.current_user_id from JWT token in each session
    op.execute("CREATE POLICY threads_user_isolation_policy ON threads FOR ALL USING (user_id = current_setting('app.current_user_id'));")

    # Enable Row Level Security on thread_items table
    op.execute("ALTER TABLE thread_items ENABLE ROW LEVEL SECURITY;")

    # Create policy for thread_items: users can only access items from threads they own
    op.execute("CREATE POLICY thread_items_user_isolation_policy ON thread_items FOR ALL USING (thread_id IN (SELECT id FROM threads WHERE user_id = current_setting('app.current_user_id')));")

    # Create policy to allow inserting thread_items for threads the user owns
    op.execute("CREATE POLICY thread_items_insert_policy ON thread_items FOR INSERT WITH CHECK (thread_id IN (SELECT id FROM threads WHERE user_id = current_setting('app.current_user_id')));")


def downgrade():
    # Drop policies for thread_items
    op.execute("DROP POLICY IF EXISTS thread_items_user_isolation_policy ON thread_items;")

    # Disable Row Level Security on thread_items table
    op.execute("ALTER TABLE thread_items DISABLE ROW LEVEL SECURITY;")

    # Drop policies for threads
    op.execute("DROP POLICY IF EXISTS threads_user_isolation_policy ON threads;")

    # Disable Row Level Security on threads table
    op.execute("ALTER TABLE threads DISABLE ROW LEVEL SECURITY;")