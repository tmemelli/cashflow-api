"""
Transactions Tests Module (The Ultimate Version).

Combines the best strategies:
1. End-to-End Financial Logic (Flow & Math)
2. Strict Business Rules & Validation (Missing fields, Mismatches)
3. Lifecycle & Restore Mode (Mode 2 validation)
4. Security Isolation (User A vs User B)
5. Audit Accuracy (Statistics excluding deleted items)
"""
import uuid
from datetime import date, timedelta, datetime
from fastapi.testclient import TestClient
from app.main import app
from app.crud.base import CRUDBase
from app.models.transaction import Transaction, TransactionType
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import Category, CategoryType

client = TestClient(app)

# --- HELPER FUNCTIONS ---

def create_unique_user():
    """Helper to create a unique user and return auth headers."""
    unique_id = str(uuid.uuid4())[:8]
    email = f"money_{unique_id}@example.com"
    password = "password123"
    
    # Register & Login
    client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": f"User {unique_id}"
    })
    login_res = client.post("/api/v1/auth/login", data={
        "username": email, "password": password
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_category(headers, name, type):
    """Helper to create a category and return its ID."""
    res = client.post("/api/v1/categories/", headers=headers, json={
        "name": name, "type": type
    })
    return res.json()["id"]

# --- 1. HAPPY PATH & MATH TESTS ---

def test_transaction_flow_and_statistics():
    """
    Test Case: Complete Flow + Statistics Math.
    
    Scenario:
        1. Create Income of 1000.00
        2. Create Expense of 250.50
        3. Check Statistics: Balance must be 749.50
    """
    headers = create_unique_user()
    
    # 1. Create Income
    cat_inc_id = create_category(headers, "Salary", "income")
    res_inc = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "income",
        "amount": 1000.00,
        "description": "October Salary",
        "date_transaction": str(date.today()),
        "category_id": cat_inc_id
    })
    assert res_inc.status_code == 201
    
    # 2. Create Expense
    cat_exp_id = create_category(headers, "Market", "expense")
    res_exp = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense",
        "amount": 250.50,
        "description": "Weekly Shopping",
        "date_transaction": str(date.today()),
        "category_id": cat_exp_id
    })
    assert res_exp.status_code == 201

    # 3. Check Statistics
    stats = client.get("/api/v1/transactions/statistics", headers=headers)
    assert stats.status_code == 200
    data = stats.json()
    
    # Validate Math
    assert float(data["total_income"]) == 1000.00
    assert float(data["total_expense"]) == 250.50
    assert float(data["balance"]) == 749.50
    assert data["transaction_count"] == 2

# --- 2. BUSINESS RULES & VALIDATION TESTS ---

def test_transaction_category_type_mismatch():
    """
    Test Case: Category Type vs Transaction Type Logic.
    
    Scenario:
        Try to create an 'expense' transaction using an 'income' category.
        API must block this inconsistency.
    """
    headers = create_unique_user()
    cat_id = create_category(headers, "Investments", "income")
    
    # Try to launch an Expense using that Income Category
    res = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense", # <--- MISMATCH
        "amount": 50.00,
        "date_transaction": str(date.today()),
        "category_id": cat_id
    })
    
    # Should fail with 400 Bad Request (Business Logic Error)
    assert res.status_code == 400
    assert "match" in res.json()["detail"].lower()

def test_transaction_missing_required_fields():
    """
    Test Case: Missing Fields (Manual Validation).
    
    Scenario:
        Try to create without 'type' or 'date'.
        Your API explicitly checks for this and raises 400.
    """
    headers = create_unique_user()
    
    response = client.post("/api/v1/transactions/", headers=headers, json={
        "amount": 100.00 # Missing type and date
    })
    
    assert response.status_code == 400
    assert "missing required fields" in response.json()["detail"].lower()

def test_transaction_negative_amount():
    """Test Case: Validation Limits (Negative Amount)."""
    headers = create_unique_user()
    
    res = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense",
        "amount": -100.00, # <--- Invalid
        "date_transaction": str(date.today())
    })
    
    # Pydantic validation error (422)
    assert res.status_code == 422

# --- 3. LIFECYCLE: RESTORE & AUDIT ---

def test_transaction_restore_lifecycle():
    """
    Test Case: Soft Delete and Restore (Mode 2).
    
    Scenario:
        1. Create transaction.
        2. Delete transaction.
        3. Restore using {"id": X} payload.
    """
    headers = create_unique_user()
    
    # 1. Create
    res = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense", "amount": 50.00, "date_transaction": str(date.today())
    })
    tx_id = res.json()["id"]
    
    # 2. Delete
    client.delete(f"/api/v1/transactions/{tx_id}", headers=headers)
    
    # Verify it's gone from list
    list_res = client.get("/api/v1/transactions/", headers=headers)
    assert len(list_res.json()) == 0
    
    # 3. Restore (The Special Mode)
    restore_res = client.post("/api/v1/transactions/", headers=headers, json={
        "id": tx_id # Only ID provided
    })
    assert restore_res.status_code == 201 
    
    # FIX: We check that 'deleted_at' is None because 'is_deleted' is not present in the response schema.
    assert restore_res.json()["deleted_at"] is None
    
    # Verify it's back
    list_res_2 = client.get("/api/v1/transactions/", headers=headers)
    assert len(list_res_2.json()) == 1

