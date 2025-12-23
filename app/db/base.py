"""
Database base configuration module.

This module imports and exposes the SQLAlchemy Base class and all models.
This ensures all models are registered with SQLAlchemy's metadata before
creating database tables.

IMPORTANT: Every new model MUST be imported here, otherwise:
- Alembic won't detect the model for migrations
- The corresponding database table won't be created
- You'll get "table doesn't exist" errors at runtime

Import order matters due to Foreign Key dependencies:
1. First, import Base from SQLAlchemy
2. Import models without dependencies (e.g., User)
3. Import models with dependencies (e.g., Category depends on User)
4. This registers all models with Base.metadata
"""
from sqlalchemy.orm import declarative_base

# Create the SQLAlchemy Base class
Base = declarative_base()

# Import all models here so Alembic can detect them
# This is required for automatic migration generation
# Import order: User → Category → Transaction (respecting FK dependencies)
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.chat import Chat  # noqa: F401
# Add future models here following the same pattern