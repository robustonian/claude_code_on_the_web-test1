"""
Database connection and session management.
"""
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine
from app.models import URLMapping

# Production database
DATABASE_URL = "sqlite:///./urlshortener.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Test database (file-based for reliability)
test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for production use."""
    with Session(engine) as session:
        yield session


def get_test_db() -> Generator[Session, None, None]:
    """
    Get test database session.

    This creates tables if needed and yields a session.
    Tables persist across multiple calls within the same test.
    """
    # Create tables if they don't exist
    SQLModel.metadata.create_all(test_engine)

    # Use a single session for the entire test
    with Session(test_engine) as session:
        yield session


def reset_test_db():
    """Reset the test database between tests."""
    # Drop all tables to ensure clean state for next test
    SQLModel.metadata.drop_all(test_engine)
