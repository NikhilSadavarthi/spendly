import datetime
from flask import session

def test_add_expense_unauthenticated_redirects(client):
    """GET /expenses/add when not logged in should redirect to /login."""
    response = client.get("/expenses/add")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # POST /expenses/add when not logged in should also redirect
    response = client.post("/expenses/add", data={
        "category": "Food",
        "amount": "150.00",
        "date": "2026-06-12",
        "description": "Lunch"
    })
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_expense_page_loads(client):
    """GET /expenses/add when logged in should load the add expense page."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        response = client.get("/expenses/add")
        assert response.status_code == 200
        assert b"Add Expense" in response.data
        assert b"Log a new expense" in response.data
        
        # Verify today's date is in the response as the default input value
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        assert today_date.encode('utf-8') in response.data


def test_add_expense_success(client, db):
    """POST /expenses/add with valid details should insert to DB and redirect."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        data = {
            "category": "Shopping",
            "amount": "2499.50",
            "date": "2026-06-11",
            "description": "New headphones"
        }
        
        # Verify initial database count of Shopping expenses
        cursor = db.execute("SELECT COUNT(*) FROM expenses WHERE user_id = 1 AND category = 'Shopping'")
        assert cursor.fetchone()[0] == 0
        
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"
        
        # Verify expense is now in the database
        cursor = db.execute("SELECT * FROM expenses WHERE user_id = 1 AND category = 'Shopping'")
        expense = cursor.fetchone()
        assert expense is not None
        assert expense["amount"] == 2499.50
        assert expense["date"] == "2026-06-11"
        assert expense["description"] == "New headphones"


def test_add_expense_validation_errors(client, db):
    """POST /expenses/add with invalid data should return 400 with error message."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # 1. Missing required field (amount)
        data = {
            "category": "Food",
            "date": "2026-06-12",
            "description": "Lunch"
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Category, amount, and date are required." in response.data

        # 2. Invalid category
        data = {
            "category": "Luxury",
            "amount": "100.00",
            "date": "2026-06-12"
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Invalid category selected." in response.data

        # 3. Non-positive amount
        data = {
            "category": "Food",
            "amount": "-50.00",
            "date": "2026-06-12"
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Amount must be a positive number." in response.data

        # 4. Zero amount
        data = {
            "category": "Food",
            "amount": "0",
            "date": "2026-06-12"
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Amount must be a positive number." in response.data

        # 5. Invalid date format
        data = {
            "category": "Food",
            "amount": "120.00",
            "date": "12-06-2026"
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Invalid date format. Use YYYY-MM-DD." in response.data

        # 6. Description too long (> 200 chars)
        data = {
            "category": "Food",
            "amount": "120.00",
            "date": "2026-06-12",
            "description": "a" * 201
        }
        response = client.post("/expenses/add", data=data)
        assert response.status_code == 400
        assert b"Description must be 200 characters or less." in response.data
