"""
Category schemas module.

This module defines Pydantic schemas for Category validation and serialization.

Schemas:
- CategoryBase: Base schema with common fields
- CategoryCreate: Schema for creating a new category
- CategoryUpdate: Schema for updating an existing category
- CategoryResponse: Schema for returning category data to client
- CategoryWithTransactions: Schema with related transactions (optional, for detailed view)
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.category import CategoryType


class CategoryBase(BaseModel):
    """
    Base schema with common category fields.
    
    Attributes:
        name: Category name (e.g., "Food", "Salary")
        type: Category type (income or expense)
    """
    name: str = Field(..., min_length=1, max_length=100)
    type: CategoryType


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.
    
    Inherits all fields from CategoryBase.
    User creates only name and type.
    Other fields (id, user_id, is_default) are set automatically.
    
    Example:
        {
            "name": "Groceries",
            "type": "expense"
        }
    """
    pass


class CategoryUpdate(BaseModel):
    """
    Schema for updating an existing category.
    
    All fields are optional (partial update).
    User can update only the fields they want to change.
    
    Example:
        {
            "name": "Food & Drinks"
        }
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[CategoryType] = None


class CategoryResponse(CategoryBase):
    """
    Schema for returning category data to client.
    
    Includes all fields that should be visible to the user.
    Excludes sensitive data (none in this case).
    
    Attributes:
        id: Category ID
        name: Category name
        type: Category type
        is_default: Whether this is a system category
        user_id: Owner ID (None for system categories)
        is_deleted: Whether category is soft deleted
        deleted_at: When category was deleted (None if active)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example response:
        {
            "id": 1,
            "name": "Food",
            "type": "expense",
            "is_default": false,
            "user_id": 5,
            "is_deleted": false,
            "deleted_at": null,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    """
    id: int
    name: str
    type: CategoryType
    is_default: bool
    user_id: Optional[int] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CategoryWithTransactions(CategoryResponse):
    """
    Extended schema with related transactions.
    
    Optional: Use this for detailed category view with all transactions.
    Useful for endpoints like GET /categories/{id}?include=transactions
    
    Example response:
        {
            "id": 1,
            "name": "Food",
            "type": "expense",
            "is_default": false,
            "user_id": 5,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z",
            "transaction_count": 25
        }
    """
    transaction_count: int = 0