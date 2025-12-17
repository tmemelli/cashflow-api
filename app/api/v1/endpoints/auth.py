"""
Authentication endpoints module.

This module provides authentication-related API endpoints:
- Login (get access token)
- Register (create new user)
- Get current user info

These endpoints handle user authentication and registration.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.crud_user import user as crud_user
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter()


@router.post("/login")
def login(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    
    Get an access token for future requests.
    
    This endpoint follows OAuth2 password flow:
    - Receives username (email) and password via form data
    - Validates credentials
    - Returns access token if valid
    
    Args:
        db: Database session (injected)
        form_data: OAuth2 form with username and password
        
    Returns:
        dict: Access token and token type
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer"
        }
        
    Raises:
        HTTPException 401: Incorrect email or password
        HTTPException 400: Inactive user account
        
    Example usage (curl):
        curl -X POST "http://localhost:8000/api/v1/auth/login" \\
             -H "Content-Type: application/x-www-form-urlencoded" \\
             -d "username=user@example.com&password=secret123"
    """

    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    # NOTE: form_data.username actually contains the email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=410,  # 410 Gone - Resource deleted
            detail="User account has been deleted"
        )

    if not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    """
    Register new user.
    
    Create a new user account.
    
    Args:
        user_in: User data (email, password, etc)
        db: Database session (injected)
        
    Returns:
        User: Created user data (without password)
        
    Raises:
        HTTPException 400: Email already registered
        
    Example usage (curl):
        curl -X POST "http://localhost:8000/api/v1/auth/register" \\
             -H "Content-Type: application/json" \\
             -d '{
                   "email": "newuser@example.com",
                   "password": "secret123"
                 }'
                 
    Response:
        {
            "id": 1,
            "email": "newuser@example.com",
            "is_active": true,
            "is_superuser": false,
            "created_at": "2025-12-05T10:30:00"
        }
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud_user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=User)
def read_user_me(current_user: User = Depends(deps.get_current_active_user)) -> User:
    """
    Get current user.
    
    Retrieve information about the currently authenticated user.
    
    Requires authentication via Bearer token.
    
    Args:
        current_user: Current authenticated user (injected by dependency)
        
    Returns:
        User: Current user data
        
    Raises:
        HTTPException 401: Invalid or missing token
        HTTPException 400: Inactive user
        
    Example usage (curl):
        curl -X GET "http://localhost:8000/api/v1/auth/me" \\
             -H "Authorization: Bearer eyJhbGc..."
             
    Response:
        {
            "id": 1,
            "email": "user@example.com",
            "is_active": true,
            "is_superuser": false,
            "created_at": "2025-12-05T10:30:00"
        }
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user profile.
    
    Update profile information of the currently authenticated user.
    This will update the updated_at timestamp.
    
    Args:
        db: Database session (injected)
        user_in: UserUpdate schema with fields to update
        current_user: Currently authenticated user (injected)
        
    Returns:
        User: Updated user data with updated_at timestamp
        
    Example:
        {
            "full_name": "New Name",
            "email": "newemail@example.com"
        }
    """
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.delete("/me", response_model=User)
def delete_user_me(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Soft delete current user account (IRREVERSIBLE).
    
    ⚠️ WARNING: This action is IRREVERSIBLE. The user will NOT be able to:
    - Login to the account again
    - Recover the account through the API
    - Access any data associated with the account
    
    The account is marked as is_deleted=True (soft delete pattern).
    Data is preserved in the database for:
    - Audit trail and compliance (GDPR/LGPD)
    - Financial record keeping
    - Legal requirements
    
    However, the account is permanently inaccessible to the user.
    Only database administrators can reverse this operation manually.
    
    Args:
        db: Database session (injected)
        current_user: Currently authenticated user (injected)
        
    Returns:
        User: User data with is_deleted=True
        
    Raises:
        HTTPException 410: On subsequent API calls after deletion
        
    Example:
        DELETE /api/v1/auth/me
        → Account marked as deleted
        → All future requests return 410 Gone
    """
    user = crud_user.update(db, db_obj=current_user, obj_in={"is_deleted": True})
    return user
