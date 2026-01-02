from typing import Any, Dict, List
import requests
import json
import re

id_counter = 1

def send_mcp_request(method: str, params: Dict[str, Any], session_id=None):
    """Helper function to send a JSON-RPC request to an MCP server."""
    global id_counter
    id_counter += 1
    base_url = "http://127.0.0.1:8000/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": id_counter, # Use a unique ID for each request
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


def extract_task_id_from_response(response_text):
    """Extract task ID from the response text."""
    try:
        response_json = json.loads(response_text)
        if 'result' in response_json and 'structuredContent' in response_json['result']:
            structured_content = response_json['result']['structuredContent']
            if 'task_id' in structured_content:
                return structured_content['task_id']
    except:
        pass

    # Fallback: try to extract from text content
    try:
        response_json = json.loads(response_text)
        if 'result' in response_json and 'content' in response_json['result']:
            content = response_json['result']['content']
            if content and len(content) > 0 and 'text' in content[0]:
                text = content[0]['text']
                data = json.loads(text)
                if 'task_id' in data:
                    return data['task_id']
    except:
        pass

    return None


def extract_tasks_from_response(response_text):
    """Extract task ID from the response text."""
    try:
        response_json = json.loads(response_text)
        if 'result' in response_json and 'structuredContent' in response_json['result']:
            structured_content: Dict[str, List[Dict[str, Any]]] = response_json['result']['structuredContent']
            tasks = structured_content['tasks']
            return tasks
    except:
        pass

    return []