def test_restore_requires_only_id():
    """
    Test Case: Strict Restore Mode Validation.
    
    Scenario:
        User tries to restore ID but also sends 'amount' to sneakily change data.
        API should reject this mix.
    """
    headers = create_unique_user()
    
    # Try to mix ID (restore mode) with other fields (create mode)
    response = client.post("/api/v1/transactions/", headers=headers, json={
        "id": 999,
        "amount": 100.00
    })
    
    assert response.status_code == 400
    assert "cannot provide other fields" in response.json()["detail"].lower()

def test_statistics_excludes_deleted():
    """
    Test Case: Audit Accuracy.
    
    Scenario:
        Deleted transactions should NOT be counted in the balance.
    """
    headers = create_unique_user()
    
    # Create and immediately delete
    res = client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense", "amount": 9999.00, "date_transaction": str(date.today())
    })
    tx_id = res.json()["id"]
    client.delete(f"/api/v1/transactions/{tx_id}", headers=headers)
    
    # Get Stats
    stats = client.get("/api/v1/transactions/statistics", headers=headers).json()
    
    # Should be zero
    assert float(stats["total_expense"]) == 0.0
    assert float(stats["balance"]) == 0.0

# --- 4. SECURITY & ISOLATION TESTS ---

def test_isolation_access_other_user_transaction():
    """Test Case: User A cannot see User B's transaction."""
    headers_a = create_unique_user()
    res_a = client.post("/api/v1/transactions/", headers=headers_a, json={
        "type": "income", "amount": 100, "date_transaction": str(date.today())
    })
    tx_id_a = res_a.json()["id"]
    
    headers_b = create_unique_user()
    get_res = client.get(f"/api/v1/transactions/{tx_id_a}", headers=headers_b)
    assert get_res.status_code == 404 

def test_isolation_use_other_user_category():
    """
    Test Case: User A cannot use User B's category to create transaction.
    This prevents cross-user data corruption.
    """
    headers_a = create_unique_user()
    cat_id_a = create_category(headers_a, "Private Cat", "expense")
    
    headers_b = create_unique_user()
    
    # User B tries to steal the category ID
    res = client.post("/api/v1/transactions/", headers=headers_b, json={
        "type": "expense",
        "amount": 50.00,
        "date_transaction": str(date.today()),
        "category_id": cat_id_a # <--- Stolen
    })
    
    # Should be Forbidden
    assert res.status_code == 403

def test_update_security_check():
    """Test Case: User B cannot UPDATE User A's transaction."""
    headers_a = create_unique_user()
    res_a = client.post("/api/v1/transactions/", headers=headers_a, json={
        "type": "income", "amount": 100, "date_transaction": str(date.today())
    })
    tx_id_a = res_a.json()["id"]
    
    headers_b = create_unique_user()
    
    update_res = client.put(f"/api/v1/transactions/{tx_id_a}", headers=headers_b, json={
        "amount": 999999
    })
    
    # Your API checks ownership
    assert update_res.status_code == 403

# --- 5. FILTERING TESTS ---

def test_list_transactions_date_filter():
    """Test Case: Filter by Start and End Date."""
    headers = create_unique_user()
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense", "amount": 10, "date_transaction": str(yesterday)
    })
    client.post("/api/v1/transactions/", headers=headers, json={
        "type": "expense", "amount": 20, "date_transaction": str(today)
    })
    
    # Filter only Today
    res = client.get(f"/api/v1/transactions/?start_date={today}&end_date={today}", headers=headers)
    data = res.json()
    
    assert len(data) == 1
    assert float(data[0]["amount"]) == 20.0

def test_crud_remove_soft_delete_mechanics(db):
    """
    Validates if the new 'remove' method using db.get() works correctly
    with the Soft Delete logic.
    """
    # 1. Arrange: Create independent User & Category manually
    # We create them here to avoid dependency on external fixtures not present in this file
    user = User(
        email="soft_delete_clean@example.com", 
        hashed_password=get_password_hash("123"), 
        full_name="Soft Delete Tester"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    category = Category(
        name="Temp Delete Cat", 
        type=CategoryType.EXPENSE, 
        user_id=user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    # Create the target transaction
    transaction = Transaction(
        user_id=user.id,
        category_id=category.id,
        type=TransactionType.EXPENSE,
        amount=50.00,
        description="To be deleted",
        date_transaction=datetime.now()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    tx_id = transaction.id

    # 2. Act: Call the refactored remove method
    crud_base = CRUDBase(Transaction) 
    deleted_obj = crud_base.remove(db, id=tx_id)

    # 3. Assert: Verify Soft Delete state
    assert deleted_obj is not None
    assert deleted_obj.id == tx_id
    assert deleted_obj.is_deleted is True
    assert deleted_obj.deleted_at is not None
    
    # 4. Assert: Verify SQLAlchemy 2.0 Identity Map behavior
    # Direct DB query to prove it's still there (physically) but marked logically
    raw_obj = db.get(Transaction, tx_id)
    assert raw_obj.is_deleted is True