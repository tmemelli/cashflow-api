"""
Test configuration - runs before all tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db

# Import Base and all models
from app.db.base import Base
from app.models import user, category, transaction, chat

# Test database (SQLite in-memory for isolation)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables before tests
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def db():
    """Create clean database for each test"""
    # Drop all tables before creating new ones
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    """Override real database with test database"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test client for API requests
client = TestClient(app)


@pytest.fixture
def test_client():
    """Return test client"""
    return client


@pytest.fixture
def auth_headers(test_client):
    """
    Creates a default user and returns authentication headers.
    This fixture allows tests to bypass manual registration/login steps.
    """
    # 1. Register user
    test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_global@example.com",
            "password": "testpass123",
            "full_name": "Global Test User"
        }
    )
    
    # 2. Login to get token
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test_global@example.com",
            "password": "testpass123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}