def test_full_task_workflow():
    """Test the complete task workflow: add, list, update, complete, delete"""
    print("Testing complete task workflow...")

    # Initialize and get session ID
    init_response = send_mcp_request(
        "initialize",
        {"protocolVersion": "2025-10-05", "capabilities": {}, "clientInfo": {"name": "workflow-test", "version": "0.0.0"}}
    )

    if not init_response:
        print("Failed to initialize MCP server")
        return

    session_id = init_response.headers.get("mcp-session-id")
    if not session_id:
        print("Failed to get session ID from initialization")
        session_id = ""

    print(f"Session ID: {session_id}")

    # Step 1: Add a task
    print("\n1. Adding a task...")
    add_response = send_mcp_request(
        "tools/call",
        {
            "name": "add_task",
            "arguments": {
                "request": {
                    "title": "Workflow Test Task",
                    "description": "Task for complete workflow test",
                    "user_id": "workflow_test_user",
                    "completed": False,
                    "priority": "high",
                    "category": "workflow"
                }
            }
        },
        session_id
    )

    if not add_response:
        print("Failed to add task")
        return

    print(f"Add task response: {add_response.status_code}")
    task_id = extract_task_id_from_response(add_response.text)
    print(f"Created task ID: {task_id}")

    if not task_id:
        print("Failed to extract task ID from add response")
        return

    # Step 2: List tasks to verify the task exists
    print(f"\n2. Listing tasks to verify task {task_id} exists...")
    list_response = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "workflow_test_user",
                    "status": None,
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response:
        print(f"List tasks response: {list_response.status_code}")
        # Check if our task is in the list
        try:
            response_json = json.loads(list_response.text)
            tasks = extract_tasks_from_response(response_json)
            our_task = next((t for t in tasks if t['id'] == task_id), None)
            if our_task:
                print(f"✓ Task {task_id} found in list: {our_task['title']}")
            else:
                print(f"✗ Task {task_id} not found in list")
        except Exception as e:
            print(f"Could not parse list response: {e}")

    # Step 3: Update the task
    print(f"\n3. Updating task {task_id}...")
    update_response = send_mcp_request(
        "tools/call",
        {
            "name": "update_task",
            "arguments": {
                "task_id": task_id,
                "user_id": "workflow_test_user",
                "request": {
                    "title": "Updated Workflow Test Task",
                    "priority": "low"
                }
            }
        },
        session_id
    )

    if update_response:
        print(f"Update task response: {update_response.status_code}")
        print(f"Update response: {update_response.text}")

    # Step 4: List tasks again to verify update
    print(f"\n4. Listing tasks to verify update for task {task_id}...")
    list_response_after_update = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "workflow_test_user",
                    "status": None,
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response_after_update:
        print(f"List tasks after update response: {list_response_after_update.status_code}")
        try:
            response_json = json.loads(list_response_after_update.text)
            tasks = extract_tasks_from_response(response_json)
            our_task = next((t for t in tasks if t['id'] == task_id), None)
            if our_task:
                print(f"✓ Updated task {task_id}: {our_task['title']}, priority: {our_task['priority']}")
            else:
                print(f"✗ Updated task {task_id} not found in list")
        except Exception as e:
            print(f"Could not parse list response after update: {e}")

    # Step 5: Complete the task
    print(f"\n5. Completing task {task_id}...")
    complete_response = send_mcp_request(
        "tools/call",
        {
            "name": "complete_task",
            "arguments": {
                "request": {
                    "task_id": task_id,
                    "user_id": "workflow_test_user"
                }
            }
        },
        session_id
    )

    if complete_response:
        print(f"Complete task response: {complete_response.status_code}")
        print(f"Complete response: {complete_response.text}")

    # Step 6: List tasks to verify completion
    print(f"\n6. Listing tasks to verify completion of task {task_id}...")
    list_response_after_completion = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "workflow_test_user",
                    "status": "completed",  # Filter for completed tasks
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response_after_completion:
        print(f"List tasks after completion (completed only) response: {list_response_after_completion.status_code}")
        try:
            response_json = json.loads(list_response_after_completion.text)
            tasks = extract_tasks_from_response(response_json)
            completed_task = next((t for t in tasks if t['id'] == task_id), None)
            if completed_task:
                print(f"✓ Completed task {task_id} found: {completed_task['title']}, completed: {completed_task['completed']}")
            else:
                print(f"✗ Completed task {task_id} not found in completed tasks list")
                # Check in all tasks list
                all_tasks_response = send_mcp_request(
                    "tools/call",
                    {
                        "name": "list_tasks",
                        "arguments": {
                            "request": {
                                "user_id": "workflow_test_user",
                                "status": None,
                                "priority": None,
                                "category": None,
                                "search": None,
                                "sort_by": None,
                                "sort_order": "asc"
                            }
                        }
                    },
                    session_id
                )
                if all_tasks_response:
                    try:
                        all_json = json.loads(all_tasks_response.text)
                        all_tasks = extract_tasks_from_response(all_json)
                        our_task = next((t for t in all_tasks if t['id'] == task_id), None)
                        if our_task:
                            print(f"✓ Task {task_id} found in all tasks: completed={our_task['completed']}")
                    except:
                        pass
        except Exception as e:
            print(f"Could not parse list response after completion: {e}")

    # Step 7: Delete the task
    print(f"\n7. Deleting task {task_id}...")
    delete_response = send_mcp_request(
        "tools/call",
        {
            "name": "delete_task",
            "arguments": {
                "request": {
                    "task_id": task_id,
                    "user_id": "workflow_test_user"
                }
            }
        },
        session_id
    )

    if delete_response:
        print(f"Delete task response: {delete_response.status_code}")
        print(f"Delete response: {delete_response.text}")

    # Step 8: List tasks to verify deletion
    print(f"\n8. Listing tasks to verify deletion of task {task_id}...")
    list_response_after_deletion = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "workflow_test_user",
                    "status": None,
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response_after_deletion:
        print(f"List tasks after deletion response: {list_response_after_deletion.status_code}")
        try:
            response_json = json.loads(list_response_after_deletion.text)
            tasks = extract_tasks_from_response(response_json)
            our_task = next((t for t in tasks if t['id'] == task_id), None)
            if not our_task:
                print(f"✓ Task {task_id} successfully deleted (not found in list)")
            else:
                print(f"✗ Task {task_id} still exists after deletion")
        except Exception as e:
            print(f"Could not parse list response after deletion: {e}")

    print("\nComplete task workflow test finished!")


