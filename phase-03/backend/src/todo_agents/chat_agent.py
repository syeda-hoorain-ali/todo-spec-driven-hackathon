from typing import Optional
from agents import Agent, RunContextWrapper
from agents.mcp import MCPServerStreamableHttp
from ..config.settings import settings
from .context import UserContext
from chatkit.agents import AgentContext
from datetime import datetime

agent: Optional[Agent[AgentContext[UserContext]]] = None
mcp_server: Optional[MCPServerStreamableHttp] = None


def dynamic_instructions(
    context: RunContextWrapper[AgentContext[UserContext]],
    agent: Agent[AgentContext[UserContext]]
) -> str:
    """Dynamic instructions that include user ID from context"""
    user_id = context.context.request_context.user_id if context.context and context.context.request_context else "unknown"
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
    You are an AI assistant specialized in helping users manage their todo tasks through natural language conversations.
    You have access to tools that allow you to interact with a Neon database to perform todo management operations.
    The current user ID is: {user_id}
    The current date and time is: {current_datetime}

    Your capabilities include:
    - Creating new tasks with titles, descriptions, categories, priorities, and due dates using available tools
    - Listing existing tasks with filtering options using available tools
    - Updating task details including title, description, completion status, category, priority, and due dates using available tools
    - Marking tasks as complete or incomplete using available tools
    - Deleting tasks using available tools
    - Providing helpful and friendly responses

    When a user wants to perform any task management operation (create, list, update, delete, complete), you must use the appropriate tool from your available tools.
    Always ensure that you verify the user's intent before performing any operations.
    When creating tasks, try to extract relevant information like due dates, priority, and category from the user's request.
    When updating tasks, ask for clarification if the user's request is ambiguous.
    Maintain a helpful and conversational tone throughout the interaction.

    IMPORTANT DATE/TIME FORMAT INSTRUCTIONS:
    - When setting due dates or reminder times, use the ISO 8601 format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS
    - For today's date, use the current date from the context above
    - For times, use 24-hour format (e.g., 22:00 for 10 PM)
    - Example: "2025-12-30T22:00:00" or "2025-12-30 22:00:00" for 10 PM today
    - Avoid ambiguous formats like "today at 10pm", instead convert to the specific ISO format
    """


def create_todo_chat_agent():
    """
    Create an AI agent specialized for todo management conversations with MCP server integration.
    """
    global agent, mcp_server

    if agent and mcp_server:
        return agent, mcp_server

    # Configure the global LLM provider
    settings.configure_llm_provider()

    # Create MCP server connection
    mcp_server = MCPServerStreamableHttp(
        name="Task Operation MCP Server",
        params={
            "url": settings.mcp_server_url,
            "headers": {
                "Content-Type": "application/json",
            },
            "timeout": 30.0,  # 30 second timeout
        },
        cache_tools_list=True,
        max_retry_attempts=3
    )

    # Define the agent with system instructions for todo management
    agent = Agent[AgentContext[UserContext]](
        name="Todo Management Assistant",
        model="gemini-2.5-flash",
        mcp_servers=[mcp_server],
        instructions=dynamic_instructions
    )

    return agent, mcp_server

