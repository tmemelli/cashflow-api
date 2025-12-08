"""
User CRUD operations module.

This module provides CRUD operations specific to the User model.
It inherits from CRUDBase and adds user-specific functionality like
email lookup, password hashing, and authentication.
"""

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.

    Inherits standard CRUD operations from CRUDBase and adds
    user-specific methods for authentication and user management.

    Inherited methods (from CRUDBase):
        - get(db, id) - Get user by ID
        - get_multi(db, skip, limit) - Get multiple users
        - update(db, db_obj, obj_in) - Update user
        - remove(db, id) - Delete user

    Additional methods:
        - get_by_email(db, email) - Get user by email
        - create(db, obj_in) - Create user with hashed password
        - authenticate(db, email, password) - Verify credentials
        - is_active(user) - Check if user is active
        - is_superuser(user) - Check if user is admin
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            db: Database session
            email: User's email address

        Returns:
            User: The user if found
            None: If no user with that email exists

        Example:
            >>> user = crud_user.get_by_email(db, email="joao@example.com")
            >>> if user:
            >>>     print(user.id)
        """

        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.

        This method overrides the base create() to hash the password
        before storing it in the database.

        Args:
            db: Database session
            obj_in: UserCreate schema with email and plain password

        Returns:
            User: The created user with ID and hashed password

        Example:
            >>> user_in = UserCreate(email="test@example.com", password="secret123")
            >>> user = crud_user.create(db, obj_in=user_in)
            >>> print(user.hashed_password)  # Will be bcrypt hash
        """

        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        This is used during login to verify credentials.

        Args:
            db: Database session
            email: User's email
            password: Plain text password to verify

        Returns:
            User: The authenticated user if credentials are correct
            None: If email doesn't exist or password is wrong

        Example:
            >>> user = crud_user.authenticate(
            >>>     db, email="joao@example.com", password="secret123"
            >>> )
            >>> if user:
            >>>     print("Login successful!")
            >>> else:
            >>>     print("Invalid credentials!")
        """

        user = self.get_by_email(db, email=email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def is_active(self, user: User) -> bool:
        """
        Check if a user account is active.

        Args:
            user: User instance

        Returns:
            bool: True if user is active, False otherwise

        Example:
            >>> if crud_user.is_active(user):
            >>>     print("User can access the system")
        """

        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """
        Check if a user has superuser (admin) privileges.

        Args:
            user: User instance

        Returns:
            bool: True if user is superuser, False otherwise

        Example:
            >>> if crud_user.is_superuser(user):
            >>>     print("User has admin access")
        """

        return user.is_superuser


user = CRUDUser(User)
