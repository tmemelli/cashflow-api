"""
Category endpoints module.

This module provides REST API endpoints for category management.
Handles both system default categories and user-created categories.

Endpoints:
- GET /categories - List available categories (defaults + user's own)
- POST /categories - Create a new user category
- GET /categories/{category_id} - Get category details with transaction count
- PUT /categories/{category_id} - Update user category
- DELETE /categories/{category_id} - Delete user category (with validation)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.crud_category import category as crud_category
from app.models.user import User
from app.models.category import CategoryType
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithTransactions
)

router = APIRouter()


# TODO: GET /categories - List categories
@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category_type: Optional[CategoryType] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    List all categories available to the current user.
    
    Returns system default categories + user's own categories.
    
    Query Parameters:
    - category_type: Filter by type (income/expense) - optional
    - skip: Number of records to skip (pagination) - default 0
    - limit: Maximum number of records to return - default 100
    
    Example:
        GET /categories?category_type=expense&limit=10
    """
    categories = crud_category.get_by_user(
        db,
        user_id=current_user.id,
        category_type=category_type,
        skip=skip,
        limit=limit
    )
    return categories


# TODO: POST /categories - Create category
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user category.
    
    User categories are always non-default (is_default=False).
    
    Request body:
    {
        "name": "Uber",
        "type": "expense"
    }
    
    Returns:
        Created category object
    """
    category = crud_category.create_with_owner(
        db,
        obj_in=category_in,
        user_id=current_user.id
    )
    return category


# TODO: GET /categories/{category_id} - Get category details
@router.get("/{category_id}", response_model=CategoryWithTransactions)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get category details with transaction count.
    
    Returns category information and number of associated transactions.
    
    Path Parameters:
    - category_id: Category ID
    
    Raises:
        404: Category not found or user doesn't have access
    """
    result = crud_category.get_with_transaction_count(
        db,
        user_id=current_user.id,
        category_id=category_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Combine category data with transaction count
    category_dict = {
        **CategoryResponse.model_validate(result["category"]).model_dump(),
        "transaction_count": result["transaction_count"]
    }
    
    return category_dict


# TODO: PUT /categories/{category_id} - Update category
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user category.
    
    Only the owner can update their own categories.
    System default categories cannot be updated.
    
    Path Parameters:
    - category_id: Category ID
    
    Request body (all fields optional):
    {
        "name": "Food & Drinks",
        "type": "expense"
    }
    
    Raises:
        404: Category not found
        403: Cannot update system default category
        403: Cannot update another user's category
    """
    # Get category
    category = crud_category.get(db, id=category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Cannot update system default categories
    if category.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update system default category"
        )
    
    # Check ownership
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update category
    category = crud_category.update(db, db_obj=category, obj_in=category_in)
    return category


# TODO: DELETE /categories/{category_id} - Delete category
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user category.
    
    Validates before deletion:
    - Category must exist
    - User must be the owner
    - Cannot delete system default categories
    - Cannot delete categories with associated transactions
    
    Path Parameters:
    - category_id: Category ID
    
    Raises:
        404: Category not found
        403: Cannot delete system default category
        403: Cannot delete another user's category
        400: Cannot delete category with associated transactions
    
    Returns:
        204 No Content on success
    """
    # Validate if category can be deleted
    can_delete, message = crud_category.can_delete(
        db,
        category_id=category_id,
        user_id=current_user.id
    )
    
    if not can_delete:
        # Determine appropriate status code based on message
        if "not found" in message.lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "cannot delete system" in message.lower():
            status_code = status.HTTP_403_FORBIDDEN
        elif "associated transactions" in message.lower():
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_403_FORBIDDEN
        
        raise HTTPException(
            status_code=status_code,
            detail=message
        )
    
    # Delete category
    crud_category.remove(db, id=category_id)
    return None