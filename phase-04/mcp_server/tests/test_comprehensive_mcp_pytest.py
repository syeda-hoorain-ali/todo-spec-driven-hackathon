import pytest
import requests
import json
from typing import Any, Dict, List, Literal


class TestMCPComprehensive:
    """Comprehensive tests for MCP server functionality using pytest"""

    def setup_method(self):
        """Setup method to initialize test state"""
        self.id_counter = 1
        self.base_url = "http://127.0.0.1:8000/mcp"
        self.session_id = self._initialize_session()

    def _initialize_session(self):
        """Initialize MCP session and return session ID"""
        payload = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-10-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest-comprehensive-test", "version": "0.0.0"}
            }
        }
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.base_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            return response.headers.get("mcp-session-id", "")
        except requests.exceptions.RequestException as e:
            print(f"Session initialization failed: {e}")
            return ""

    def _send_mcp_request(self, method: str, params: Dict[str, Any], session_id=None):
        """Helper function to send a JSON-RPC request to an MCP server."""
        self.id_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
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
            response = requests.post(self.base_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_add_task(self):
        """Test adding a task"""
        response = self._send_mcp_request(
            "tools/call",
            {
                "name": "add_task",
                "arguments": {
                    "request": {
                        "title": "Test Task from HTTP Client",
                        "description": "Task created via HTTP MCP client",
                        "user_id": "test_user_123",
                        "completed": False,
                        "priority": "medium",
                        "category": "test"
                    }
                }
            },
            self.session_id
        )
        assert response is not None
        assert response.status_code == 200
        result = response.json()
        assert 'result' in result
        assert 'structuredContent' in result['result']
        task_response = result['result']['structuredContent']
        assert 'task_id' in task_response
        assert task_response['status'] == 'created'
        assert task_response['title'] == 'Test Task from HTTP Client'

    def test_list_tasks(self):
        """Test listing tasks"""
        response = self._send_mcp_request(
            "tools/call",
            {
                "name": "list_tasks",
                "arguments": {
                    "request": {
                        "user_id": "test_user_123",
                        "status": None,
                        "priority": None,
                        "category": None,
                        "search": None,
                        "sort_by": None,
                        "sort_order": "asc"
                    }
                }
            },
            self.session_id
        )
        assert response is not None
        assert response.status_code == 200
        result = response.json()
        assert 'result' in result
        assert 'structuredContent' in result['result']
        tasks_response = result['result']['structuredContent']
        assert 'tasks' in tasks_response
        assert isinstance(tasks_response['tasks'], list)

    def test_add_recurring_task(self):
        """Test adding a recurring task"""
        response = self._send_mcp_request(
            "tools/call",
            {
                "name": "add_task",
                "arguments": {
                    "request": {
                        "title": "Recurring Task",
                        "description": "A task that repeats daily",
                        "user_id": "test_user_123",
                        "completed": False,
                        "priority": "medium",
                        "category": "recurring",
                        "is_recurring": True,
                        "recurrence_pattern": "daily",
                        "recurrence_interval": 1
                    }
                }
            },
            self.session_id
        )
        assert response is not None
        assert response.status_code == 200
        result = response.json()
        assert 'result' in result
        assert 'structuredContent' in result['result']
        task_response = result['result']['structuredContent']
        assert 'task_id' in task_response
        assert task_response['status'] == 'created'
        assert task_response['title'] == 'Recurring Task'

    def test_list_tasks_with_filters(self):
        """Test listing tasks with filters"""
        response = self._send_mcp_request(
            "tools/call",
            {
                "name": "list_tasks",
                "arguments": {
                    "request": {
                        "user_id": "test_user_123",
                        "status": "pending",
                        "category": "test",
                        "priority": "medium",
                        "search": None,
                        "sort_by": None,
                        "sort_order": "asc"
                    }
                }
            },
            self.session_id
        )
        assert response is not None
        assert response.status_code == 200
        result = response.json()
        assert 'result' in result
        assert 'structuredContent' in result['result']
        tasks_response = result['result']['structuredContent']
        assert 'tasks' in tasks_response
        assert isinstance(tasks_response['tasks'], list)

    @pytest.mark.parametrize("priority,category", [
        ("high", "test"),
        ("medium", "recurring"),
        ("low", "recurring_test")
    ])
    def test_list_tasks_with_different_filters(self, priority, category):
        """Test listing tasks with different filter combinations using parametrization"""
        response = self._send_mcp_request(
            "tools/call",
            {
                "name": "list_tasks",
                "arguments": {
                    "request": {
                        "user_id": "test_user_123",
                        "status": "pending",
                        "category": category,
                        "priority": priority,
                        "search": None,
                        "sort_by": None,
                        "sort_order": "asc"
                    }
                }
            },
            self.session_id
        )
        assert response is not None
        assert response.status_code == 200
        result = response.json()
        assert 'result' in result
        assert 'structuredContent' in result['result']
        tasks_response = result['result']['structuredContent']
        assert 'tasks' in tasks_response
        assert isinstance(tasks_response['tasks'], list)
