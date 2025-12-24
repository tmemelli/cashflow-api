"""
Transaction CRUD operations module.

This module provides database operations for Transaction model.
Includes specific methods for filtering, soft delete, and statistics.
"""
from typing import List, Optional, Any
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.crud.base import CRUDBase
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    """
    CRUD operations for Transaction model.
    
    Inherits basic CRUD from CRUDBase and adds transaction-specific methods:
    - Soft delete (mark as deleted instead of removing)
    - Filter by date_transaction range, type, category
    - Calculate statistics (total income, total expense, balance)
    """
    
    # get_multi_by_user (list user's active transactions)
    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Transaction]:
        """
        Get multiple transactions for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted transactions
            
        Returns:
            List of Transaction objects
            
        Example:
            >>> transactions = crud.transaction.get_multi_by_user(
            ...     db, user_id=1, skip=0, limit=10
            ... )
        """
        query = db.query(self.model).filter(
            Transaction.user_id == user_id
        )
        
        if not include_deleted:
            query = query.filter(Transaction.is_deleted == False)
        
        return (
            query
            .order_by(Transaction.date_transaction.desc(), Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    # get_by_date_range (filter by date_transaction range)
    def get_by_date_range(
        self,
        db: Session,
        *,
        user_id: int,
        start_date: date,
        end_date: date,
        transaction_type: Optional[TransactionType] = None,
        category_id: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transactions within a date_transaction range.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            transaction_type: Optional filter by type (income/expense)
            category_id: Optional filter by category
            
        Returns:
            List of Transaction objects
            
        Example:
            >>> from datetime import date
            >>> transactions = crud.transaction.get_by_date_range(
            ...     db,
            ...     user_id=1,
            ...     start_date=date(2025, 1, 1),
            ...     end_date=date(2025, 1, 31),
            ...     transaction_type=TransactionType.EXPENSE
            ... )
        """
        query = db.query(self.model).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date_transaction >= start_date,
                Transaction.date_transaction <= end_date,
                Transaction.is_deleted == False
            )
        )
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if category_id is not None:
            query = query.filter(Transaction.category_id == category_id)
        
        return query.order_by(Transaction.date_transaction.desc()).all()
    
    # get_statistics (calculate totals)
    def get_statistics(
        self,
        db: Session,
        *,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Calculate financial statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary with statistics:
            {
                "total_income": Decimal,
                "total_expense": Decimal,
                "balance": Decimal,
                "transaction_count": int
            }
            
        Example:
            >>> stats = crud.transaction.get_statistics(db, user_id=1)
            >>> print(stats)
            {
                "total_income": Decimal("5000.00"),
                "total_expense": Decimal("3500.50"),
                "balance": Decimal("1499.50"),
                "transaction_count": 25
            }
        """
        # Base filters aplicados em todas as queries
        base_filters = [
            Transaction.user_id == user_id,
            Transaction.is_deleted == False
        ]
        
        if start_date:
            base_filters.append(Transaction.date_transaction >= start_date)
        if end_date:
            base_filters.append(Transaction.date_transaction <= end_date)
        
        # Calculate total income (query independente)
        total_income = (
            db.query(func.sum(Transaction.amount))
            .filter(and_(*base_filters, Transaction.type == TransactionType.INCOME))
            .scalar()
        ) or Decimal("0.00")
        
        # Calculate total expense (query independente)
        total_expense = (
            db.query(func.sum(Transaction.amount))
            .filter(and_(*base_filters, Transaction.type == TransactionType.EXPENSE))
            .scalar()
        ) or Decimal("0.00")
        
        # Count transactions (query independente)
        transaction_count = (
            db.query(func.count(Transaction.id))
            .filter(and_(*base_filters))
            .scalar()
        ) or 0
        
        # Calculate balance
        balance = total_income - total_expense
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": transaction_count
        }


# Create instance for use in endpoints
transaction = CRUDTransaction(Transaction)