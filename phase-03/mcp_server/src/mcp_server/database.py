from sqlmodel import create_engine, Session, text
from typing import Generator
from .config import settings


# Create the database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection.
    """
    with Session(engine) as session:
        yield session


def get_session_with_user(user_id: str) -> Generator[Session, None, None]:
    """
    Get a database session with RLS user context set.

    Args:
        user_id: The user ID to set for RLS policies

    Yields:
        Configured database session with RLS context
    """
    with Session(engine) as session:
        # Set the session variable for RLS policies
        session.exec(text("SET app.current_user_id = :user_id"), params={"user_id": user_id})
        yield session
