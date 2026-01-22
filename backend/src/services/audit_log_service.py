import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
from ..config import settings


logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Data class representing an audit log entry."""
    id: Optional[str] = None
    entity_type: str = ""
    entity_id: str = ""
    operation: str = ""
    user_id: str = ""
    timestamp: str = ""
    details: Dict[str, Any] = None
    source: str = ""

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class AuditLogService:
    """
    Service for storing and retrieving audit logs.
    Uses SQLite for persistence as a simple solution.
    In production, this could be replaced with PostgreSQL, MongoDB, or Elasticsearch.
    """

    def __init__(self, db_path: str = "audit_log.db"):
        """Initialize the audit log service."""
        self.db_path = Path(db_path)
        self.init_db()
        logger.info(f"Audit Log Service initialized with database: {self.db_path}")

    def init_db(self):
        """Initialize the database with the audit_log table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the audit_log table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT NOT NULL,
                    source TEXT NOT NULL
                )
            """)

            # Create indexes for common query patterns
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entity ON audit_log(entity_type, entity_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user ON audit_log(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_operation ON audit_log(operation)
            """)

            conn.commit()
            conn.close()

            logger.info("Audit log database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audit log database: {str(e)}")
            raise

    def save_audit_entry(self, audit_entry: AuditEntry):
        """
        Save an audit entry to the database.

        Args:
            audit_entry: The audit entry to save
        """
        try:
            import uuid
            if not audit_entry.id:
                audit_entry.id = str(uuid.uuid4())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert details to JSON string
            details_json = json.dumps(audit_entry.details)

            cursor.execute("""
                INSERT INTO audit_log (id, entity_type, entity_id, operation, user_id, timestamp, details, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_entry.id,
                audit_entry.entity_type,
                audit_entry.entity_id,
                audit_entry.operation,
                audit_entry.user_id,
                audit_entry.timestamp,
                details_json,
                audit_entry.source
            ))

            conn.commit()
            conn.close()

            logger.info(f"Audit entry saved: {audit_entry.operation} {audit_entry.entity_type} {audit_entry.entity_id}")

        except Exception as e:
            logger.error(f"Failed to save audit entry: {str(e)}")
            raise

    def get_audit_entries(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """
        Retrieve audit entries based on filters.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            user_id: Filter by user ID
            operation: Filter by operation type
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of audit entries matching the criteria
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build the query dynamically based on filters
            query = "SELECT id, entity_type, entity_id, operation, user_id, timestamp, details, source FROM audit_log WHERE 1=1"
            params = []

            if entity_type:
                query += " AND entity_type = ?"
                params.append(entity_type)

            if entity_id:
                query += " AND entity_id = ?"
                params.append(entity_id)

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if operation:
                query += " AND operation = ?"
                params.append(operation)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            conn.close()

            # Convert rows to AuditEntry objects
            audit_entries = []
            for row in rows:
                details = json.loads(row[6])  # Parse the JSON details
                audit_entry = AuditEntry(
                    id=row[0],
                    entity_type=row[1],
                    entity_id=row[2],
                    operation=row[3],
                    user_id=row[4],
                    timestamp=row[5],
                    details=details,
                    source=row[7]
                )
                audit_entries.append(audit_entry)

            return audit_entries

        except Exception as e:
            logger.error(f"Failed to retrieve audit entries: {str(e)}")
            raise

    def get_audit_entry_by_id(self, entry_id: str) -> Optional[AuditEntry]:
        """
        Retrieve a specific audit entry by ID.

        Args:
            entry_id: The ID of the audit entry

        Returns:
            The audit entry if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id, entity_type, entity_id, operation, user_id, timestamp, details, source FROM audit_log WHERE id = ?", (entry_id,))
            row = cursor.fetchone()

            conn.close()

            if row:
                details = json.loads(row[6])  # Parse the JSON details
                return AuditEntry(
                    id=row[0],
                    entity_type=row[1],
                    entity_id=row[2],
                    operation=row[3],
                    user_id=row[4],
                    timestamp=row[5],
                    details=details,
                    source=row[7]
                )

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve audit entry {entry_id}: {str(e)}")
            raise

    def search_audit_entries(self, search_term: str, limit: int = 100) -> List[AuditEntry]:
        """
        Search audit entries for a specific term across all fields.

        Args:
            search_term: The term to search for
            limit: Maximum number of results

        Returns:
            List of audit entries matching the search term
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Search across multiple fields using LIKE
            query = """
                SELECT id, entity_type, entity_id, operation, user_id, timestamp, details, source
                FROM audit_log
                WHERE entity_type LIKE ? OR entity_id LIKE ? OR operation LIKE ? OR user_id LIKE ?
                OR details LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            search_pattern = f"%{search_term}%"
            params = [search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, limit]

            cursor.execute(query, params)
            rows = cursor.fetchall()

            conn.close()

            # Convert rows to AuditEntry objects
            audit_entries = []
            for row in rows:
                details = json.loads(row[6])  # Parse the JSON details
                audit_entry = AuditEntry(
                    id=row[0],
                    entity_type=row[1],
                    entity_id=row[2],
                    operation=row[3],
                    user_id=row[4],
                    timestamp=row[5],
                    details=details,
                    source=row[7]
                )
                audit_entries.append(audit_entry)

            return audit_entries

        except Exception as e:
            logger.error(f"Failed to search audit entries: {str(e)}")
            raise

    def cleanup_old_entries(self, days_to_keep: int = 90, entity_type_filter: Optional[str] = None):
        """
        Delete audit entries older than the specified number of days.

        Args:
            days_to_keep: Number of days to retain entries (default 90 days for audit)
            entity_type_filter: Optional entity type to filter cleanup
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "DELETE FROM audit_log WHERE timestamp < ?"
            params = [cutoff_date]

            if entity_type_filter:
                query += " AND entity_type = ?"
                params.append(entity_type_filter)

            cursor.execute(query, params)
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted_count} audit entries older than {days_to_keep} days")

        except Exception as e:
            logger.error(f"Failed to cleanup old audit entries: {str(e)}")
            raise

    def apply_retention_policy(self):
        """
        Apply compliance retention policies:
        - Audit logs: 90 days
        - Other logs: 7 days
        """
        try:
            # Keep audit logs for 90 days
            self.cleanup_old_entries(days_to_keep=90, entity_type_filter="audit")

            # Keep other logs for 7 days
            self.cleanup_old_entries(days_to_keep=7)

            logger.info("Retention policy applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply retention policy: {str(e)}")
            raise


# Global instance of audit log service
audit_log_service = AuditLogService()