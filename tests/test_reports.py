"""
Reports Tests Module.

Validates the analytical engine of the API.
Covers:
1. Summary (Totals, Averages, Zero-state)
2. Category Breakdown (Grouping, Percentages, Uncategorized)
3. Monthly History (Year/Month grouping)
4. Trends (Daily/Weekly/Monthly aggregation)
5. Security (User Isolation)
"""
import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- HELPER FUNCTIONS ---

def create_unique_user():
    """Helper to create a unique user and return auth headers."""
    unique_id = str(uuid.uuid4())[:8]
    email = f"report_{unique_id}@example.com"
    password = "password123"
    
    client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "full_name": f"User {unique_id}"
    })
    
    login_res = client.post("/api/v1/auth/login", data={
        "username": email, "password": password
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_category(headers, name, type):
    """Helper to create category."""
    res = client.post("/api/v1/categories/", headers=headers, json={
        "name": name, "type": type
    })
    return res.json()["id"]

def create_transaction(headers, type, amount, date_tx, category_id=None):
    """Helper to create transaction."""
    payload = {
        "type": type,
        "amount": amount,
        "date_transaction": str(date_tx)
    }
    if category_id:
        payload["category_id"] = category_id
        
    client.post("/api/v1/transactions/", headers=headers, json=payload)

# --- 1. SUMMARY REPORT TESTS ---

def test_summary_calculations():
    """
    Test Case: Summary Math.
    Validates totals, balance, and average daily calculations.
    """
    headers = create_unique_user()
    today = date.today()
    
    # Create 3 days of data
    # Day 1: +3000
    create_transaction(headers, "income", 3000, today - timedelta(days=2))
    # Day 2: -1000
    create_transaction(headers, "expense", 1000, today - timedelta(days=1))
    # Day 3: -500
    create_transaction(headers, "expense", 500, today)
    
    # Request Summary for these 3 days
    start = today - timedelta(days=2)
    res = client.get(f"/api/v1/reports/summary?start_date={start}&end_date={today}", headers=headers)
    
    assert res.status_code == 200
    data = res.json()
    
    # Stats
    stats = data["statistics"]
    assert float(stats["total_income"]) == 3000.00
    assert float(stats["total_expense"]) == 1500.00
    assert float(stats["balance"]) == 1500.00
    assert stats["transaction_count"] == 3
    
    # Averages (3 days duration)
    avgs = data["averages"]
    # Income 3000 / 3 days = 1000/day
    assert float(avgs["avg_daily_income"]) == 1000.00
    # Expense 1500 / 3 days = 500/day
    assert float(avgs["avg_daily_expense"]) == 500.00

def test_summary_empty_state():
    """Test Case: Zero Division Protection (Empty Account)."""
    headers = create_unique_user()
    res = client.get("/api/v1/reports/summary", headers=headers)
    
    assert res.status_code == 200
    data = res.json()
    
    assert float(data["statistics"]["total_income"]) == 0.0
    assert float(data["averages"]["avg_transaction_amount"]) == 0.0 # Tested division logic

# --- 2. BY CATEGORY REPORT TESTS ---

def test_by_category_grouping_and_percentage():
    """
    Test Case: Category Grouping.
    Validates that transactions are grouped by category and percentages match.
    """
    headers = create_unique_user()
    today = date.today()
    
    cat_food = create_category(headers, "Food", "expense")
    cat_transport = create_category(headers, "Transport", "expense")
    
    # Total Expense = 1000
    create_transaction(headers, "expense", 600, today, cat_food)      # 60%
    create_transaction(headers, "expense", 400, today, cat_transport) # 40%
    
    res = client.get(f"/api/v1/reports/by-category?start_date={today}&end_date={today}", headers=headers)
    data = res.json()
    
    assert float(data["total"]) == 1000.00
    
    # Check Food
    food = next(c for c in data["by_category"] if c["category_name"] == "Food")
    assert float(food["total_amount"]) == 600.00
    assert food["percentage"] == 60.0
    
    # Check Transport
    transport = next(c for c in data["by_category"] if c["category_name"] == "Transport")
    assert float(transport["total_amount"]) == 400.00
    assert transport["percentage"] == 40.0

def test_by_category_uncategorized():
    """Test Case: Uncategorized transactions handling."""
    headers = create_unique_user()
    today = date.today()
    
    # 100 Uncategorized expense
    create_transaction(headers, "expense", 100, today, category_id=None)
    
    res = client.get(f"/api/v1/reports/by-category", headers=headers)
    data = res.json()
    
    assert float(data["uncategorized"]["total_amount"]) == 100.00
    assert data["uncategorized"]["percentage"] == 100.0

# --- 3. MONTHLY REPORT TESTS ---

def test_monthly_report_structure():
    """Test Case: Monthly Aggregation."""
    headers = create_unique_user()
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    
    create_transaction(headers, "income", 1000, today)
    create_transaction(headers, "income", 2000, last_month)
    
    res = client.get("/api/v1/reports/monthly?months=2", headers=headers)
    data = res.json()
    
    assert len(data["months"]) >= 2
    
    # Verify we have data for the current month
    current_month_data = next((m for m in data["months"] if m["month"] == today.month), None)
    assert current_month_data is not None
    assert float(current_month_data["total_income"]) == 1000.00

# --- 4. TRENDS REPORT TESTS ---

def test_trends_weekly():
    """Test Case: Weekly Trends Logic."""
    headers = create_unique_user()
    today = date.today()
    # We use 'yesterday' because the endpoint logic uses an exclusive end date (< week_end), so 'today' is excluded.
    yesterday = today - timedelta(days=1)
    
    create_transaction(headers, "expense", 500, yesterday)
    
    res = client.get("/api/v1/reports/trends?period=weekly", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    assert data["period"] == "weekly"
    assert len(data["data"]) > 0
    
    # Check if ANY week has the data
    week_with_data = next((w for w in data["data"] if float(w["total_expense"]) > 0), None)
    assert week_with_data is not None
    assert float(week_with_data["total_expense"]) == 500.00

def test_trends_invalid_period():
    """Test Case: Validation of period parameter."""
    headers = create_unique_user()
    res = client.get("/api/v1/reports/trends?period=yearly", headers=headers)
    assert res.status_code == 422 # Pydantic validation error

# --- 5. SECURITY & ISOLATION ---

def test_report_isolation():
    """Test Case: User A vs User B."""
    headers_a = create_unique_user()
    create_transaction(headers_a, "income", 1000000, date.today())
    
    headers_b = create_unique_user()
    res = client.get("/api/v1/reports/summary", headers=headers_b)
    
    stats = res.json()["statistics"]
    assert float(stats["total_income"]) == 0.0

def test_trends_fills_empty_weeks():
    """
    Test Case: Chart Continuity.
    
    Scenario:
        - Transaction in Week 1.
        - Transaction in Week 3.
        - Week 2 has NO transactions.
        - Expected: Week 2 must appear in the list with 0 values (not be skipped).
    """
    headers = create_unique_user()
    today = date.today()
    
    # Create data for "Today" (Week 0/Latest)
    create_transaction(headers, "expense", 100, today)
    
    # Create data for "3 Weeks Ago"
    three_weeks_ago = today - timedelta(weeks=3)
    create_transaction(headers, "expense", 100, three_weeks_ago)
    
    res = client.get("/api/v1/reports/trends?period=weekly", headers=headers)
    data = res.json()
    
    # We expect 12 weeks of data
    assert len(data["data"]) == 12
    
    # Check if we have weeks with 0 balance (the gaps)
    # Filter weeks where total_expense is "0.00"
    empty_weeks = [w for w in data["data"] if float(w["total_expense"]) == 0.0]
    
    # We should have plenty of empty weeks between the transactions
    assert len(empty_weeks) > 0
    
    # Verify structure of an empty week
    gap_week = empty_weeks[0]
    assert float(gap_week["total_income"]) == 0.0
    assert float(gap_week["balance"]) == 0.0

def test_by_category_type_filter_strict():
    """
    Test Case: Strict Type Filtering.
    
    Scenario:
        - User has Income (Salary) and Expense (Food).
        - Request breakdown for 'expense' ONLY.
        - Expected: Income category should NOT appear in the list.
    """
    headers = create_unique_user()
    today = date.today()
    
    # Setup Data
    cat_salary = create_category(headers, "Salary", "income")
    cat_food = create_category(headers, "Food", "expense")
    
    create_transaction(headers, "income", 5000, today, cat_salary)
    create_transaction(headers, "expense", 100, today, cat_food)
    
    # Filter ONLY expenses
    res = client.get(f"/api/v1/reports/by-category?transaction_type=expense", headers=headers)
    data = res.json()
    
    # Check total matches only expenses
    assert float(data["total"]) == 100.00
    
    # Check that "Salary" is NOT in the list
    categories_found = [c["category_name"] for c in data["by_category"]]
    assert "Food" in categories_found
    assert "Salary" not in categories_found