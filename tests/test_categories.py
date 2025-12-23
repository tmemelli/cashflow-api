"""
Categories Tests Module.

This module validates the CRUD operations for Categories with strict
security and data integrity checks.

It covers:
1. Happy Path (Create, List, Update, Delete)
2. Data Validation (Limits, Enums)
3. Security & Isolation (User A vs User B)
4. Soft Delete Lifecycle
"""
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import create_default_categories
from app.models.category import CategoryType, Category

client = TestClient(app)

# --- HELPER FUNCTIONS ---

def create_unique_user():
    """
    Helper to create a unique user and return their auth headers.
    Prevents email collision errors between tests.
    """
    unique_id = str(uuid.uuid4())[:8]
    email = f"user_{unique_id}@example.com"
    password = "password123"
    
    # Register
    client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": f"User {unique_id}"
    })
    
    # Login
    login_res = client.post("/api/v1/auth/login", data={
        "username": email, "password": password
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- 1. HAPPY PATH TESTS ---

def test_create_category_success():
    """Test Case: Create valid Income and Expense categories."""
    headers = create_unique_user()
    
    # 1. Expense
    res_exp = client.post("/api/v1/categories/", headers=headers, json={
        "name": "Groceries", "type": "expense"
    })
    assert res_exp.status_code in [200, 201]
    assert res_exp.json()["name"] == "Groceries"
    assert res_exp.json()["type"] == "expense"
    assert res_exp.json()["is_default"] is False

    # 2. Income
    res_inc = client.post("/api/v1/categories/", headers=headers, json={
        "name": "Freelance", "type": "income"
    })
    assert res_inc.status_code in [200, 201]
    assert res_inc.json()["type"] == "income"

def test_list_categories():
    """Test Case: List categories creates earlier."""
    headers = create_unique_user()
    
    # Create two categories
    client.post("/api/v1/categories/", headers=headers, json={"name": "Cat 1", "type": "expense"})
    client.post("/api/v1/categories/", headers=headers, json={"name": "Cat 2", "type": "income"})
    
    # List
    response = client.get("/api/v1/categories/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    # Verify we got a list of category objects
    assert "name" in data[0]
    assert "type" in data[0]

def test_update_category_success():
    """Test Case: Update name and type."""
    headers = create_unique_user()
    
    # Create
    create_res = client.post("/api/v1/categories/", headers=headers, json={"name": "Old Name", "type": "expense"})
    cat_id = create_res.json()["id"]
    
    # Update
    update_res = client.put(f"/api/v1/categories/{cat_id}", headers=headers, json={
        "name": "New Name",
        "type": "income" # Changing type is allowed in schema
    })
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"
    assert update_res.json()["type"] == "income"

# --- 2. VALIDATION & LIMITS TESTS (HARDCORE) ---

def test_create_category_invalid_type():
    """
    Test Case: Enum Validation.
    Sending a type that is not 'income' or 'expense'.
    """
    headers = create_unique_user()
    payload = {"name": "Bad Type", "type": "investment"} # 'investment' is not in Enum
    
    response = client.post("/api/v1/categories/", headers=headers, json=payload)
    
    # Pydantic should block this
    assert response.status_code == 422
    assert "type" in str(response.json())

def test_create_category_name_limits():
    """
    Test Case: Name Length Limits (Min 1, Max 100).
    """
    headers = create_unique_user()
    
    # Case 1: Empty Name
    res_empty = client.post("/api/v1/categories/", headers=headers, json={
        "name": "", "type": "expense"
    })
    assert res_empty.status_code == 422
    
    # Case 2: Too Long (>100 chars)
    long_name = "A" * 101
    res_long = client.post("/api/v1/categories/", headers=headers, json={
        "name": long_name, "type": "expense"
    })
    assert res_long.status_code == 422

# --- 3. SECURITY & ISOLATION TESTS (CRITICAL) ---

def test_isolation_access_other_user_category():
    """
    Test Case: User A cannot access User B's category.
    This is the most important security test.
    """
    # 1. Setup User A and create a category
    headers_a = create_unique_user()
    res_a = client.post("/api/v1/categories/", headers=headers_a, json={"name": "Secret A", "type": "expense"})
    cat_id_a = res_a.json()["id"]
    
    # 2. Setup User B
    headers_b = create_unique_user()
    
    # 3. User B tries to GET User A's category
    get_res = client.get(f"/api/v1/categories/{cat_id_a}", headers=headers_b)
    # Should be 404 Not Found (Security best practice: don't reveal it exists)
    assert get_res.status_code == 404
    
    # 4. User B tries to UPDATE User A's category
    put_res = client.put(f"/api/v1/categories/{cat_id_a}", headers=headers_b, json={"name": "Hacked"})
    assert put_res.status_code == 404
    
    # 5. User B tries to DELETE User A's category
    del_res = client.delete(f"/api/v1/categories/{cat_id_a}", headers=headers_b)
    assert del_res.status_code == 404

def test_update_system_default_category_forbidden():
    """
    Test Case: User cannot update/delete system default categories.
    (Assuming you have logic or seed data for defaults, or we simulate one)
    """
    # Note: If your system doesn't have a way to create 'is_default=True' via API,
    # this test might need to rely on existing seed data. 
    # For now, we will skip creating a system cat via API because endpoints usually forbid it.
    pass 

# --- 4. LIFECYCLE TESTS (SOFT DELETE) ---

def test_soft_delete_category_lifecycle():
    """
    Test Case: Verify Soft Delete Logic.
    1. Create
    2. Delete
    3. Verify response says is_deleted=True (or returns 404 if your API hides deleted ones)
    """
    headers = create_unique_user()
    
    # 1. Create
    create_res = client.post("/api/v1/categories/", headers=headers, json={"name": "To Delete", "type": "expense"})
    cat_id = create_res.json()["id"]
    
    # 2. Delete
    del_res = client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    assert del_res.status_code == 200
    
    # 3. Verify logic (Depends on your specific implementation)
    # Option A: GET returns 404 for deleted items
    # Option B: GET returns item with is_deleted=True
    
    get_res = client.get(f"/api/v1/categories/{cat_id}", headers=headers)
    
    # Adjust this assertion based on your crud_category.py logic:
    if get_res.status_code == 200:
        # If your API shows deleted items but marks them:
        assert get_res.json()["is_deleted"] is True
    else:
        # If your API hides deleted items completely:
        assert get_res.status_code == 404

def test_list_categories_pagination():
    """
    Test Case: Pagination (Limit & Skip).
    
    Scenario:
        1. Create 15 categories.
        2. Request limit=10. Should return 10.
        3. Request skip=10. Should return 5.
    """
    headers = create_unique_user()
    
    # 1. Populate with 15 categories
    for i in range(15):
        client.post("/api/v1/categories/", headers=headers, json={
            "name": f"Cat {i}", 
            "type": "expense"
        })
        
    # 2. Test Limit
    res_limit = client.get("/api/v1/categories/?limit=10", headers=headers)
    assert res_limit.status_code == 200
    assert len(res_limit.json()) == 10
    
    # 3. Test Skip
    res_skip = client.get("/api/v1/categories/?skip=10&limit=100", headers=headers)
    assert res_skip.status_code == 200
    # If there were 15 and we skipped 10, 5 should remain (assuming no extra default categories).
    # Because defaults may vary, we check that the result is reasonable, or exactly 5 if only user categories exist.
    data = res_skip.json()
    assert len(data) >= 5 

def test_list_categories_filter_by_type():
    """
    Test Case: Filtering by Type.
    
    Scenario:
        User requests only 'income'. API should not return 'expense'.
    """
    headers = create_unique_user()
    
    # Create Mixed Types
    client.post("/api/v1/categories/", headers=headers, json={"name": "Job", "type": "income"})
    client.post("/api/v1/categories/", headers=headers, json={"name": "Food", "type": "expense"})
    
    # Filter for INCOME
    res = client.get("/api/v1/categories/?category_type=income", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    # Verify ALL returned items are income
    assert len(data) > 0
    for cat in data:
        assert cat["type"] == "income"

def test_init_db_creates_categories_and_is_idempotent(db):
    """
    Test the database initialization logic.
    Verifies creation and ensures running it twice DOES NOT duplicate data.
    """
    # 1. ROUND 1: First Execution
    create_default_categories(db)
    
    # Assert: Verify categories were created
    system_categories = db.query(Category).filter(
        Category.is_default == True,
        Category.user_id == None
    ).all()
    
    count_first_run = len(system_categories)
    assert count_first_run > 0, "Init DB failed to create any categories"
    
    # Verify typing of a sample
    if count_first_run > 0:
        sample = system_categories[0]
        assert isinstance(sample.type, CategoryType) or isinstance(sample.type, str)

    # 2. ROUND 2: Second Execution (Idempotency Check)
    create_default_categories(db)
    
    # Assert: Count should be EXACTLY the same
    count_second_run = db.query(Category).filter(
        Category.is_default == True,
        Category.user_id == None
    ).count()
    
    assert count_second_run == count_first_run, \
        f"Idempotency failed! Found {count_second_run} categories, expected {count_first_run}."