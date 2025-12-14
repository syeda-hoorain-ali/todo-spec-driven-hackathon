#!/usr/bin/env python3
"""
Test script to verify the full workflow of the secured todo API
"""
import requests
import json
from datetime import datetime, timedelta
import os
import sys
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.auth.jwt import create_access_token

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_full_workflow():
    print("Testing full workflow...")

    # Create a JWT token for user 1
    user_id = 1
    token_data = {"user_id": user_id, "sub": str(user_id)}
    token = create_access_token(data=token_data)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"Using token for user {user_id}")

    # 1. Create a task
    print("\n1. Creating a task...")
    create_response = requests.post(
        f"{BASE_URL}/api/{user_id}/tasks",
        json={"title": "Test Task", "description": "This is a test task"},
        headers=headers
    )
    print(f"Create task response: {create_response.status_code}")
    if create_response.status_code == 200:
        created_task = create_response.json()
        task_id = created_task['id']
        print(f"Created task with ID: {task_id}")
        print(f"Task: {created_task}")
    else:
        print(f"Failed to create task: {create_response.text}")
        return False

    # 2. Read the task
    print("\n2. Reading the task...")
    read_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    print(f"Read task response: {read_response.status_code}")
    if read_response.status_code == 200:
        read_task = read_response.json()
        print(f"Read task: {read_task}")
    else:
        print(f"Failed to read task: {read_response.text}")
        return False

    # 3. Update the task
    print("\n3. Updating the task...")
    update_response = requests.put(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        json={"title": "Updated Test Task", "description": "This is an updated test task"},
        headers=headers
    )
    print(f"Update task response: {update_response.status_code}")
    if update_response.status_code == 200:
        updated_task = update_response.json()
        print(f"Updated task: {updated_task}")
    else:
        print(f"Failed to update task: {update_response.text}")
        return False

    # 4. Mark as complete
    print("\n4. Marking task as complete...")
    complete_response = requests.patch(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}/complete",
        headers=headers
    )
    print(f"Mark complete response: {complete_response.status_code}")
    if complete_response.status_code == 200:
        completed_task = complete_response.json()
        print(f"Completed task: {completed_task}")
        assert completed_task['completed'] == True, "Task should be marked as completed"
    else:
        print(f"Failed to mark task as complete: {complete_response.text}")
        return False

    # 5. Create another task for search/filter testing
    print("\n5. Creating additional tasks for search/filter...")
    task2_response = requests.post(
        f"{BASE_URL}/api/{user_id}/tasks",
        json={"title": "Shopping Task", "description": "Buy groceries for the week"},
        headers=headers
    )
    task3_response = requests.post(
        f"{BASE_URL}/api/{user_id}/tasks",
        json={"title": "Work Task", "description": "Prepare meeting agenda"},
        headers=headers
    )

    if task2_response.status_code == 200 and task3_response.status_code == 200:
        task2 = task2_response.json()
        task3 = task3_response.json()
        print(f"Created additional tasks: {task2['id']}, {task3['id']}")
    else:
        print(f"Failed to create additional tasks: {task2_response.text}, {task3_response.text}")
        return False

    # 6. Search tasks
    print("\n6. Searching tasks for 'groceries'...")
    search_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks",
        params={"keyword": "groceries"},
        headers=headers
    )
    print(f"Search response: {search_response.status_code}")
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"Found {search_results['count']} tasks matching 'groceries'")
        print(f"Search results: {len(search_results['tasks'])} tasks")
        if len(search_results['tasks']) > 0:
            print(f"First result: {search_results['tasks'][0]['title']}")
    else:
        print(f"Failed to search tasks: {search_response.text}")
        return False

    # 7. Filter tasks by completion status
    print("\n7. Filtering tasks by completion status (completed=true)...")
    filter_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks",
        params={"completed": "true"},
        headers=headers
    )
    print(f"Filter response: {filter_response.status_code}")
    if filter_response.status_code == 200:
        filter_results = filter_response.json()
        print(f"Found {filter_results['count']} completed tasks")
        print(f"Completed tasks: {len(filter_results['tasks'])}")
    else:
        print(f"Failed to filter tasks: {filter_response.text}")
        return False

    # 8. Delete the task
    print("\n8. Deleting the original task...")
    delete_response = requests.delete(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    print(f"Delete task response: {delete_response.status_code}")
    if delete_response.status_code == 200:
        delete_result = delete_response.json()
        print(f"Delete result: {delete_result}")
    else:
        print(f"Failed to delete task: {delete_response.text}")
        return False

    # 9. Verify the task was deleted
    print("\n9. Verifying task was deleted...")
    verify_response = requests.get(
        f"{BASE_URL}/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    print(f"Verify deletion response: {verify_response.status_code}")
    if verify_response.status_code == 404:
        print("Task was successfully deleted (404 Not Found)")
    else:
        print(f"Unexpected response when verifying deletion: {verify_response.status_code}")
        return False

    print("\n✅ All workflow tests passed!")
    return True

if __name__ == "__main__":
    success = test_full_workflow()
    if not success:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")