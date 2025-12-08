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
        is_active: Whether the account is active
        is_superuser: Whether the user has admin privileges
    """

    email: Optional[EmailStr] = None
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
    """

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )

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
        created_at: When user was created
        updated_at: When user was last updated
    """

    id: int
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """
    Schema for user data returned by API.

    This is what API clients receive. Excludes sensitive fields
    like hashed_password.

    Attributes:
        id: User's unique identifier
        email: User's email
        is_active: Account status
        is_superuser: Admin status
        created_at: Creation timestamp
    """

    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
