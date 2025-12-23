"""
Security utilities module.

This module provides security-related functions including:
- Password hashing and verification using bcrypt
- JWT token creation and validation
- Token payload encoding and decoding
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    This function compares a plain text password with its hashed version
    stored in the database. It uses bcrypt for secure comparison.

    Args:
        plain_password: The plain text password provided by the user
        hashed_password: The hashed password stored in the database

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = "$2b$12$KIX..."
        >>> verify_password("senha123", hashed)
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    This function takes a plain text password and returns its hashed version.
    The hash is what gets stored in the database - never store plain passwords!

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password (bcrypt format: $2b$12$...)

    Example:
        >>> get_password_hash("senha123")
        "$2b$12$KIXnB8h3vW9FyZ..."

    Security Note:
        Bcrypt automatically generates a salt and includes it in the hash.
        Same password will produce different hashes each time (this is good!).
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    This function generates a JWT token containing user data and an expiration time.
    The token is signed using the SECRET_KEY from settings.

    Args:
        data: Dictionary containing data to encode in the token (usually user_id)
        expires_delta: Optional custom expiration time. If not provided,
                      uses ACCESS_TOKEN_EXPIRE_MINUTES from settings

    Returns:
        str: Encoded JWT token string

    Example:
        >>> token = create_access_token(data={"sub": "user@email.com"})
        >>> print(token)
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Token Structure:
        {
            "sub": "user@email.com",
            "exp": 1234567890  # Unix timestamp
        }
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.

    This function decodes a JWT token, validates its signature and expiration,
    and returns the payload data if valid.

    Args:
        token: JWT token string to decode

    Returns:
        dict: Token payload if valid (contains user data)
        None: If token is invalid, expired, or malformed

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {"sub": "user@email.com", "exp": 1234567890}

    Security Notes:
        - Validates token signature using SECRET_KEY
        - Checks if token has expired
        - Returns None for any invalid token (don't expose error details)
    """
    # Use try-except to handle potential JWT errors
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
