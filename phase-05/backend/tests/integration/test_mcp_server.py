"""
Test script to verify MCP server functionality
"""
import asyncio
import httpx
import json


async def test_mcp_server():
    """Test the MCP server endpoints"""
    base_url = "http://localhost:8000"  # MCP endpoints are now integrated into main app

    # Test the call_tool endpoint
    async with httpx.AsyncClient() as client:
        # Test list_tasks (this will fail without a valid user_id, but should reach the server)
        try:
            response = await client.post(
                f"{base_url}/mcp/call_tool",
                json={
                    "method": "list_tasks",
                    "params": {"user_id": "test_user_123"}
                },
                timeout=10.0
            )
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        except httpx.ConnectError:
            print("Could not connect to MCP server. Make sure the main backend is running on port 8000.")
        except Exception as e:
            print(f"Error calling MCP server: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())