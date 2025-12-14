from sqlmodel import SQLModel
from .database import engine
from ..models.task import Task


def create_db_and_tables():
    """Create database tables based on models."""
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables created successfully!")
    