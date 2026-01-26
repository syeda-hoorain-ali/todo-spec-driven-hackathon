"""Create audit and dead letter queue tables with RLS policies

Revision ID: 001_create_audit_and_dead_letter_queue_tables
Revises: 967623eee52d
Create Date: 2026-01-26 03:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = '001_create_audit_and_dead_letter_queue_tables'
down_revision = '967623eee52d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('entity_type', sa.String(length=255), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=False),
        sa.Column('operation', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.String(length=255), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for audit_log
    op.create_index(op.f('ix_audit_log_user_id'), 'audit_log', ['user_id'])
    op.create_index(op.f('ix_audit_log_entity_type_entity_id'), 'audit_log', ['entity_type', 'entity_id'])
    op.create_index(op.f('ix_audit_log_timestamp'), 'audit_log', ['timestamp'])
    op.create_index(op.f('ix_audit_log_operation'), 'audit_log', ['operation'])

    # Create dead_letter_queue table
    op.create_table(
        'dead_letter_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=255), nullable=False),
        sa.Column('partition', sa.Integer(), nullable=False),
        sa.Column('offset_value', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.String(length=255), nullable=False),
        sa.Column('processed', sa.Boolean(), server_default=sa.text("'0'"), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for dead_letter_queue
    op.create_index(op.f('ix_dead_letter_queue_processed'), 'dead_letter_queue', ['processed'])
    op.create_index(op.f('ix_dead_letter_queue_timestamp'), 'dead_letter_queue', ['timestamp'])

    # Add RLS policies for PostgreSQL (these will be ignored in SQLite)
    conn = op.get_bind()

    # Enable RLS on the tables (PostgreSQL specific)
    try:
        # Enable Row Level Security
        conn.execute(text("ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;"))
        conn.execute(text("ALTER TABLE dead_letter_queue ENABLE ROW LEVEL SECURITY;"))

        # Create RLS policies for audit_log - users can only see their own audit logs
        conn.execute(text("""
            CREATE POLICY audit_log_policy ON audit_log
            FOR ALL TO app_user
            USING (user_id = current_setting('app.current_user_id', true))
        """))

        # Create RLS policies for dead_letter_queue - users can only see their own failed messages
        # This policy extracts the userId from the JSON message value to determine access
        conn.execute(text("""
            CREATE POLICY dead_letter_queue_policy ON dead_letter_queue
            FOR ALL TO app_user
            USING (
                user_id = current_setting('app.current_user_id', true)
                OR value::json->>'userId' = current_setting('app.current_user_id', true)
                OR value::json->'payload'->>'userId' = current_setting('app.current_user_id', true)
            )
        """))

        # Grant permissions to app_user
        conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON audit_log TO app_user;"))
        conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON dead_letter_queue TO app_user;"))
        conn.execute(text("GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;"))

    except Exception as e:
        # If RLS is not supported (e.g., SQLite), silently continue
        # This allows the migration to work with both PostgreSQL and SQLite
        pass


def downgrade() -> None:
    conn = op.get_bind()

    # Drop RLS policies if they exist (PostgreSQL specific)
    try:
        conn.execute(text("DROP POLICY IF EXISTS audit_log_policy ON audit_log;"))
        conn.execute(text("DROP POLICY IF EXISTS dead_letter_queue_policy ON dead_letter_queue;"))
        conn.execute(text("ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY;"))
        conn.execute(text("ALTER TABLE dead_letter_queue DISABLE ROW LEVEL SECURITY;"))
    except Exception:
        # Ignore if RLS is not supported
        pass

    # Drop indexes for dead_letter_queue
    op.drop_index(op.f('ix_dead_letter_queue_timestamp'), table_name='dead_letter_queue')
    op.drop_index(op.f('ix_dead_letter_queue_processed'), table_name='dead_letter_queue')

    # Drop dead_letter_queue table
    op.drop_table('dead_letter_queue')

    # Drop indexes for audit_log
    op.drop_index(op.f('ix_audit_log_operation'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_timestamp'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_entity_type_entity_id'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_user_id'), table_name='audit_log')

    # Drop audit_log table
    op.drop_table('audit_log')