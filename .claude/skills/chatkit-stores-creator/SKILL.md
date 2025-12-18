---
name: chatkit-store-creator
description: This skill helps create ChatKit store implementations with database integration, following best practices and avoiding common errors we've solved in previous implementations.
---

# ChatKit Stores Creator

This skill helps create ChatKit store implementations with database integration, following best practices and avoiding common errors we've solved in previous implementations.

## Usage Instructions

When a user needs to create a ChatKit store with database integration, use this skill to generate:

1. Store class extending the base ChatKit Store interface
2. Proper database connection and connection pooling
3. All required abstract methods implementation
4. Error handling for database operations
5. Type-safe implementations for ChatKit types

## Common Errors to Avoid (Based on Previous Solutions)

1. **Abstract Method Implementation Error**: "Cannot instantiate abstract class 'Stores' - Abstract methods not implemented"
   - Solution: Implement ALL required abstract methods from the Store interface

2. **Configuration Access Error**: "AttributeError: 'Config' object has no attribute 'NEON_DATABASE_URL'"
   - Solution: Access settings correctly using the settings instance, not the Config class

3. **Content Part Type Error**: Using incorrect content types like MessageContentPart
   - Solution: Use correct ChatKit types like UserMessageContent and AssistantMessageContent

4. **Connection Pool Error**: "acquire" is not a known attribute of "None"
   - Solution: Ensure connection pool is initialized before use

5. **Type Mismatch Error**: "Argument of type 'int' cannot be assigned to parameter 'object' of type 'str'"
   - Solution: Cast parameters to correct types when appending to query parameters

6. **ThreadMetadata Error**: "No parameter named 'updated_at'"
   - Solution: Use metadata field instead: metadata={"updated_at": value}

## Template Structure

### Complete Store Implementation Template:
```python
import asyncpg
from typing import Optional, List, Dict, Any
import uuid
import logging
from chatkit.store import Store, StoreItemType
from chatkit.types import ThreadMetadata, ThreadItem, Attachment, Page, UserMessageItem, AssistantMessageItem, InferenceOptions, AssistantMessageContent, UserMessageTextContent
from src.config import settings  # Import the settings instance, not the Config class

# Set up logging
logger = logging.getLogger(__name__)

class YourStoreName(Store[dict]):
    """Store implementation using PostgreSQL database for message and attachment persistence."""

    def __init__(self):
        self.connection_string = settings.your_database_url  # Access settings correctly

    async def connect(self):
        """Establish connection to the database."""

    async def _initialize_tables(self):
        """Create required tables if they don't exist."""
        if not self.pool:
            await self.connect()

        # Verify the pool is not None after connecting
        if not self.pool:
            raise RuntimeError("Failed to establish database connection pool")


    # Implement ALL abstract methods from Store class
    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        """Load a thread by its ID."""

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        """Save a thread."""

    async def load_thread_items(self, thread_id: str, after: str | None, limit: int, order: str, context: dict) -> Page[ThreadItem]:
        """Load items for a specific thread."""


    async def save_attachment(self, attachment: Attachment, context: dict) -> None:
        """Save an attachment."""
        # For now, we'll just log this since we're not implementing file storage
        logger.info(f"Saving attachment: {attachment.id}")

    async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
        """Load an attachment by ID."""
        # For now, we'll return a placeholder since we're not implementing file storage
        logger.info(f"Loading attachment: {attachment_id}")
        raise ValueError(f"Attachment {attachment_id} not found")

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        """Delete an attachment by ID."""
        logger.info(f"Deleting attachment: {attachment_id}")

    async def load_threads(self, limit: int, after: str | None, order: str, context: dict) -> Page[ThreadMetadata]:
        """Load multiple threads."""

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        """Add an item to a thread."""

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        """Save an item to a thread (alternative to add_thread_item)."""

    async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
        """Load a specific item from a thread."""

    def generate_thread_id(self, context: dict) -> str:
        """Generate a new thread ID."""

    def generate_item_id(self, item_type: StoreItemType, thread: ThreadMetadata, context: dict) -> str:
        """Generate a new item ID."""

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        """Delete a thread by its ID."""

    # Helper methods for compatibility with original implementation
    async def save_message(self, thread_id: str, content: str, sender_type: str) -> str:
        """Save a message to the database.

        Args:
            thread_id: The ID of the thread the message belongs to
            content: The content of the message
            sender_type: The type of sender ('user' or 'agent')

        Returns:
            The ID of the saved message
        """

    async def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific thread.

        Args:
            thread_id: The ID of the thread to retrieve messages for

        Returns:
            List of messages in the thread
        """

    async def create_thread(self, title: Optional[str] = None) -> str:
        """Create a new conversation thread.

        Args:
            title: Optional title for the thread

        Returns:
            The ID of the created thread
        """

    async def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific thread by ID.

        Args:
            thread_id: The ID of the thread to retrieve

        Returns:
            Thread information or None if not found
        """
    async def close(self):
        """Close the database connection pool."""
```

## Key Implementation Points

- **All Abstract Methods**: Implements ALL required abstract methods from the Store interface
- **Configuration Access**: Uses the settings instance correctly, not the Config class
- **Type Safety**: Uses correct ChatKit types like UserMessageContent and AssistantMessageContent
- **Connection Handling**: Ensures connection pool is initialized before database operations
- **Type Casting**: Properly casts parameters to avoid type mismatch errors
- **ThreadMetadata**: Uses metadata field instead of direct updated_at parameter

## Common Store Categories

- PostgreSQL stores (using asyncpg)
- MySQL stores (using aiomysql)
- SQLite stores (using aiosqlite)
- MongoDB stores (using motor)
- In-memory stores (for testing)

## Output Requirements

1. Generate complete, working ChatKit store implementations
2. Include ALL required abstract methods implementation
3. Add proper error handling for database operations
4. Use correct ChatKit types for content
5. Follow the exact patterns shown in the template to avoid common errors
