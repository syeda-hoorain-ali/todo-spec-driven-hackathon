"""
Test to verify the ChatKit integration with Neon DB
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path to make it a module
backend_path = str(Path(__file__).parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the app using the installed package structure
from src.main import app


def test_chatkit_routes_exist():
    """Test that the ChatKit routes are accessible"""
    client = TestClient(app)

    # Get all route paths
    route_paths = [route.path for route in app.routes]

    # Check that ChatKit routes are present
    chatkit_routes = [path for path in route_paths if '/chatkit' in path]

    assert len(chatkit_routes) > 0, f"Expected ChatKit routes to be present, but found: {chatkit_routes}"

    # Check that specific ChatKit route patterns exist
    has_conversations_route = any('/api/chatkit/conversations' in path for path in route_paths)
    has_conversation_route = any('/api/chatkit/conversation' in path for path in route_paths)
    has_message_route = '/api/chatkit/message' in route_paths

    assert has_conversations_route, f"Expected conversations route to be present, available routes: {route_paths}"
    assert has_conversation_route, f"Expected conversation route to be present, available routes: {route_paths}"
    assert has_message_route, f"Expected message route to be present, available routes: {route_paths}"

    print(f"Found ChatKit routes: {chatkit_routes}")


def test_chat_routes_exist():
    """Test that the main chat routes are still accessible"""
    client = TestClient(app)

    # Get all route paths
    route_paths = [route.path for route in app.routes]

    # Check that main chat routes are present
    expected_chat_routes = ['/api/chat', '/api/conversations']

    for route in expected_chat_routes:
        assert route in route_paths, f"Expected route {route} to be present, available routes: {route_paths}"

    print(f"Found main chat routes: [r for r in route_paths if 'chat' in r and 'chatkit' not in r]")


if __name__ == "__main__":
    test_chatkit_routes_exist()
    test_chat_routes_exist()
    print("All tests passed!")