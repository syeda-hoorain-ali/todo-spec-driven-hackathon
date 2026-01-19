from typing import Any, Dict
import requests
import json

id = 10

def send_mcp_request(method: str, params: Dict[str, Any], session_id=None):
    """Helper function to send a JSON-RPC request to an MCP server."""
    global id
    id += 1
    base_url = "http://127.0.0.1:8000/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": id, # Use a unique ID for each request
        "method": method,
        "params": params
    }
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    try:
        response = requests.post(base_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def test_mcp_server_http():
    """Test the MCP server endpoints via HTTP requests"""
    print("Testing MCP Server HTTP endpoints...")
    session_id = None

    # For MCP servers, we need to establish a session first
    # The FastMCP server expects specific headers for session management

    # Test 1: Initialize method - This might need a proper session
    print("\n1. Testing initialize method...")
    response = send_mcp_request(
        "initialize", 
        {"protocolVersion": "2025-10-05", "capabilities": {}, "clientInfo": {"name": "manual-client", "version": "0.0.0"}}
    )

    if response:
        print(f"Initialize response status: {response.status_code}")
        session_id = response.headers.get("mcp-session-id")

    if not session_id:
        raise Exception("")

    # Test 2: List tools method
    print("\n2. Testing tools/list method...")
    tools_response = send_mcp_request("tools/list", {}, session_id)

    if (tools_response):
        print(f"Tools list response status: {tools_response.status_code}")

        # Parse and display tools if successful
        if tools_response.status_code == 200:
            try:
                response_data = tools_response.json()
                if 'result' in response_data and 'tools' in response_data['result']:
                    tools: list[dict] = response_data['result']['tools']
                    print(f"Available tools: {len(tools)}")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description').strip()}")
                else:
                    print("No tools found in response")
            except json.JSONDecodeError:
                print("Response is not valid JSON")


    # Test 3: List tasks
    print("\n3. Testing tools/list method...")
    tools_response = send_mcp_request(
        "tools/call", 
        {"name": "list_tasks", "arguments": {"request": { "user_id": "cMGMMnZsPLg7RHeYglfTKXQQ9zyGRlq4", "status": None, "priority": None, "category": None, "search": None, "sort_by": None, "sort_order": "asc" }}},
        session_id
    )

    if (tools_response):
        print(f"Tools list response status: {tools_response.status_code}")

        # Parse and display tools if successful
        if tools_response.status_code == 200:
            try:
                response_data = tools_response.json()
                print(response_data)

            except json.JSONDecodeError:
                print("Response is not valid JSON")


if __name__ == "__main__":
    test_mcp_server_http()
