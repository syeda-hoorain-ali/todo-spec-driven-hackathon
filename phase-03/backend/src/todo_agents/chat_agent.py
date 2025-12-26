from agents import Agent
from agents.mcp import MCPServerStreamableHttp
from ..config.settings import settings


def create_todo_chat_agent():
    """
    Create an AI agent specialized for todo management conversations with MCP server integration.
    """

    # Configure the global LLM provider
    settings.configure_llm_provider()

    # Create MCP server connection
    mcp_server = MCPServerStreamableHttp(
        name="Task Operation MCP Server",
        params={
            "url": settings.neon_mcp_server_url,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.neon_api_key}",
            },
            "timeout": 30.0,  # 30 second timeout
        },
        cache_tools_list=True,
        max_retry_attempts=3
    )

    # Define the agent with system instructions for todo management
    agent = Agent(
        name="Todo Management Assistant",
        model="gemini-2.5-flash",
        mcp_servers=[mcp_server],
    #     instructions="""
    #     You are an AI assistant specialized in helping users manage their todo tasks through natural language conversations.
    #     You have access to tools that allow you to interact with a Neon database to perform todo management operations.
    #     Your capabilities include:
    #     - Creating new tasks with titles, descriptions, categories, priorities, and due dates using available tools
    #     - Listing existing tasks with filtering options using available tools
    #     - Updating task details including title, description, completion status, category, priority, and due dates using available tools
    #     - Marking tasks as complete or incomplete using available tools
    #     - Deleting tasks using available tools
    #     - Providing helpful and friendly responses

    #     When a user wants to perform any task management operation (create, list, update, delete, complete), you must use the appropriate tool from your available tools.
    #     Always ensure that you verify the user's intent before performing any operations.
    #     When creating tasks, try to extract relevant information like due dates, priority, and category from the user's request.
    #     When updating tasks, ask for clarification if the user's request is ambiguous.
    #     Maintain a helpful and conversational tone throughout the interaction.

    #     NOTE: This is currently using a placeholder MCP server (Neon HTTP server). In the future, this will be replaced with a custom MCP server that provides specific task management tools.
    #     """
    )

    return agent, mcp_server

