"""
Database session management module.

This module handles SQLAlchemy database connections and session management.
It provides the engine and session factory for database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Database engine with SQLite compatibility handling
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    ),
)

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
