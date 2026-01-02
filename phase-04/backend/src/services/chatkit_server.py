"""
ChatKit Server Implementation
Provides ChatKit server functionality for conversation management with database integration and agent processing
"""
import logging
from typing import AsyncIterator
from agents import Agent, Runner
from chatkit.server import ChatKitServer as BaseChatKitServer
from chatkit.store import Store
from chatkit.types import AssistantMessageItem, ThreadMetadata, UserMessageItem, ThreadStreamEvent
from chatkit.agents import AgentContext, stream_agent_response, ThreadItemConverter
from ..todo_agents.context import UserContext


# Set up logging
logger = logging.getLogger(__name__)

class ChatKitServer(BaseChatKitServer):
    """
    Custom ChatKit server implementation extending the base ChatKitServer class.
    """

    def __init__(self, agent: Agent[AgentContext[UserContext]], store: Store[UserContext]):
        """
        Initialize the custom ChatKit server with the provided agent and store.

        Args:
            agent: The OpenAI Agent to use for processing messages
            store: The store implementation for message persistence
        """
        # Initialize the base class with store
        super().__init__(store=store)
        self.agent = agent
        self.converter = ThreadItemConverter()
        logger.info("CustomChatKitServer initialized")

    async def respond(self, thread: ThreadMetadata, input_user_message: UserMessageItem | None, context: UserContext) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process a user message and generate an agent response with database persistence.
        """
        agent_context = AgentContext[UserContext](
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Load all thread items from the database
        page = await self.store.load_thread_items(thread.id, None, 100, "asc", context)
        all_items = list(page.data)

        # Add current input to the list if provided
        if input_user_message:
            all_items.append(input_user_message)

        # Convert thread items to agent input format
        agent_input = await self.converter.to_agent_input(all_items) if all_items else []

        # Run the agent with streaming
        result = Runner.run_streamed(
            self.agent,
            agent_input,
            context=agent_context,
        )

        # Track ID mappings to ensure unique IDs (LiteLLM/Gemini may reuse IDs)
        id_mapping: dict[str, str] = {}
        try:
            async for event in stream_agent_response(agent_context, result):
                # Handle ID mapping for uniqueness
                if event.type == "thread.item.added":
                    if isinstance(event.item, AssistantMessageItem):
                        old_id = event.item.id
                        # Generate unique ID if we haven't seen this response ID before
                        if old_id not in id_mapping:
                            new_id = self.store.generate_item_id("message", thread, context)
                            id_mapping[old_id] = new_id
                        event.item.id = id_mapping[old_id]
                elif event.type == "thread.item.done":
                    if isinstance(event.item, AssistantMessageItem):
                        old_id = event.item.id
                        if old_id in id_mapping:
                            event.item.id = id_mapping[old_id]
                elif event.type == "thread.item.updated":
                    if event.item_id in id_mapping:
                        event.item_id = id_mapping[event.item_id]

                yield event
        except Exception as e:
            logger.error("Error", e)
