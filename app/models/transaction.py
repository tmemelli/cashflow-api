"""
Transaction model module.

This module defines the Transaction model for financial records.
A transaction can be either an income or an expense.

Transactions are the core of the financial tracking system:
- Income: Money received (salary, freelance, investments, etc)
- Expense: Money spent (food, transport, entertainment, etc)

Features:
- Soft delete: Transactions are never permanently deleted, just marked as deleted
- Historical tracking: All changes are timestamped
- User isolation: Each user only sees their own transactions
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from decimal import Decimal

from app.db.base import Base


class TransactionType(str, enum.Enum):
    """
    Enum for transaction types.
    
    Values:
        INCOME: Money received (e.g., Salary, Freelance payment)
        EXPENSE: Money spent (e.g., Grocery shopping, Rent payment)
    """
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """
    Transaction model for financial records.
    
    Represents a single financial transaction (income or expense).
    Each transaction belongs to a user and optionally to a category.
    
    Attributes:
        id: Primary key
        user_id: Owner of the transaction (FK to users)
        category_id: Category of the transaction (FK to categories, optional)
        type: Whether this is income or expense (TransactionType enum)
        amount: Transaction amount (Decimal, 2 decimal places, e.g., 150.50)
        description: Description of the transaction (optional, max 500 chars)
        date: Date when the transaction occurred (can be future for planning)
        is_deleted: Soft delete flag (True = deleted, False = active)
        created_at: When transaction was created
        updated_at: When transaction was last modified
        
    Relationships:
        owner: The User who created this transaction
        category: The Category assigned to this transaction (optional)
    
    Business Rules:
        - Amount must be positive (> 0)
        - Type must match category type (if category is set)
        - User can only access their own transactions
        - Deleted transactions are hidden but kept for audit
    
    Examples:
        Income transaction:
        >>> salary = Transaction(
        ...     user_id=1,
        ...     category_id=5,
        ...     type=TransactionType.INCOME,
        ...     amount=Decimal("5000.00"),
        ...     description="Monthly salary",
        ...     date=date.today()
        ... )
        
        Expense transaction:
        >>> grocery = Transaction(
        ...     user_id=1,
        ...     category_id=2,
        ...     type=TransactionType.EXPENSE,
        ...     amount=Decimal("150.75"),
        ...     description="Supermarket shopping",
        ...     date=date.today()
        ... )
    """
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(String(500), nullable=True)
    date = Column(Date, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")