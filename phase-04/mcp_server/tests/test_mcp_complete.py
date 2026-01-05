import requests
import json

def test_mcp_server_complete():
    """Test the MCP server with proper session management"""
    base_url = "http://127.0.0.1:8000/mcp"

    print("Testing MCP Server with proper session management...")

    # Session to maintain connection state
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    # Step 1: Initialize the MCP session
    print("\n1. Initializing MCP session...")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "capabilities": {},
            "client_info": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    try:
        response = session.post(base_url, json=init_payload)
        print(f"Initialize response status: {response.status_code}")
        print(f"Initialize response: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            if 'result' in response_data:
                print("✓ Initialization successful")
            else:
                print("✗ Initialization failed")
        else:
            print("✗ Initialization failed with status code:", response.status_code)
    except Exception as e:
        print(f"Error during initialize: {e}")

    # Step 2: Try to list tools (this may require a proper session ID)
    print("\n2. Listing available tools...")
    tools_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }

    try:
        response = session.post(base_url, json=tools_payload)
        print(f"Tools list response status: {response.status_code}")
        print(f"Tools list response: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            if 'result' in response_data and 'tools' in response_data['result']:
                tools = response_data['result']['tools']
                print(f"✓ Found {len(tools)} tools:")
                for i, tool in enumerate(tools, 1):
                    name = tool.get('name', 'Unknown')
                    desc = tool.get('description', 'No description')
                    input_schema = tool.get('inputSchema', {})
                    print(f"  {i}. {name} - {desc}")
                    print(f"     Input schema: {input_schema}")
            else:
                print("✗ No tools found in response")
        else:
            print("✗ Failed to list tools")
    except Exception as e:
        print(f"Error during tools/list: {e}")

    # Step 3: Test a specific tool call (add_task example)
    print("\n3. Testing add_task tool...")
    add_task_payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "call/tool",
        "params": {
            "name": "add_task",
            "arguments": {
                "title": "Test Task from HTTP Client",
                "description": "Task created via HTTP MCP client",
                "user_id": "test_user_123",
                "completed": False,
                "priority": "medium",
                "category": "test"
            }
        }
    }

    try:
        response = session.post(base_url, json=add_task_payload)
        print(f"Add task response status: {response.status_code}")
        print(f"Add task response: {response.text}")
    except Exception as e:
        print(f"Error during add_task: {e}")

if __name__ == "__main__":
    test_mcp_server_complete()