from typing import Optional
from sqlmodel import create_engine, SQLModel, Session
import os

# Database configuration
DATABASE_URL = "sqlite:///./farmer_backend.db"

# Create SQLite engine with check_same_thread=False for compatibility
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
