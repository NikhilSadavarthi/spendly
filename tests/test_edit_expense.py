from flask import session

def test_edit_expense_unauthenticated_redirects(client):
    """GET /expenses/1/edit when not logged in should redirect to /login."""
    response = client.get("/expenses/1/edit")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # POST /expenses/1/edit when not logged in should also redirect
    response = client.post("/expenses/1/edit", data={
        "category": "Food",
        "amount": "150.00",
        "date": "2026-06-12",
        "description": "Lunch"
    })
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_edit_expense_ownership(client, db):
    """GET/POST /expenses/id/edit should redirect to /profile with error if unauthorized/nonexistent."""
    # Seed another user's expense (user_id=2 or nonexistent id)
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # 1. Non-existent expense
        response = client.get("/expenses/9999/edit")
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        response = client.post("/expenses/9999/edit", data={
            "category": "Food",
            "amount": "150.00",
            "date": "2026-06-12"
        })
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # 2. Expense owned by someone else
        # Insert another user first to satisfy foreign key constraint
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Other User", "other@example.com", "otherpassword")
        )
        db.commit()

        # Insert expense for user_id = 2
        db.execute(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            (2, "Bills", 500.0, "2026-06-11", "Other user bills")
        )
        db.commit()
        
        cursor = db.execute("SELECT id FROM expenses WHERE description = ?", ("Other user bills",))
        other_user_expense_id = cursor.fetchone()["id"]

        response = client.get(f"/expenses/{other_user_expense_id}/edit")
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        response = client.post(f"/expenses/{other_user_expense_id}/edit", data={
            "category": "Bills",
            "amount": "600.0",
            "date": "2026-06-11"
        })
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"


def test_edit_expense_page_loads(client, db):
    """GET /expenses/id/edit pre-populates form fields with current values."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Find Nitish's seeded expense
        cursor = db.execute("SELECT id FROM expenses WHERE user_id = 1 LIMIT 1")
        expense_id = cursor.fetchone()["id"]

        response = client.get(f"/expenses/{expense_id}/edit")
        assert response.status_code == 200
        assert b"Edit Expense" in response.data
        assert b"Update your expense details below" in response.data
        # Verify preset fields are present in the response
        assert b"Dinner at restaurant" in response.data or b"Auto ride" in response.data or b"Internet subscription" in response.data


def test_edit_expense_success(client, db):
    """POST /expenses/id/edit with valid data updates database and redirects."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Find Nitish's seeded expense
        cursor = db.execute("SELECT id, amount FROM expenses WHERE user_id = 1 LIMIT 1")
        expense = cursor.fetchone()
        expense_id = expense["id"]
        old_amount = expense["amount"]

        new_data = {
            "category": "Food",
            "amount": str(old_amount + 50.0),
            "date": "2026-06-12",
            "description": "Updated Dinner"
        }

        response = client.post(f"/expenses/{expense_id}/edit", data=new_data)
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # Verify updated values in the DB
        cursor = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        updated_expense = cursor.fetchone()
        assert updated_expense["amount"] == old_amount + 50.0
        assert updated_expense["description"] == "Updated Dinner"
        assert updated_expense["date"] == "2026-06-12"


def test_edit_expense_validation_errors(client, db):
    """POST /expenses/id/edit with invalid fields should return 400."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Find Nitish's seeded expense
        cursor = db.execute("SELECT id FROM expenses WHERE user_id = 1 LIMIT 1")
        expense_id = cursor.fetchone()["id"]

        # 1. Missing required field (category)
        data = {
            "amount": "150.00",
            "date": "2026-06-12"
        }
        response = client.post(f"/expenses/{expense_id}/edit", data=data)
        assert response.status_code == 400
        assert b"Category, amount, and date are required." in response.data

        # 2. Invalid category
        data = {
            "category": "Traveler",
            "amount": "150.00",
            "date": "2026-06-12"
        }
        response = client.post(f"/expenses/{expense_id}/edit", data=data)
        assert response.status_code == 400
        assert b"Invalid category selected." in response.data

        # 3. Non-positive amount
        data = {
            "category": "Food",
            "amount": "-5.00",
            "date": "2026-06-12"
        }
        response = client.post(f"/expenses/{expense_id}/edit", data=data)
        assert response.status_code == 400
        assert b"Amount must be a positive number." in response.data

        # 4. Invalid date format
        data = {
            "category": "Food",
            "amount": "150.00",
            "date": "12-06-2026"
        }
        response = client.post(f"/expenses/{expense_id}/edit", data=data)
        assert response.status_code == 400
        assert b"Invalid date format. Use YYYY-MM-DD." in response.data

        # 5. Description too long
        data = {
            "category": "Food",
            "amount": "150.00",
            "date": "2026-06-12",
            "description": "x" * 201
        }
        response = client.post(f"/expenses/{expense_id}/edit", data=data)
        assert response.status_code == 400
        assert b"Description must be 200 characters or less." in response.data
