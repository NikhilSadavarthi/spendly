from flask import session

def test_delete_expense_unauthenticated_redirects(client):
    """POST /expenses/1/delete when not logged in should redirect to /login."""
    response = client.post("/expenses/1/delete")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_delete_expense_method_not_allowed(client):
    """GET /expenses/1/delete should return 405 Method Not Allowed."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        response = client.get("/expenses/1/delete")
        assert response.status_code == 405


def test_delete_expense_success(client, db):
    """POST /expenses/id/delete removes the expense and redirects to profile."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Find one of Nitish's seeded expenses
        cursor = db.execute("SELECT id FROM expenses WHERE user_id = 1 LIMIT 1")
        expense = cursor.fetchone()
        expense_id = expense["id"]

        # Assert expense exists in database before delete
        cursor = db.execute("SELECT COUNT(*) FROM expenses WHERE id = ?", (expense_id,))
        assert cursor.fetchone()[0] == 1

        # Request deletion
        response = client.post(f"/expenses/{expense_id}/delete")
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # Assert expense no longer exists in database
        cursor = db.execute("SELECT COUNT(*) FROM expenses WHERE id = ?", (expense_id,))
        assert cursor.fetchone()[0] == 0


def test_delete_expense_ownership(client, db):
    """POST /expenses/id/delete for another user's or non-existent expense redirects to profile with error."""
    # 1. Non-existent expense ID
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        response = client.post("/expenses/9999/delete")
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # 2. Other user's expense
        # Insert a second user
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Other User", "other@example.com", "hashedpassword")
        )
        db.commit()

        # Find the second user's ID
        cursor = db.execute("SELECT id FROM users WHERE email = ?", ("other@example.com",))
        other_user_id = cursor.fetchone()["id"]

        # Insert an expense for this user
        db.execute(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            (other_user_id, "Bills", 500.0, "2026-06-11", "Other user bills")
        )
        db.commit()

        cursor = db.execute("SELECT id FROM expenses WHERE description = ?", ("Other user bills",))
        other_user_expense_id = cursor.fetchone()["id"]

        # Attempt to delete other user's expense as user_id = 1
        response = client.post(f"/expenses/{other_user_expense_id}/delete")
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # Assert expense still exists in the database
        cursor = db.execute("SELECT COUNT(*) FROM expenses WHERE id = ?", (other_user_expense_id,))
        assert cursor.fetchone()[0] == 1
