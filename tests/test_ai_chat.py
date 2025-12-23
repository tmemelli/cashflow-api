"""
AI Chat Tests Module - REAL API INTEGRATION.

⚠️ WARNING: These tests make REAL calls to the OpenAI API and consume credits ($$$).

This suite validates the entire stack (End-to-End):
1. INFRASTRUCTURE: Database Seeding & Idempotency logic.
2. CORE LOGIC: Soft Delete consistency & Math accuracy (The "Golden Test").
3. INTEGRATION: Real OpenAI calls with actual user data.
4. HISTORY: Saving, listing, deleting, and ordering conversation history.
5. SECURITY: User Isolation (User A cannot see User B's data).
6. SAFETY: Fail-fast behavior (Graceful handling of missing API Key).
7. EDGE CASES: Empty accounts, huge inputs, markdown cleaning validation.

Note: Tests use gpt-4o-mini to minimize costs while ensuring quality.
"""
import pytest
import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.main import app
from app.db.init_db import create_default_categories
from app.models.category import Category
from app.db.session import SessionLocal
from app.services.ai_service import AIService

client = TestClient(app)

# --- 1. PYTEST FIXTURES (The "Magic" that reduces code lines) ---

@pytest.fixture(scope="module")
def db():
    """
    Module-level database session fixture.
    Used for checking direct DB state (like seeding results).
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def auth_headers():
    """
    Fixture that creates a fresh, unique user for EACH test function.
    
    Returns:
        dict: The Authorization header {'Authorization': 'Bearer ...'}
    
    Why this is better:
    Instead of calling 'create_user' inside every single test (repetitive),
    we just pass 'auth_headers' as an argument to the test function.
    Pytest handles the setup automatically.
    """
    unique_id = str(uuid.uuid4())[:8]
    email = f"real_{unique_id}@example.com"
    password = "password123"
    
    # Register User
    client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": f"Tester {unique_id}"
    })
    
    # Login to get Token
    login_res = client.post("/api/v1/auth/login", data={
        "username": email, "password": password
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- 2. HELPER FUNCTIONS ---

def create_category(headers, name, cat_type):
    """Helper: Create a category and return its ID."""
    res = client.post("/api/v1/categories/", headers=headers, json={
        "name": name, "type": cat_type
    })
    return res.json()["id"]

def create_transaction(headers, trans_type, amount, trans_date=None, category_id=None, description="Test transaction"):
    """Helper: Create a transaction and return the full JSON object."""
    if trans_date is None:
        trans_date = date.today()
    
    payload = {
        "type": trans_type,
        "amount": amount,
        "date_transaction": str(trans_date),
        "description": description
    }
    if category_id:
        payload["category_id"] = category_id
    
    res = client.post("/api/v1/transactions/", headers=headers, json=payload)
    return res.json()

# --- 3. INFRASTRUCTURE TESTS (New Refactoring) ---

def test_infrastructure_init_db_idempotency(db: Session):
    """
    Test Case: Seeding Robustness (Idempotency).
    
    Scenario:
        Run the seeding function twice.
    
    Expectation:
        The second run should NOT duplicate data. The count of categories
        must remain the same.
    """
    print("\n🏗️ [INFRA] Testing Database Seeding & Idempotency...")
    
    # Round 1: Initial Seed
    create_default_categories(db)
    count_1 = db.query(Category).filter(Category.is_default == True).count()
    assert count_1 > 0, "Seeding failed to create categories"
    
    # Round 2: Re-run Seed (Idempotency Check)
    create_default_categories(db)
    count_2 = db.query(Category).filter(Category.is_default == True).count()
    
    assert count_1 == count_2, f"Idempotency Failed! Before: {count_1}, After: {count_2}"
    print(f"✅ System Categories Stable: {count_1} categories found.")

# --- 4. CORE LOGIC & "GOLDEN TEST" (Soft Delete + AI) ---

def test_ai_recognizes_soft_delete_updates(auth_headers):
    """
    Test Case: The 'Golden Test' (Full Cycle Validation).
    
    Scenario:
    1. User adds Income ($5000) and Expense ($1000).
    2. AI confirms Balance is $4000.
    3. User DELETES the Expense ($1000) via API.
    4. AI is asked again.
    
    Expectation:
    AI should realize the expense is gone and report Balance $5000.
    This proves the AIService respects the 'is_deleted' flag in the database.
    """
    print("\n🔥 [REAL API] Starting 'Golden Test' (Create -> AI -> Delete -> AI)...")
    
    # 1. Setup Data
    create_transaction(auth_headers, "income", 5000, description="Salary")
    expense_tx = create_transaction(auth_headers, "expense", 1000, description="Wrong Expense")
    expense_id = expense_tx["id"]
    
    # 2. First AI Check (Expect 4000)
    print("   🤖 Asking AI about balance (Pre-Delete)...")
    res1 = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "What is my current balance?"
    })
    data1 = res1.json()
    balance_1 = float(data1["data"]["balance"])
    assert balance_1 == 4000.0, f"AI Math Fail! Expected 4000, got {balance_1}"
    print(f"   ✅ AI correctly sees $4000.")

    # 3. Perform Soft Delete
    print(f"   🗑️ Deleting transaction {expense_id}...")
    del_res = client.delete(f"/api/v1/transactions/{expense_id}", headers=auth_headers)
    assert del_res.status_code == 200
    
    # 4. Second AI Check (Expect 5000)
    print("   🤖 Asking AI about balance (Post-Delete)...")
    res2 = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "Update me. What is my balance now?"
    })
    data2 = res2.json()
    balance_2 = float(data2["data"]["balance"])
    
    assert balance_2 == 5000.0, f"Soft Delete Fail! AI still sees deleted data. Got {balance_2}"
    
    print(f"   ✅ AI correctly sees $5000. Deleted item is gone.")
    print("   🏆 GOLDEN TEST PASSED.")

# --- 5. BASIC CHAT FLOW TESTS ---

def test_chat_basic_question_real_api(auth_headers):
    """Test Case: Basic Chat with Real OpenAI API."""
    print("\n🔥 [REAL API] Calling OpenAI for basic question...")
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "What's my balance?"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["reply"]) > 0
    assert data["data"] is not None
    assert "balance" in data["data"]
    
    print(f"✅ AI Response: {data['reply'][:100]}...")

def test_chat_with_real_financial_data(auth_headers):
    """Test Case: AI Analyzes Real User Financial Data (Accuracy Check)."""
    today = date.today()
    
    # Create real financial data
    create_transaction(auth_headers, "income", 5000, today, description="Monthly Salary")
    create_transaction(auth_headers, "expense", 1500, today, description="Rent + Bills")
    
    print("\n🔥 [REAL API] Calling OpenAI with financial context...")
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "What's my current balance?"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate data context matches DB
    assert float(data["data"]["total_income"]) == 5000.00
    assert float(data["data"]["total_expense"]) == 1500.00
    assert float(data["data"]["balance"]) == 3500.00
    
    # AI should mention the balance in the text reply
    reply = data["reply"].lower()
    assert "3500" in reply or "3,500" in reply
    print(f"✅ AI correctly calculated balance: {data['reply'][:100]}...")

def test_chat_saves_to_history_real(auth_headers):
    """Test Case: Real Conversation is Saved to History."""
    question = "How much money do I have?"
    
    print("\n🔥 [REAL API] Testing history persistence...")
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": question})
    
    # Get history
    history_res = client.get("/api/v1/ai/history", headers=auth_headers)
    assert history_res.status_code == 200
    
    history = history_res.json()
    assert len(history) == 1
    assert history[0]["question"] == question
    assert history[0]["was_successful"] is True
    print(f"✅ History saved correctly")

def test_markdown_cleaning_in_real_response(auth_headers):
    """Test Case: Markdown Cleaner Works on Real AI Responses."""
    print("\n🔥 [REAL API] Testing markdown cleaning...")
    
    # Create scenario forcing a list response
    today = date.today()
    create_transaction(auth_headers, "expense", 300, today, description="Groceries")
    create_transaction(auth_headers, "expense", 200, today, description="Uber")
    
    # We ask for a list, which GPT usually formats with bullets
    client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "List my expenses with bullet points"
    })
    
    # Get saved response from DB
    history_res = client.get("/api/v1/ai/history", headers=auth_headers)
    saved_response = history_res.json()[0]["response"]
    
    # Validate no markdown syntax remains
    assert "**" not in saved_response
    assert "###" not in saved_response
    print(f"✅ Response clean (no markdown): {saved_response[:100]}...")

# --- 6. HISTORY MANAGEMENT TESTS ---

def test_history_ordering_real(auth_headers):
    """Test Case: History Returns Newest First."""
    print("\n🔥 [REAL API] Testing history ordering...")
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": "Q1"})
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": "Q2"})
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": "Q3"})
    
    history = client.get("/api/v1/ai/history", headers=auth_headers).json()
    assert len(history) == 3
    assert history[0]["question"] == "Q3" # Newest
    assert history[2]["question"] == "Q1" # Oldest
    print("✅ History ordered correctly")

def test_history_limit(auth_headers):
    """Test Case: History Limit Parameter Works."""
    for i in range(5):
        client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": f"Q{i}"})
    
    history = client.get("/api/v1/ai/history?limit=2", headers=auth_headers).json()
    assert len(history) == 2
    print("✅ Limit parameter works")

def test_delete_chat_real(auth_headers):
    """Test Case: Delete Chat from History."""
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": "Delete me"})
    
    history = client.get("/api/v1/ai/history", headers=auth_headers).json()
    chat_id = history[0]["id"]
    
    del_res = client.delete(f"/api/v1/ai/history/{chat_id}", headers=auth_headers)
    assert del_res.status_code == 204
    
    history_after = client.get("/api/v1/ai/history", headers=auth_headers).json()
    assert len(history_after) == 0
    print("✅ Chat deleted successfully")

# --- 7. SECURITY & ISOLATION TESTS ---

def test_chat_user_isolation_real(auth_headers):
    """Test Case: User A Cannot See User B's Data in AI."""
    # We need a second user here
    headers_b = create_unique_user_helper_internal()
    
    print("\n🔥 [REAL API] Testing user isolation...")
    # User A (auth_headers) creates massive income
    create_transaction(auth_headers, "income", 99999, date.today())
    
    # User B asks about balance
    chat_b = client.post("/api/v1/ai/chat", headers=headers_b, json={
        "message": "What's my balance?"
    })
    data_b = chat_b.json()["data"]
    
    # User B should see ZERO income
    assert float(data_b["total_income"]) == 0.0
    print("✅ Users properly isolated")

