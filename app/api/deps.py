"""
API dependencies module.

This module provides dependency functions for FastAPI routes.
Dependencies are used to inject database sessions, authenticate users,
and validate permissions before route handlers are executed.

Common dependencies:
- get_db: Provides database session
- get_current_user: Validates JWT token and returns current user
- get_current_active_user: Returns current user if active
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.crud_user import user as crud_user
from app.db.session import SessionLocal
from app.models.user import User

# What this does:
# - Creates a dependency that extracts token from: Authorization: Bearer <token>
# - If no token is provided, automatically returns 401 Unauthorized
# - The tokenUrl is for API documentation (Swagger UI) to know where to login
# Esquema OAuth2 (login com username/password no Swagger)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

# Esquema HTTPBearer (colar token direto)
http_bearer = HTTPBearer(auto_error=False)

def get_db() -> Generator:
    """
    Dependency that provides a database session.

    This function creates a new database session for each request
    and ensures it's properly closed after the request is complete.

    Yields:
        Session: SQLAlchemy database session

    Example usage in a route:
        @app.get("/users/")
        def read_users(db: Session = Depends(get_db)):
            users = crud_user.get_multi(db)
            return users

    How it works:
        1. Creates new session with SessionLocal()
        2. Yields session to the route
        3. Route executes with the session
        4. Finally block closes session (even if error occurs)
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    oauth_token: Optional[str] = Depends(oauth2_scheme),
    bearer_token: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
) -> User:
    """
    Dependency that validates JWT token and returns current user.

    This function:
    1. Receives token from Authorization header (via oauth2_scheme)
    2. Decodes and validates the JWT token
    3. Extracts user email from token
    4. Fetches user from database
    5. Returns the user object

    Args:
        db: Database session (injected by get_db dependency)
        token: JWT token string (injected by oauth2_scheme dependency)

    Returns:
        User: The authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found

    Example usage in a route:
        @app.get("/users/me")
        def read_current_user(current_user: User = Depends(get_current_user)):
            return current_user

    Token format expected:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Tenta pegar token de qualquer um dos dois métodos
    token = None
    if oauth_token:
        token = oauth_token
    elif bearer_token:
        token = bearer_token.credentials
    
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = crud_user.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that returns current user only if account is active.

    This is a wrapper around get_current_user that adds an additional
    check for account status. Use this in routes that require active accounts.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User: The current user if active

    Raises:
        HTTPException 400: If user account is inactive

    Example usage in a route:
        @app.post("/transactions/")
        def create_transaction(
            transaction: TransactionCreate,
            current_user: User = Depends(get_current_active_user)
        ):
            # Only active users can create transactions
            return crud_transaction.create(db, obj_in=transaction, owner_id=current_user.id)

    Dependency chain:
        get_current_active_user -> get_current_user -> get_db, oauth2_scheme
    """

    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
