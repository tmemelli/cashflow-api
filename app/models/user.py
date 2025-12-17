"""
User model module.

This module defines the User model which represents the users table
in the database. Users can have multiple transactions.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    """
    User model class.

    Represents a user in the system. Each user can create financial transactions.

    Attributes:
        id: Primary key, auto-incremented integer
        email: User's email address (unique, required)
        hashed_password: Bcrypt hashed password (required)
        full_name: User's full name (required)
        is_active: Whether the user account is active (default: True)
        is_superuser: Whether the user has admin privileges (default: False)
        is_deleted: Soft delete flag (default: False)
        created_at: Timestamp when user was created (auto-generated)
        updated_at: Timestamp when user profile is updated (manual update only)
        last_login_at: Timestamp of last successful login (updated on authentication)

    Relationships:
        transactions: One-to-many relationship with Transaction model
        categories: One-to-many relationship with Category model
    """

    __tablename__ = "users"

    # Identification fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(150), nullable=False)

    # Status boolean fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamp fields (func.now() is from sqlalchemy.sql import func)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), nullable=True)  # Manual update only
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    transactions = relationship("Transaction", back_populates="owner")
    categories = relationship("Category", back_populates="owner")
    chats = relationship("Chat", back_populates="user")

    def __repr__(self) -> str:
        """
        String representation of User object for debugging.

        Returns:
            str: Readable representation showing key fields.
        """
        return (
            f"<User(id={self.id}, email='{self.email}', is_active={self.is_active}, "
            f"is_superuser={self.is_superuser}, is_deleted={self.is_deleted})>"
        )