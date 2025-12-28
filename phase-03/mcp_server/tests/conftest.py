import pytest
import sys
import os
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from fastapi.testclient import TestClient

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the database URL to use SQLite for testing
with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
    from src.mcp_server.main import mcp
    from src.mcp_server.database import engine
    from src.mcp_server.models import Task

# For tests, we'll use the mcp app directly
app = mcp


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture():
    client = TestClient(app)
    yield client