def create_unique_user_helper_internal():
    """Internal Helper specifically for isolation test where we need a 2nd user."""
    unique_id = str(uuid.uuid4())[:8]
    email = f"user_b_{unique_id}@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "User B"})
    login = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}

def test_delete_other_user_chat(auth_headers):
    """Test Case: User B Cannot Delete User A's Chat."""
    headers_b = create_unique_user_helper_internal()
    
    # User A creates chat
    client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": "Private"})
    history_a = client.get("/api/v1/ai/history", headers=auth_headers).json()
    chat_id_a = history_a[0]["id"]
    
    # User B tries to delete
    del_res = client.delete(f"/api/v1/ai/history/{chat_id_a}", headers=headers_b)
    assert del_res.status_code == 404
    print("✅ Cannot delete other user's chat")

# --- 8. VALIDATION TESTS ---

def test_chat_empty_message(auth_headers):
    """Test: Cannot send empty message."""
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": ""})
    assert response.status_code == 422

def test_chat_message_too_long(auth_headers):
    """Test: Message length limit."""
    long_message = "A" * 1001
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={"message": long_message})
    assert response.status_code == 422

# --- 9. SAFETY TESTS (New Refactoring) ---

def test_fail_fast_safety():
    """
    Test Case: Simulate Missing Key (Safety Check).
    
    Scenario:
        We mock the settings to make 'openai_api_key' None.
        Then we try to initialize the service.
    
    Expectation:
        The service should NOT crash. 
        It should initialize with 'client = None'.
    """
    print("\n🛡️ [SAFETY] Testing Missing Key Behavior...")
    with patch("app.core.config.settings.openai_api_key", None):
        service = AIService()
        assert service.client is None
        print("✅ Service initialized safely without key.")

# --- 10. EDGE CASES ---

def test_chat_empty_account_real(auth_headers):
    """Test Case: AI Handles Empty Account Gracefully."""
    print("\n🔥 [REAL API] Testing empty account...")
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "What's my balance?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["data"]["balance"]) == 0.0
    print(f"✅ Empty account handled.")

def test_chat_with_categories_real(auth_headers):
    """Test Case: AI References Categories."""
    today = date.today()
    cat_id = create_category(auth_headers, "Food", "expense")
    create_transaction(auth_headers, "expense", 100, today, cat_id, "Lunch")
    
    response = client.post("/api/v1/ai/chat", headers=auth_headers, json={
        "message": "What did I spend on?"
    })
    
    data = response.json()
    assert "categories" in data["data"]
    assert len(data["data"]["categories"]) == 1
    assert data["data"]["categories"][0]["name"] == "Food"
    print(f"✅ Categories in context.")