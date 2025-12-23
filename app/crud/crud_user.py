"""
User CRUD operations module.

This module provides CRUD operations specific to the User model.
It inherits from CRUDBase and adds user-specific functionality like
email lookup, password hashing, authentication, and login tracking.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from sqlalchemy import update
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
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            obj_in: UserCreate schema with email and plain password

        Returns:
            User: The created user with ID and hashed password
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )

        db.add(db_obj)
        db.commit() # Ensures data persistence for duplicate checks
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user's attributes safely.

        If the password is included in the update data, it is hashed automatically
        before saving.

        Args:
            db: The database session.
            db_obj: The existing user object from the database.
            obj_in: The update data (schema or dict).

        Returns:
            User: The updated user instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Check if password needs to be updated and hash it
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User's email
            password: Plain text password to verify

        Returns:
            User: The authenticated user if credentials are correct
            None: If email doesn't exist or password is wrong
        """
        user = self.get_by_email(db, email=email)

        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None

        # Update last login timestamp
        # Using execute update avoids triggering the main updated_at field logic
        db.execute(
            update(User).where(User.id == user.id).values(last_login_at=datetime.now(timezone.utc))
        )
        db.commit()
        db.refresh(user)

        return user

    def is_active(self, user: User) -> bool:
        """
        Check if a user account is active.
        """
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """
        Check if a user has superuser (admin) privileges.
        """
        return user.is_superuser


user = CRUDUser(User)