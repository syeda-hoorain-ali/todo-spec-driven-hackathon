from sqlmodel import create_engine, Session
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/todo_db")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Get a database session with context manager."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_with_user(user_id: str) -> Generator[Session, None, None]:
    """Get a database session with user context for RLS."""
    with Session(engine) as session:
        # Set the current user ID for RLS policies
        session.execute(f"SET app.current_user_id = '{user_id}'")
        yield session
