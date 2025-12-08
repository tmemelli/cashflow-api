"""
Category model module.

This module defines the Category model for transaction categorization.
Categories can be system-default or user-created.
Each category is specific to either income or expense transactions.

System categories (is_default=True, user_id=NULL):
- Food, Transport, Entertainment, Health, etc (for expenses)
- Salary, Freelance, Investments, Gifts, etc (for incomes)

User categories (is_default=False, user_id set):
- Custom categories created by each user
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class CategoryType(str, enum.Enum):
    """
    Enum for category types.
    
    Values:
        INCOME: Category for income transactions (e.g., Salary, Freelance)
        EXPENSE: Category for expense transactions (e.g., Food, Transport)
    """
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """
    Category model for organizing transactions.
    
    Categories can be:
    1. System default (is_default=True, user_id=NULL) - available to all users
    2. User-created (is_default=False, user_id set) - specific to one user
    
    Each category has a type (income or expense) to separate revenue from costs.
    
    Attributes:
        id: Primary key
        name: Category name (e.g., "Food", "Salary")
        type: Whether this is for income or expense (CategoryType enum)
        is_default: Whether this is a system category (True) or user-created (False)
        user_id: Owner of the category (NULL for system categories, set for user categories)
        created_at: When category was created
        updated_at: When category was last modified
        
    Relationships:
        owner: The User who created this category (NULL for system categories)
        transactions: List of Transaction records using this category
    
    Examples:
        System category:
        >>> food_category = Category(name="Food", type=CategoryType.EXPENSE, is_default=True, user_id=None)
        
        User category:
        >>> custom_category = Category(name="Uber", type=CategoryType.EXPENSE, is_default=False, user_id=1)
    """
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    owner = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")