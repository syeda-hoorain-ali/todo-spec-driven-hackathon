"""Rename conversations and messages tables to threads and thread_items

Revision ID: 967623eee52c
Revises: 967623eee52b
Create Date: 2025-12-26 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '967623eee52c'
down_revision = '967623eee52b'
branch_labels = None
depends_on = None


def upgrade():
    # Check if old tables exist before trying to rename them
    # If they don't exist, it means we're starting fresh with the new schema
    connection = op.get_bind()

    # Check if conversations table exists
    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'conversations'
            );
        """)
    )
    conversations_exists = result.scalar()

    # Check if messages table exists
    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'messages'
            );
        """)
    )
    messages_exists = result.scalar()

    # If old tables exist, rename them to new names
    if conversations_exists:
        op.rename_table('conversations', 'threads')

    if messages_exists:
        op.rename_table('messages', 'thread_items')

    # If old indexes exist, rename them too
    if conversations_exists:
        try:
            op.execute("ALTER INDEX ix_conversations_user_id RENAME TO ix_threads_user_id")
        except:
            # Index might not exist or already renamed
            pass

    if messages_exists:
        try:
            op.execute("ALTER INDEX ix_messages_user_id RENAME TO ix_thread_items_user_id")
            op.execute("ALTER INDEX ix_messages_conversation_id RENAME TO ix_thread_items_thread_id")
        except:
            # Index might not exist or already renamed
            pass


def downgrade():
    # Rename back to old names
    connection = op.get_bind()

    # Check if new tables exist before renaming
    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'threads'
            );
        """)
    )
    threads_exists = result.scalar()

    result = connection.execute(
        sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'thread_items'
            );
        """)
    )
    thread_items_exists = result.scalar()

    if threads_exists:
        op.rename_table('threads', 'conversations')

    if thread_items_exists:
        op.rename_table('thread_items', 'messages')

    # Rename indexes back
    if threads_exists:
        try:
            op.execute("ALTER INDEX ix_threads_user_id RENAME TO ix_conversations_user_id")
        except:
            pass

    if thread_items_exists:
        try:
            op.execute("ALTER INDEX ix_thread_items_user_id RENAME TO ix_messages_user_id")
            op.execute("ALTER INDEX ix_thread_items_thread_id RENAME TO ix_messages_conversation_id")
        except:
            pass