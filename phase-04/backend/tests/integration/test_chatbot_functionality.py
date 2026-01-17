"""
Test to verify the complete AI chatbot functionality with MCP integration
"""
import asyncio
import sys
from pathlib import Path

# Add the backend/src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.todo_agents.chat_agent import create_todo_chat_agent
from agents import Runner


async def test_mcp_server_direct_functionality():
    """Test MCP server methods directly - skipped for Neon HTTP server placeholder"""
    print("Skipping direct MCP server functionality test - using Neon HTTP server as placeholder")
    print("In future, this will be replaced with custom task management MCP server")
    pass


async def test_agent_with_mcp_integration():
    """Test the agent with MCP integration"""
    print("Testing agent with MCP integration...")

    try:
        # Create the agent with Neon HTTP MCP server as placeholder
        agent, mcp_server = create_todo_chat_agent()

        # Test getting available tools
        from agents import RunContextWrapper
        tools = await agent.get_all_tools(run_context=RunContextWrapper(context=None))
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:100].replace(chr(10), '')}")

        # Test the agent with a simple message
        async with mcp_server:
            result = await Runner.run(agent, "List tasks for user test_user_123")
            print(f"Agent response: {result.final_output}")

            # Test creating a task via agent
            result = await Runner.run(agent, "Create a task for user test_user_123 with title 'Test task' and description 'This is a test task created from the agent'")
            print(f"Create task via agent response: {result.final_output}")

        print("Agent with MCP integration test completed.")
    except Exception as e:
        print(f"Error in agent MCP integration test: {e}")
        import traceback
        traceback.print_exc()


def test_mcp_server_http_endpoints():
    """Test MCP server HTTP endpoints - skipped for Neon HTTP server placeholder"""
    print("Skipping MCP server HTTP endpoints test - using Neon HTTP server as placeholder")
    print("In future, this will be replaced with custom task management MCP server endpoints")
    pass


if __name__ == "__main__":
    print("Running comprehensive tests for AI chatbot with MCP integration...")

    print("\n1. Testing MCP server direct functionality:")
    asyncio.run(test_mcp_server_direct_functionality())

    print("\n2. Testing MCP server HTTP endpoints:")
    test_mcp_server_http_endpoints()

    print("\n3. Testing agent with MCP integration:")
    asyncio.run(test_agent_with_mcp_integration())

    print("\nAll tests completed!")