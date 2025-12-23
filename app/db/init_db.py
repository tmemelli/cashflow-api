"""
Database initialization module.

This module provides functions to initialize the database with default data.
It handles the seeding of system-default categories and ensures idempotency
(can be run multiple times without duplicating data).

Usage:
    from app.db.init_db import init_db
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    init_db(db)
    db.close()
"""
import logging
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryType

# Configure logger
logger = logging.getLogger(__name__)


def create_default_categories(db: Session) -> None:
    """
    Create default system categories if they don't exist.
    
    Creates common categories for:
    - Expenses: Food, Transport, Health, etc.
    - Incomes: Salary, Freelance, Investments, etc.
    
    These categories are marked as default (is_default=True) and global (user_id=None).
    
    Args:
        db (Session): Database session.
    """
    logger.info("Checking for default system categories...")

    # Define standard categories with strong typing
    default_categories = [
        # --- INCOME Categories ---
        {"name": "Salary", "type": CategoryType.INCOME},
        {"name": "Investments", "type": CategoryType.INCOME},
        {"name": "Freelance", "type": CategoryType.INCOME},
        {"name": "Gifts", "type": CategoryType.INCOME},
        {"name": "Other Income", "type": CategoryType.INCOME},
        
        # --- EXPENSE Categories ---
        {"name": "Food", "type": CategoryType.EXPENSE},
        {"name": "Transport", "type": CategoryType.EXPENSE},
        {"name": "Housing", "type": CategoryType.EXPENSE},
        {"name": "Health", "type": CategoryType.EXPENSE},
        {"name": "Entertainment", "type": CategoryType.EXPENSE},
        {"name": "Education", "type": CategoryType.EXPENSE},
        {"name": "Shopping", "type": CategoryType.EXPENSE},
        {"name": "Utilities", "type": CategoryType.EXPENSE},
        {"name": "Travel", "type": CategoryType.EXPENSE},
    ]

    created_count = 0

    for data in default_categories:
        # Idempotency Check:
        # Query to see if this specific system category already exists.
        # We filter by name, type, and explicitly check is_default=True.
        existing_category = db.query(Category).filter(
            Category.name == data["name"],
            Category.type == data["type"],
            Category.is_default == True
        ).first()

        if not existing_category:
            category = Category(
                name=data["name"],
                type=data["type"],
                is_default=True,  # Mark as system category
                user_id=None      # Global category (no specific owner)
            )
            db.add(category)
            created_count += 1
            logger.debug(f"Queued creation of category: {data['name']}")

    # Commit only if changes were made
    if created_count > 0:
        db.commit()
        logger.info(f"✅ Successfully seeded {created_count} system categories.")
    else:
        logger.info("ℹ️ System categories are already up to date.")


def init_db(db: Session) -> None:
    """
    Initialize database with all default data.
    
    This is the main entry point for database seeding. It orchestrates
    the creation of categories, admins, and other initial data.
    
    Args:
        db: Database session
    """
    logger.info("Starting database initialization...")
    
    # 1. Seed Categories
    create_default_categories(db)
    
    # Future: 2. Create Superuser
    # create_superuser(db)
    
    logger.info("Database initialization completed.")