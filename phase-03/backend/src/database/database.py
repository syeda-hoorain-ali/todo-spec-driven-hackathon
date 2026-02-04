from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
from ..config.settings import settings


# Load environment variables
load_dotenv(find_dotenv())

# Create the database engine
# Only enable SQL echoing in development or if debug is True
echo_sql = settings.environment.lower() != "production" or settings.debug
engine = create_engine(
    settings.database_url, 
    echo=echo_sql,
    poolclass=QueuePool,  # Use connection pooling, NullPool for serverless (if on Vercel/Lambda):
    pool_size=5,          # Number of connections to keep
    max_overflow=10,      # Max additional connections
    pool_pre_ping=True,   # Verify connection before using (IMPORTANT!)
    pool_recycle=3600,    # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)


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
