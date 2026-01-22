import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path


logger = logging.getLogger(__name__)


class IdempotencyChecker:
    """
    Utility class to check for duplicate events using idempotency keys.
    """

    def __init__(self, db_path: str = "idempotency.db", retention_days: int = 7):
        """
        Initialize the idempotency checker.

        Args:
            db_path: Path to the SQLite database for storing idempotency keys
            retention_days: Number of days to retain idempotency records
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.init_db()
        logger.info(f"Idempotency checker initialized with database: {self.db_path}")

    def init_db(self):
        """Initialize the database with the idempotency_keys table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the idempotency_keys table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS idempotency_keys (
                    idempotency_key TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)

            # Create an index on processed_at for cleanup queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON idempotency_keys(expires_at)
            """)

            conn.commit()
            conn.close()

            logger.info("Idempotency database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize idempotency database: {str(e)}")
            raise

    def generate_idempotency_key(self, message: Dict[str, Any]) -> str:
        """
        Generate an idempotency key from a message.

        Args:
            message: The message to generate an idempotency key for

        Returns:
            A unique idempotency key
        """
        # Try to get idempotency key from message headers first
        headers = message.get('headers', {})
        if 'idempotency-key' in headers:
            return headers['idempotency-key']

        # If not provided, generate from message content
        # Use eventId if available, otherwise hash the message content
        event_id = message.get('value', {}).get('eventId') or message.get('eventId')
        if event_id:
            return f"event:{event_id}"

        # As a fallback, create a hash of the message content
        message_copy = message.copy()
        # Remove headers and metadata that might vary between duplicates
        message_copy.pop('timestamp', None)
        message_copy.pop('partition', None)
        message_copy.pop('offset', None)

        message_str = json.dumps(message_copy, sort_keys=True, default=str)
        return hashlib.sha256(message_str.encode()).hexdigest()[:32]

    def check_and_record(self, message: Dict[str, Any]) -> bool:
        """
        Check if a message is a duplicate and record it if it's new.

        Args:
            message: The message to check and record

        Returns:
            True if the message is new (not a duplicate), False if it's a duplicate
        """
        try:
            idempotency_key = self.generate_idempotency_key(message)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if the idempotency key already exists
            cursor.execute(
                "SELECT 1 FROM idempotency_keys WHERE idempotency_key = ?",
                (idempotency_key,)
            )
            result = cursor.fetchone()

            if result is not None:
                # Duplicate found
                conn.close()
                logger.info(f"Duplicate event detected with idempotency key: {idempotency_key}")
                return False

            # Create a hash of the message to detect if content changed
            message_str = json.dumps(message, sort_keys=True, default=str)
            event_hash = hashlib.sha256(message_str.encode()).hexdigest()

            # Calculate expiration time
            expires_at = (datetime.utcnow() + timedelta(days=self.retention_days)).isoformat()

            # Insert the idempotency key
            cursor.execute("""
                INSERT INTO idempotency_keys
                (idempotency_key, processed_at, event_hash, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                idempotency_key,
                datetime.utcnow().isoformat(),
                event_hash,
                expires_at
            ))

            conn.commit()
            conn.close()

            logger.debug(f"Recorded new event with idempotency key: {idempotency_key}")
            return True

        except Exception as e:
            logger.error(f"Error checking for duplicate event: {str(e)}")
            # If there's an error checking, we'll process the event anyway
            # to avoid blocking legitimate events due to storage issues
            return True

    def cleanup_expired_records(self):
        """
        Remove expired idempotency records from the database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now_iso = datetime.utcnow().isoformat()
            cursor.execute(
                "DELETE FROM idempotency_keys WHERE expires_at < ?",
                (now_iso,)
            )
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired idempotency records")

        except Exception as e:
            logger.error(f"Error cleaning up expired idempotency records: {str(e)}")


# Global instance of idempotency checker
idempotency_checker = IdempotencyChecker()