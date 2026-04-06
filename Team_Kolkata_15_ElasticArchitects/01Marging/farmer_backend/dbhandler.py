# Database Connection
# dbhandler.py
"""
Database connection and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import json

# Load database configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    DATABASE_URL = config.get('DATABASE_URL', 'sqlite:///./farmer_backend.db')
else:
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./farmer_backend.db')

# Create engine based on database type
if DATABASE_URL.startswith('sqlite'):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use with FastAPI Depends().
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this once to create all tables defined in models.py
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables (use with caution!).
    Useful for development/testing.
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped!")


def get_session() -> Session:
    """
    Get a database session directly (not for use with FastAPI Depends).
    Remember to close the session when done.
    
    Returns:
        Database session
    """
    return SessionLocal()


# For backward compatibility with existing code
def get_db_connection():
    """Legacy function name - returns session"""
    return get_session()
