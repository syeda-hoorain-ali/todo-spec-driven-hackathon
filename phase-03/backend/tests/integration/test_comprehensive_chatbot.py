"""
Comprehensive test for the AI chatbot with MCP integration
"""
import asyncio
import httpx
import json
from datetime import datetime


async def test_chat_endpoint():
    """Test the chat endpoint with a sample message"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        try:
            # Test the chat endpoint
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "message": "Create a task to buy groceries",
                    "user_timezone": "UTC"
                },
                headers={
                    "Authorization": "Bearer your-test-jwt-token-here",  # This will fail without a real token
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            print(f"Chat endpoint response status: {response.status_code}")
            print(f"Chat endpoint response: {response.text}")
        except httpx.ConnectError:
            print("Could not connect to API server. Make sure it's running on port 8000.")
        except Exception as e:
            print(f"Error calling chat endpoint: {e}")


async def test_mcp_server_directly():
    """Test the MCP server directly"""
    base_url = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        try:
            # Test list_tasks method
            response = await client.post(
                f"{base_url}/mcp/call_tool",
                json={
                    "method": "list_tasks",
                    "params": {
                        "user_id": "test_user_123"
                    }
                },
                timeout=10.0
            )
            print(f"MCP list_tasks response status: {response.status_code}")
            print(f"MCP list_tasks response: {response.text}")

            # Test create_task method
            response = await client.post(
                f"{base_url}/mcp/call_tool",
                json={
                    "method": "create_task",
                    "params": {
                        "user_id": "test_user_123",
                        "title": "Test task from MCP",
                        "description": "This is a test task created via MCP"
                    }
                },
                timeout=10.0
            )
            print(f"MCP create_task response status: {response.status_code}")
            print(f"MCP create_task response: {response.text}")

        except httpx.ConnectError:
            print("Could not connect to MCP server. Make sure it's running on port 8001.")
        except Exception as e:
            print(f"Error calling MCP server: {e}")


async def main():
    print("Testing MCP server integration...")

    print("\n1. Testing MCP server directly:")
    await test_mcp_server_directly()

    print("\n2. Testing chat endpoint:")
    await test_chat_endpoint()

    print("\nTest completed.")


if __name__ == "__main__":
    asyncio.run(main())