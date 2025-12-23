"""
Authentication Tests Module.

This module contains comprehensive integration tests for the authentication endpoints.
It covers registration, login, and user profile retrieval scenarios, including
happy paths, validation errors, and security constraints.

Endpoints covered:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- 1. Registration Tests ---

def test_register_new_user_success():
    """
    Test Case: Successful User Registration.
    
    Scenario:
        A new user submits valid email, password, and full name.
    
    Expected Result:
        - Status Code: 200 OK (or 201 Created depending on implementation).
        - Response Body: Should contain the created user's email and id.
        - Security: Password should not be returned in the response.
    """
    payload = {
        "email": "unique_user_01@example.com",
        "password": "strongpassword123",
        "full_name": "Test User One"
    }
    
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "password" not in data  # Security check

def test_register_duplicate_email():
    """
    Test Case: Registration with Duplicate Email.
    
    Scenario:
        A user attempts to register with an email that already exists in the database.
    
    Expected Result:
        - Status Code: 400 Bad Request.
        - Error Message: Should indicate that the user/email already exists.
    """
    email = "duplicate_check@example.com"
    
    # Step 1: Create the first user
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Original"
    })
    
    # Step 2: Attempt to create the second user with the same email
    response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "otherpass",
        "full_name": "Copy"
    })
    
    assert response.status_code == 400
    assert "detail" in response.json()

def test_register_short_password():
    """
    Test Case: Password Length Validation.
    
    Scenario:
        User tries to register with a password shorter than 8 characters.
        
    Expected Result:
        - Status Code: 422 Unprocessable Entity.
    """
    payload = {
        "email": "short_pass@example.com",
        "password": "short",  # <--- Only 5 characters
        "full_name": "Short Password User"
    }
    
    response = client.post("/api/v1/auth/register", json=payload)
    
    # Pydantic should automatically reject with 422
    assert response.status_code == 422
    
    # Check that the error message mentions the password
    data = response.json()
    # Usually the error is in 'detail' -> list of errors -> 'loc' or 'msg'
    assert "password" in str(data["detail"])

def test_register_missing_fields():
    """
    Test Case: Registration Validation (Missing Fields).
    
    Scenario:
        The client sends a JSON payload missing required fields (e.g., password).
        This tests Pydantic validation.
    
    Expected Result:
        - Status Code: 422 Unprocessable Entity.
    """
    # Missing password
    payload = {
        "email": "incomplete@example.com",
        "full_name": "Incomplete User"
    }
    
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

def test_register_invalid_email_format():
    """
    Test Case: Registration Validation (Invalid Email).
    
    Scenario:
        The client sends a string that is not a valid email format.
    
    Expected Result:
        - Status Code: 422 Unprocessable Entity.
    """
    payload = {
        "email": "not-an-email-string",
        "password": "password123",
        "full_name": "Bad Email User"
    }
    
    response = client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422

# --- 2. Login Tests ---

def test_login_success():
    """
    Test Case: Successful Login.
    
    Scenario:
        A registered user attempts to login with correct credentials.
    
    Expected Result:
        - Status Code: 200 OK.
        - Response Body: Must contain a valid JWT 'access_token' and 'token_type'.
    """
    email = "login_success@example.com"
    password = "correct_password"
    
    # Prerequisite: Register the user
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Login Tester"
    })
    
    # Attempt Login (OAuth2PasswordRequestForm expects form-data, not JSON)
    response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    """
    Test Case: Login with Incorrect Password.
    
    Scenario:
        A valid user attempts to login with the wrong password.
    
    Expected Result:
        - Status Code: 401 Unauthorized (or 400 depending on implementation).
        - Error Message: Incorrect email or password.
    """
    email = "wrong_pass@example.com"
    password = "my_password"
    
    # Prerequisite: Register
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Secure User"
    })
    
    # Attempt Login with wrong password
    response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "WRONG_PASSWORD"
    })
    
    # Usually 400 or 401 for bad credentials
    assert response.status_code in [400, 401]

def test_login_non_existent_user():
    """
    Test Case: Login with Non-Existent User.
    
    Scenario:
        An unregistered email attempts to login.
    
    Expected Result:
        - Status Code: 401 Unauthorized (or 400).
    """
    response = client.post("/api/v1/auth/login", data={
        "username": "ghost_user@example.com",
        "password": "any_password"
    })
    
    assert response.status_code in [400, 401]

def test_login_missing_form_data():
    """
    Test Case: Login Validation (Missing Data).
    
    Scenario:
        Client sends empty form data to login endpoint.
    
    Expected Result:
        - Status Code: 422 Unprocessable Entity.
    """
    response = client.post("/api/v1/auth/login", data={})
    
    assert response.status_code == 422

# --- 3. User Profile Tests (Protected Routes) ---

def test_get_current_user_success():
    """
    Test Case: Get Current User Profile.
    
    Scenario:
        A logged-in user requests their own profile using a valid Bearer token.
    
    Expected Result:
        - Status Code: 200 OK.
        - Response Body: User details matching the registered account.
    """
    email = "profile_test@example.com"
    password = "password123"
    
    # 1. Register
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Profile Owner"
    })
    
    # 2. Login to get token
    login_res = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password
    })
    token = login_res.json()["access_token"]
    
    # 3. Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_get_current_user_no_token():
    """
    Test Case: Access Protected Route without Token.
    
    Scenario:
        A client tries to access /auth/me without the Authorization header.
    
    Expected Result:
        - Status Code: 401 Unauthorized.
        - Detail: Not authenticated.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_get_current_user_invalid_token():
    """
    Test Case: Access Protected Route with Invalid Token.
    
    Scenario:
        A client sends a malformed or fake token.
    
    Expected Result:
        - Status Code: 401 Unauthorized or 403 Forbidden.
    """
    headers = {"Authorization": "Bearer invalid_token_string_123"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code in [401, 403]

# --- 4. HARDCORE / LIMITS & LIFECYCLE TESTS ---

def test_register_email_normalization():
    """
    Test Case: Email Normalization Validator.
    
    Scenario:
        User registers with messy casing and whitespace: "  MyEmail@Example.COM  ".
        
    Expected Result:
        - API saves clean version: "myemail@example.com".
        - Login works with the clean email.
        - Prevents duplicates (e.g., cannot register "myemail@example.com" afterwards).
    """
    messy_email = "  NormalizeMe@Example.COM  "
    clean_email = "normalizeme@example.com"
    password = "password123"
    
    # 1. Register with messy input
    response = client.post("/api/v1/auth/register", json={
        "email": messy_email,
        "password": password,
        "full_name": "Dirty Email User"
    })
    
    # Assert successful creation
    assert response.status_code == 201
    data = response.json()
    # Validator should have cleaned it
    assert data["email"] == clean_email 
    
    # 2. Verify Login works with the Clean Email
    login_res = client.post("/api/v1/auth/login", data={
        "username": clean_email, 
        "password": password
    })
    assert login_res.status_code == 200

    # 3. Verify Duplicate Check catches the clean version
    dup_res = client.post("/api/v1/auth/register", json={
        "email": clean_email, # Trying to register the clean version directly
        "password": "newpassword",
        "full_name": "Copy Cat"
    })
    assert dup_res.status_code == 400

def test_register_name_boundaries():
    """
    Test Case: Full Name Limits (Min & Max).
    
    Scenario:
        1. Try name with 0 characters (Empty).
        2. Try name with 151 characters (Limit is 150).
        
    Expected Result:
        - Both should return 422 Unprocessable Entity.
    """
    # Case 1: Empty Name
    res_empty = client.post("/api/v1/auth/register", json={
        "email": "empty@test.com", "password": "pass", "full_name": ""
    })
    assert res_empty.status_code == 422

    # Case 2: Too Long (151 chars)
    long_name = "A" * 151
    res_long = client.post("/api/v1/auth/register", json={
        "email": "long@test.com", "password": "pass", "full_name": long_name
    })
    assert res_long.status_code == 422
    # Ensure error is about full_name constraint, not something else
    assert "full_name" in str(res_long.json())

def test_update_profile_partial_and_password():
    """
    Test Case: Partial Update & Password Change.
    
    Scenario:
        1. User updates ONLY full_name (password should remain same).
        2. User updates ONLY password (security check).
    """
    email = "updater@example.com"
    original_pass = "password123"
    new_pass = "newsecurepass"
    
    # Setup: Register & Login
    client.post("/api/v1/auth/register", json={"email": email, "password": original_pass, "full_name": "Old Name"})
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": original_pass})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Update Name Only (Partial)
    res_name = client.put("/api/v1/auth/me", headers=headers, json={"full_name": "New Name"})
    assert res_name.status_code == 200
    assert res_name.json()["full_name"] == "New Name"
    assert res_name.json()["email"] == email # Email shouldn't change
    
    # 2. Update Password Only
    res_pass = client.put("/api/v1/auth/me", headers=headers, json={"password": new_pass})
    assert res_pass.status_code == 200
    
    # 3. Verify Old Password Fails
    fail_login = client.post("/api/v1/auth/login", data={"username": email, "password": original_pass})
    assert fail_login.status_code == 401
    
    # 4. Verify New Password Works
    success_login = client.post("/api/v1/auth/login", data={"username": email, "password": new_pass})
    assert success_login.status_code == 200

def test_soft_delete_lifecycle():
    """
    Test Case: Account Deletion Lifecycle (Soft Delete).
    
    Scenario:
        1. User deletes own account via API.
        2. API returns user object with is_deleted=True.
        3. Attempts to login afterwards should fail (410 Gone).
    """
    email = "deleted_user@example.com"
    password = "password123"
    
    # 1. Setup
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "To Delete"})
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Delete Action
    del_res = client.delete("/api/v1/auth/me", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["is_deleted"] is True
    
    # 3. Verify Login Block (Expect 410 as configured in auth.py)
    login_retry = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    
    # Note: Your auth.py code explicitly raises 410 for deleted users.
    assert login_retry.status_code == 410
    assert "deleted" in login_retry.json()["detail"].lower()

def test_security_tampered_token():
    """
    Test Case: JWT Integrity / Tampering.
    
    Scenario:
        A hacker takes a valid token, changes the last character (signature),
        and tries to use it.
        
    Expected Result:
        - API must reject with 401 (Could not validate credentials).
        - Proves that signature verification is active.
    """
    # 1. Login to get a valid token
    email = "security_check@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Sec Check"})
    
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    valid_token = login_res.json()["access_token"]
    
    # 2. Tamper with the token (Change the last character of the signature)
    # JWT format: header.payload.signature
    # If we change any char, the signature becomes invalid for that payload
    tampered_token = valid_token[:-5] + "AAAAA" # Brutal change at the end
    
    # 3. Try to access protected route
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    
    # Should fail because signature doesn't match
    assert response.status_code == 401

def test_security_sql_injection_attempt():
    """
    Test Case: SQL Injection on Login.
    
    Scenario:
        User tries classic SQL Injection payloads in the username field.
        e.g., "' OR '1'='1"
        
    Expected Result:
        - API should treat it as a literal string.
        - Should return 401 (Invalid credentials) or 422 (Validation Error).
        - MUST NOT return 500 (Server Error) or 200 (Bypass).
    """
    payload = {
        "username": "' OR '1'='1",
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=payload)
    
    # If SQLAlchemy is safe, it simply won't find a user with that email.
    # It should NOT crash (500).
    assert response.status_code in [401, 400, 422]