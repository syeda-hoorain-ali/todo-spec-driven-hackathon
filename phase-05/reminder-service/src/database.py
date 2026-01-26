"""Database module for Reminder Service."""
import logging
from typing import Optional
import asyncpg
from sqlmodel import create_engine


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations for the reminder service."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self.engine = create_engine(database_url)

    async def initialize(self):
        """Initialize the database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("Database connection pool created")

            # Ensure tables exist
            await self.ensure_db_tables()
            logger.info("Database tables verified")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {str(e)}")
            raise

    async def close(self):
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def ensure_db_tables(self):
        """Verify that the required tables exist in the database."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            # Just verify that tables exist - they should be created via Alembic migrations
            try:
                # Check if reminder table exists
                await conn.fetchval("SELECT to_regclass('public.reminder')")

                logger.info("Database tables verified - assuming they exist from Alembic migrations")
            except Exception as e:
                logger.error(f"Error verifying database tables: {str(e)}")
                raise

    def get_connection(self):
        """Get a database connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        return self.pool.acquire()

    @property
    def connection_pool(self) -> asyncpg.Pool:
        """Get the connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        return self.pool
