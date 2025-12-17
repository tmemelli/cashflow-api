"""
Transaction endpoints module.

This module provides REST API endpoints for transaction management.
Handles both income and expense transactions with filtering capabilities.

Endpoints:
- GET /transactions - List user's transactions with filters
- POST /transactions - Create a new transaction
- GET /transactions/{transaction_id} - Get transaction details
- PUT /transactions/{transaction_id} - Update transaction
- DELETE /transactions/{transaction_id} - Soft delete transaction
- GET /transactions/statistics - Get financial statistics
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.crud.crud_transaction import transaction as crud_transaction
from app.crud.crud_category import category as crud_category
from app.models.user import User
from app.models.transaction import TransactionType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionWithCategory
)

router = APIRouter()


# TODO: GET /transactions - List transactions with filters
@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[TransactionType] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    include_deleted: bool = False
):
    """
    List user's transactions with optional filters.
    
    Query Parameters:
    - skip: Number of records to skip (pagination) - default 0
    - limit: Maximum number of records - default 100
    - transaction_type: Filter by type (income/expense) - optional
    - category_id: Filter by category - optional
    - start_date: Filter from date (YYYY-MM-DD) - optional
    - end_date: Filter to date (YYYY-MM-DD) - optional
    - include_deleted: Include soft-deleted transactions - default false
    
    Examples:
        GET /transactions?transaction_type=expense&limit=10
        GET /transactions?start_date=2025-01-01&end_date=2025-01-31
        GET /transactions?category_id=5
    """
    # If any date filter is provided, use date range query
    if start_date or end_date:
        # Set defaults for missing dates
        from datetime import datetime, timedelta
        if not start_date:
            start_date = date.today() - timedelta(days=365)  # 1 year ago
        if not end_date:
            end_date = date.today()
        
        transactions = crud_transaction.get_by_date_range(
            db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id
        )
    else:
        transactions = crud_transaction.get_multi_by_user(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted
        )
        
        # Apply additional filters if using get_multi_by_user
        if transaction_type:
            transactions = [t for t in transactions if t.type == transaction_type]
        if category_id is not None:
            transactions = [t for t in transactions if t.category_id == category_id]
    
    return transactions


# TODO: POST /transactions - Create or restore transaction
@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new transaction or restore a deleted one.
    
    MODE 1: Create new transaction (provide all required fields):
    {
        "type": "expense",
        "amount": 150.50,
        "description": "Grocery shopping",
        "date": "2025-01-15",
        "category_id": 2
    }
    
    MODE 2: Restore deleted transaction (provide only id):
    {
        "id": 4
    }
    - Restores the deleted transaction with id=4 if it belongs to the user
    - Cannot provide other fields when restoring by id
    
    Validates:
    - Category exists and user has access (if category_id provided)
    - Category type matches transaction type (if category_id provided)
    - Cannot provide id with other fields (for restore mode)
    
    Returns:
        Created or restored transaction object
        
    Raises:
        404: Category not found OR Transaction not found (for restore)
        400: Category type mismatch OR Invalid field combination
        403: No permission to access category OR No permission to restore transaction
    """
    # MODE 2: RESTORE deleted transaction by id
    if transaction_in.id is not None:
        # Check if other fields are provided (not allowed in restore mode)
        other_fields_provided = any([
            transaction_in.type is not None,
            transaction_in.amount is not None,
            transaction_in.description is not None,
            transaction_in.date is not None,
            transaction_in.category_id is not None
        ])
        
        if other_fields_provided:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot provide other fields when restoring transaction by id. Provide only 'id' field."
            )
        
        # Find deleted transaction
        from app.models.transaction import Transaction
        deleted_transaction = db.query(Transaction).filter(
            Transaction.id == transaction_in.id,
            Transaction.user_id == current_user.id,
            Transaction.is_deleted == True
        ).first()
        
        if not deleted_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deleted transaction not found or does not belong to you"
            )
        
        # Restore transaction
        deleted_transaction.is_deleted = False
        deleted_transaction.deleted_at = None
        db.add(deleted_transaction)
        db.commit()
        db.refresh(deleted_transaction)
        
        return deleted_transaction
    
    # MODE 1: CREATE new transaction
    # Validate required fields for creation
    if not all([transaction_in.type, transaction_in.amount, transaction_in.date]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: type, amount, and date are required for creating new transaction"
        )
    
    # Validate category if provided
    if transaction_in.category_id:
        category = crud_category.get(db, id=transaction_in.category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if user has access to category
        has_access = category.is_default or category.user_id == current_user.id
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to use this category"
            )
        
        # Validate category type matches transaction type
        if category.type.value != transaction_in.type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category type '{category.type.value}' does not match transaction type '{transaction_in.type.value}'"
            )
    
    # Create transaction
    from app.models.transaction import Transaction
    transaction_data = transaction_in.model_dump(exclude={'id'})  # Exclude id from creation
    db_transaction = Transaction(**transaction_data, user_id=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


# TODO: GET /transactions/statistics - Get statistics
@router.get("/statistics", response_model=dict)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Get financial statistics for the user.
    
    Query Parameters:
    - start_date: Filter from date (YYYY-MM-DD) - optional
    - end_date: Filter to date (YYYY-MM-DD) - optional
    
    Returns:
    {
        "total_income": "5000.00",
        "total_expense": "3500.50",
        "balance": "1499.50",
        "transaction_count": 25
    }
    
    Examples:
        GET /transactions/statistics
        GET /transactions/statistics?start_date=2025-01-01&end_date=2025-01-31
    """
    statistics = crud_transaction.get_statistics(
        db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return statistics


# TODO: DELETE /transactions/{transaction_id} - Soft delete
@router.delete("/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete a transaction.
    
    Transaction is marked as deleted (is_deleted=True) but not removed from database.
    This preserves data for audit and statistics.
    
    Path Parameters:
    - transaction_id: Transaction ID
    
    Raises:
        404: Transaction not found or doesn't belong to user
    
    Returns:
        Soft deleted transaction object with is_deleted=True and deleted_at timestamp
    """
    transaction = crud_transaction.soft_delete(
        db,
        id=transaction_id,
        user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


# TODO: GET /transactions/{transaction_id} - Get transaction details
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get transaction details.
    
    Path Parameters:
    - transaction_id: Transaction ID
    
    Raises:
        404: Transaction not found or doesn't belong to user
    """
    transaction = crud_transaction.get(db, id=transaction_id)
    
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


# TODO: PUT /transactions/{transaction_id} - Update transaction
@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a transaction.
    
    Path Parameters:
    - transaction_id: Transaction ID
    
    Request body (all fields optional):
    {
        "type": "income",
        "amount": 200.00,
        "description": "Freelance work",
        "date": "2025-01-16",
        "category_id": 10
    }
    
    Validates:
    - Transaction exists and belongs to user
    - If category_id changed: validate category access and type match
    
    Raises:
        404: Transaction not found
        403: Transaction doesn't belong to user
        404: Category not found
        400: Category type mismatch
    """
    # Get transaction
    transaction = crud_transaction.get(db, id=transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Check ownership
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate category if being updated
    if transaction_in.category_id is not None:
        category = crud_category.get(db, id=transaction_in.category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check access
        has_access = category.is_default or category.user_id == current_user.id
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to use this category"
            )
        
        # Validate type match (use transaction_in.type if provided, else current transaction.type)
        transaction_type = transaction_in.type if transaction_in.type else transaction.type
        if category.type.value != transaction_type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category type '{category.type.value}' does not match transaction type '{transaction_type.value}'"
            )
    
    # Update transaction
    transaction = crud_transaction.update(db, db_obj=transaction, obj_in=transaction_in)
    return transaction
