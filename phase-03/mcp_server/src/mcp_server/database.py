from sqlmodel import create_engine, Session
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


def init_db():
    """
    Initialize the database by creating all tables.
    This should be called when starting the application.
    """
    from .models import Task  # Import here to avoid circular imports

    # Create all tables defined in the models
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)