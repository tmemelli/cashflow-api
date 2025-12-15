"""
Application configuration module.

This module handles all application settings using Pydantic Settings.
It reads environment variables from .env file and provides type validation.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings class.

    This class manages all configuration variables for the application.
    It automatically reads from environment variables and .env file.

    Attributes:
        PROJECT_NAME: Name of the API project
        VERSION: API version
        API_V1_STR: API version 1 prefix for routes
        SECRET_KEY: Secret key for JWT token encoding (keep this secure!)
        ALGORITHM: Algorithm used for JWT encoding
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes
        DATABASE_URL: SQLite database connection string
    """

    PROJECT_NAME: str = "CashFlow API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security configuration
    SECRET_KEY: str = "your-very-secure-and-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database configuration
    DATABASE_URL: str = "sqlite:///./cashflow.db"

    # AI Settings - ADICIONAR AQUI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        """
        Pydantic configuration class.
        Tells Pydantic where to find environment variables.
        """

        env_file = ".env"
        case_sensitive = True


settings = Settings()
