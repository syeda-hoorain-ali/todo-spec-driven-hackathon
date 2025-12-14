from sqlmodel import create_engine, Session
from contextlib import contextmanager
from typing import Generator
import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
from ..config.settings import settings

# Load environment variables
load_dotenv(find_dotenv())

# Create the database engine
engine = create_engine(settings.database_url, echo=True)


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
        session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})
        yield session
