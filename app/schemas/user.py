"""
User schemas module.

This module defines Pydantic schemas for User data validation.
Schemas control what data can be sent to and received from the API.

Schema hierarchy:
- UserBase: Common attributes shared by all schemas
- UserCreate: Data required to create a new user
- UserUpdate: Data that can be updated (all optional)
- UserInDB: Complete user data as stored in database (includes hashed_password)
- User: User data returned by API (excludes sensitive fields)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """
    Base User schema with common attributes.

    This schema contains fields that are common across
    different User operations.

    Attributes:
        email: User's email address (validated format)
        full_name: User's full name
        is_active: Whether the account is active
        is_superuser: Whether the user has admin privileges
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Used when a new user registers. Requires email and password.
    Password will be hashed before storing in database.

    Attributes:
        email: Required email address
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
    """

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )
    full_name: str = Field(..., min_length=1, max_length=150, description="User's full name")

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """
        Normalize email to lowercase and remove leading/trailing spaces.
        
        This ensures:
        - USER@example.com becomes user@example.com
        - Prevents duplicate accounts with different cases
        - Removes accidental whitespace
        """
        return v.lower().strip()

class UserUpdate(UserBase):
    """
    Schema for updating an existing user.

    All fields are optional - only provided fields will be updated.

    Attributes:
        email: Optional new email
        password: Optional new password
        is_active: Optional new active status
        is_superuser: Optional new superuser status
    """

    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """
    Schema representing user as stored in database.

    Includes all fields from the database including sensitive data.
    This schema is used internally, never sent to API clients.

    Attributes:
        id: User's unique identifier
        email: User's email
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        is_deleted: Soft delete flag
        created_at: When user was created
        updated_at: When user was last updated
        last_login_at: When user last logged in
    """

    id: int
    email: EmailStr
    hashed_password: str
    full_name: str
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """
    Schema for user data returned by API.

    This is what API clients receive. Excludes only hashed_password.
    All other database fields are included.

    Attributes:
        id: User's unique identifier
        email: User's email
        full_name: User's full name
        is_active: Account status
        is_superuser: Admin status
        is_deleted: Soft delete flag
        created_at: Creation timestamp
        updated_at: Profile update timestamp
        last_login_at: Last login timestamp
    """

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
