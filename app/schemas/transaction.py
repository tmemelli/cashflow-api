"""
Transaction schemas module.

This module defines Pydantic schemas for Transaction validation and serialization.

Schemas:
- TransactionBase: Base schema with common fields
- TransactionCreate: Schema for creating a new transaction
- TransactionUpdate: Schema for updating an existing transaction
- TransactionResponse: Schema for returning transaction data to client
- TransactionWithCategory: Schema with full category details
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.transaction import TransactionType


class TransactionBase(BaseModel):
    """
    Base schema with common transaction fields.
    
    Attributes:
        type: Transaction type (income or expense)
        amount: Transaction amount (positive decimal)
        description: Optional description
        date: Transaction date
        category_id: Optional category ID
    """
    type: TransactionType
    amount: Decimal = Field(..., gt=0, description="Amount must be greater than 0")
    description: Optional[str] = Field(None, max_length=500)
    date: date
    category_id: Optional[int] = None


class TransactionCreate(BaseModel):
    """
    Schema for creating or restoring a transaction.
    
    Two modes of operation:
    
    1. CREATE NEW TRANSACTION (all fields required except id):
        {
            "type": "expense",
            "amount": 150.50,
            "description": "Grocery shopping",
            "date": "2025-01-15",
            "category_id": 2
        }
    
    2. RESTORE DELETED TRANSACTION (only id provided):
        {
            "id": 4
        }
        - If transaction with id=4 exists and is deleted, it will be restored
        - Cannot provide other fields when restoring by id
    
    Attributes:
        id: Optional - Only for restoring deleted transactions
        type: Transaction type (required when creating new)
        amount: Transaction amount (required when creating new)
        description: Optional description
        date: Transaction date (required when creating new)
        category_id: Optional category ID
    """
    id: Optional[int] = Field(None, description="Provide only this field to restore a deleted transaction")
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, gt=0, description="Amount must be greater than 0")
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None
    category_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    """
    Schema for updating an existing transaction.
    
    All fields are optional (partial update).
    User can update only the fields they want to change.
    is_deleted is NOT updatable via API (use DELETE endpoint instead).
    
    Example:
        {
            "amount": 175.00,
            "description": "Grocery shopping at Walmart"
        }
    """
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, gt=0, description="Amount must be greater than 0")
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None
    category_id: Optional[int] = None


class TransactionResponse(TransactionBase):
    """
    Schema for returning transaction data to client.
    
    Includes all fields except is_deleted (internal use only).
    
    Attributes:
        id: Transaction ID
        user_id: Owner ID
        type: Transaction type
        amount: Transaction amount
        description: Description (may be None)
        date: Transaction date
        category_id: Category ID (may be None)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example response:
        {
            "id": 1,
            "user_id": 5,
            "type": "expense",
            "amount": "150.50",
            "description": "Grocery shopping",
            "date": "2025-01-15",
            "category_id": 2,
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    """
    id: int
    user_id: int
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    date: date
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransactionWithCategory(TransactionResponse):
    """
    Extended schema with full category details.
    
    Useful for list views where you want to show category name
    without additional API calls.
    
    Example response:
        {
            "id": 1,
            "user_id": 5,
            "type": "expense",
            "amount": "150.50",
            "description": "Grocery shopping",
            "date": "2025-01-15",
            "category_id": 2,
            "category_name": "Food",
            "category_type": "expense",
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    """
    category_name: Optional[str] = None
    category_type: Optional[str] = None