"""
Test to verify the main application functionality
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


def test_main_app_routes():
    """Test that the main application has the expected routes"""
    # Get all route paths
    route_paths = [route.path for route in app.routes]

    # Check that main routes are present
    expected_routes = ['/', '/health', '/tasks']
    for route in expected_routes:
        assert route in route_paths, f"Expected route {route} to be present, available routes: {route_paths}"

    print(f"Found expected routes: {expected_routes}")


def test_health_endpoint():
    """Test that the health endpoint is accessible"""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

    print(f"Health endpoint accessible, returned status: {response.status_code}")


if __name__ == "__main__":
    test_main_app_routes()
    test_health_endpoint()
    print("All tests passed!")