def test_recurring_task_workflow():
    """Test the recurring task workflow"""
    print("\n\nTesting recurring task workflow...")

    # Initialize and get session ID
    init_response = send_mcp_request(
        "initialize",
        {"protocolVersion": "2025-10-05", "capabilities": {}, "clientInfo": {"name": "recurring-test", "version": "0.0.0"}}
    )

    if not init_response:
        print("Failed to initialize MCP server")
        return

    session_id = init_response.headers.get("mcp-session-id")
    if not session_id:
        print("Failed to get session ID from initialization")
        session_id = ""

    print(f"Session ID: {session_id}")

    # Step 1: Add a recurring task
    print("\n1. Adding a recurring task...")
    add_response = send_mcp_request(
        "tools/call",
        {
            "name": "add_task",
            "arguments": {
                "request": {
                    "title": "Daily Recurring Task",
                    "description": "A task that repeats daily",
                    "user_id": "recurring_test_user",
                    "completed": False,
                    "priority": "medium",
                    "category": "recurring",
                    "is_recurring": True,
                    "recurrence_pattern": "daily",
                    "recurrence_interval": 1
                }
            }
        },
        session_id
    )

    if not add_response:
        print("Failed to add recurring task")
        return

    print(f"Add recurring task response: {add_response.status_code}")
    task_id = extract_task_id_from_response(add_response.text)
    print(f"Created recurring task ID: {task_id}")

    if not task_id:
        print("Failed to extract task ID from recurring task add response")
        return

    # Step 2: List tasks to verify the recurring task exists
    print(f"\n2. Listing tasks to verify recurring task {task_id} exists...")
    list_response = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "recurring_test_user",
                    "status": None,
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response:
        print(f"List tasks response: {list_response.status_code}")
        try:
            response_json = json.loads(list_response.text)
            if 'result' in response_json and 'structuredContent' in response_json['result']:
                tasks_data: Dict[str, List[Dict[str, Any]]] = response_json['result']['structuredContent']
                tasks = tasks_data['tasks']
                our_task = next((t for t in tasks if t['id'] == task_id), None)
                if our_task:
                    print(f"✓ Recurring task {task_id} found: {our_task['title']}")
                    print(f"  Is recurring: {our_task['is_recurring']}")
                    print(f"  Recurrence pattern: {our_task['recurrence_pattern']}")
                else:
                    print(f"✗ Recurring task {task_id} not found in list")
        except Exception as e:
            print(f"Could not parse list response: {e}")

    # Step 3: Complete the recurring task (this should create a new occurrence)
    print(f"\n3. Completing recurring task {task_id} (should create next occurrence)...")
    complete_response = send_mcp_request(
        "tools/call",
        {
            "name": "complete_task",
            "arguments": {
                "request": {
                    "task_id": task_id,
                    "user_id": "recurring_test_user"
                }
            }
        },
        session_id
    )

    if complete_response:
        print(f"Complete recurring task response: {complete_response.status_code}")
        print(f"Complete response: {complete_response.text}")

    # Step 4: List tasks to verify a new occurrence was created
    print(f"\n4. Listing tasks to verify new occurrence was created...")
    list_response_after_completion = send_mcp_request(
        "tools/call",
        {
            "name": "list_tasks",
            "arguments": {
                "request": {
                    "user_id": "recurring_test_user",
                    "status": "pending",  # Look for pending tasks
                    "priority": None,
                    "category": None,
                    "search": None,
                    "sort_by": None,
                    "sort_order": "asc"
                }
            }
        },
        session_id
    )

    if list_response_after_completion:
        print(f"List tasks after completion response: {list_response_after_completion.status_code}")
        try:
            response_json = json.loads(list_response_after_completion.text)
            tasks = extract_tasks_from_response(response_json)
            # Find tasks with the same title as our original recurring task
            recurring_tasks = [t for t in tasks if t['title'] == "Daily Recurring Task"]
            if len(recurring_tasks) > 1:
                print(f"✓ New occurrence created! Found {len(recurring_tasks)} tasks with title 'Daily Recurring Task'")
                for task in recurring_tasks:
                    print(f"  - Task ID {task['id']}: completed={task['completed']}, created_at={task['created_at']}")
            elif len(recurring_tasks) == 1:
                print(f"✓ Original recurring task found but no new occurrence created yet")
                task = recurring_tasks[0]
                print(f"  - Task ID {task['id']}: completed={task['completed']}")
            else:
                print("✗ No recurring tasks found with expected title")
        except Exception as e:
            print(f"Could not parse list response after completion: {e}")

    print("\nRecurring task workflow test finished!")


if __name__ == "__main__":
    test_full_task_workflow()
    test_recurring_task_workflow()
