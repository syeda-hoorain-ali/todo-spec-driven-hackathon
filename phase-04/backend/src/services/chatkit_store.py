"""
ChatKit Stores Implementation
Connects ChatKit to Neon DB for conversation persistence
"""
from typing import List, Optional
from sqlmodel import Session, select, asc, desc
from sqlalchemy import text
from chatkit.store import Store
from chatkit.types import (
    AssistantMessageItem, UserMessageItem,
    UserMessageTextContent, AssistantMessageContent,
    InferenceOptions, Page,
    ThreadMetadata, ThreadItem as ThreadItemType, Attachment
)
from ..models.thread import Thread as Thread
from ..models.thread_item import ThreadItem as ThreadItem
from ..database.database import engine
from ..todo_agents.context import UserContext
import uuid



class ChatKitNeonStore(Store[UserContext]):
    """
    ChatKit stores implementation that connects to Neon DB
    Provides conversation and message storage for ChatKit
    """

    def __init__(self):
        self.engine = engine

    async def load_thread(self, thread_id: str, context: UserContext) -> ThreadMetadata:
        """Load a thread by its ID"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            thread = session.get(Thread, thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")

            # Verify that the thread belongs to the requesting user (double-check)
            if thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            return ThreadMetadata(
                id=thread.id,
                created_at=thread.created_at,
                metadata={
                    "updated_at": thread.updated_at.isoformat(),
                    "user_id": thread.user_id
                }
            )

    async def save_thread(self, thread: ThreadMetadata, context: UserContext) -> None:
        """Save a thread"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            # Check if thread already exists in the database
            existing_thread = session.get(Thread, thread.id)

            if not existing_thread:
                # Create a new thread with the thread ID as the thread ID
                # This ensures the thread ID matches the thread ID from ChatKit
                thread_obj = Thread(
                    id=thread.id,
                    user_id=user_id  # Use the user_id from context, not from thread metadata
                )
                session.add(thread_obj)
                session.commit()

    async def load_thread_items(self, thread_id: str, after: Optional[str], limit: int, order: str, context: UserContext):
        """Load thread items for a thread"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            # First verify that the thread belongs to the user
            thread = session.get(Thread, thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            if thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            thread_items = session.exec(
                select(ThreadItem)
                .where(ThreadItem.thread_id == thread_id)
                .order_by(asc(ThreadItem.timestamp))
            ).all()

            items: List[ThreadItemType] = []
            for item in thread_items:
                if item.role == "user":
                    thread_item = UserMessageItem(
                        id=item.id,
                        thread_id=thread_id,
                        content=[UserMessageTextContent(type="input_text", text=item.content)],
                        created_at=item.timestamp,
                        inference_options=InferenceOptions()
                    )
                else:
                    thread_item = AssistantMessageItem(
                        id=item.id,
                        thread_id=thread_id,
                        content=[AssistantMessageContent(type="output_text", text=item.content)],
                        created_at=item.timestamp
                    )
                items.append(thread_item)

            if after:
                pass

            if limit and len(items) > limit:
                items = items[:limit]

            return Page(data=items, has_more=False)

    async def save_attachment(self, attachment: Attachment, context: UserContext) -> None:
        """Save an attachment"""
        print(f"Saving attachment: {attachment.id}")

    async def load_attachment(self, attachment_id: str, context: UserContext) -> Attachment:
        """Load an attachment by ID"""
        raise ValueError(f"Attachment {attachment_id} not found")

    async def delete_attachment(self, attachment_id: str, context: UserContext) -> None:
        """Delete an attachment by ID"""
        print(f"Deleting attachment: {attachment_id}")

    async def load_threads(self, limit: int, after: str | None, order: str, context: UserContext) -> Page[ThreadMetadata]:
        """Load multiple threads"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            # Load only threads that belong to the requesting user
            threads = session.exec(
                select(Thread)
                .where(Thread.user_id == user_id)
                .order_by(desc(Thread.updated_at))
            ).all()

            thread_metadata_list: List[ThreadMetadata] = []
            for thread in threads:
                thread_metadata = ThreadMetadata(
                    id=thread.id,
                    created_at=thread.created_at,
                    metadata={
                        "updated_at": thread.updated_at.isoformat(),
                        "user_id": thread.user_id
                    }
                )
                thread_metadata_list.append(thread_metadata)

            if limit:
                thread_metadata_list = thread_metadata_list[:limit]

            return Page(data=thread_metadata_list, has_more=False)

    async def add_thread_item(self, thread_id: str, item: ThreadItemType, context: UserContext) -> None:
        """Add an item to a thread"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            # Verify that the thread belongs to the user
            thread = session.get(Thread, thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
            if thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            content_text = ""

            if (item.type == "user_message" or item.type == "assistant_message") and item.content:
                for part in item.content:
                    content_text += part.text

            role = 'assistant' if hasattr(item, 'type') and item.type == 'assistant_message' else 'user'

            thread_item = ThreadItem(
                id=str(uuid.uuid4()),  # Generate a new ID for the thread item
                thread_id=thread_id,
                user_id=user_id,  # Use the user_id from context
                role=role,
                content=content_text
            )

            session.add(thread_item)
            session.commit()

    async def save_item(self, thread_id: str, item: ThreadItemType, context: UserContext) -> None:
        """Save an item to a thread"""
        await self.add_thread_item(thread_id, item, context)

    async def load_item(self, thread_id: str, item_id: str, context: UserContext) -> ThreadItemType:
        """Load a specific item from a thread"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            thread_item = session.get(ThreadItem, item_id)  # ThreadItem ID is now string

            if not thread_item or str(thread_item.thread_id) != thread_id:
                raise ValueError(f"Item {item_id} not found in thread {thread_id}")

            # Verify that the thread belongs to the user
            thread = session.get(Thread, thread_id)
            if not thread or thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            if thread_item.role == "user":
                return UserMessageItem(
                    id=thread_item.id,
                    thread_id=thread_id,
                    content=[UserMessageTextContent(type="input_text", text=thread_item.content)],
                    created_at=thread_item.timestamp,
                    inference_options=InferenceOptions()
                )
            else:
                return AssistantMessageItem(
                    id=thread_item.id,
                    thread_id=thread_id,
                    content=[AssistantMessageContent(type="output_text", text=thread_item.content)],
                    created_at=thread_item.timestamp
                )

    async def delete_thread_item(self, thread_id: str, item_id: str, context: UserContext) -> None:
        """Delete a thread item by its ID"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            thread_item = session.get(ThreadItem, item_id)

            if not thread_item or str(thread_item.thread_id) != thread_id:
                raise ValueError(f"Item {item_id} not found in thread {thread_id}")

            # Verify that the thread belongs to the user
            thread = session.get(Thread, thread_id)
            if not thread or thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            session.delete(thread_item)
            session.commit()

    async def delete_thread(self, thread_id: str, context: UserContext) -> None:
        """Delete a thread by its ID"""
        # Get user_id from context for RLS policies
        user_id = context.user_id

        # Create a session and set the session variable for RLS
        with Session(self.engine) as session:
            # Execute raw SQL to set the session variable for RLS
            session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})

            thread = session.get(Thread, thread_id)

            if not thread:
                raise ValueError(f"Thread {thread_id} not found")

            # Verify that the thread belongs to the user
            if thread.user_id != user_id:
                raise ValueError(f"Thread {thread_id} does not belong to user {user_id}")

            thread_items = session.exec(select(ThreadItem).where(ThreadItem.thread_id == thread_id)).all()
            for thread_item in thread_items:
                session.delete(thread_item)

            session.delete(thread)
            session.commit()
