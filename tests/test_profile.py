from flask import session
from werkzeug.security import check_password_hash

def test_profile_unauthenticated_redirects(client):
    """GET /profile when not logged in should redirect to /login."""
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    # Post to profile should also redirect
    response = client.post("/profile", data={"name": "Test", "email": "test@example.com"})
    assert response.status_code == 302

    # Post to profile password should also redirect
    response = client.post("/profile/password", data={})
    assert response.status_code == 302


def test_profile_page_loads_with_stats(client, db):
    """GET /profile when logged in should load user stats and details."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Nitish Kumar" in response.data
        assert b"nitish@example.com" in response.data
        # Stats checks: count of 8, total of 12,450.75
        assert b"8" in response.data
        assert b"12,450.75" in response.data


def test_profile_update_info_success(client, db):
    """POST /profile with valid details should update DB, session, and redirect."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        data = {
            "name": "Nitish Patel",
            "email": "nitish.patel@example.com"
        }
        response = client.post("/profile", data=data)
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"

        # Verify database updated
        user = db.execute("SELECT * FROM users WHERE id = 1").fetchone()
        assert user["name"] == "Nitish Patel"
        assert user["email"] == "nitish.patel@example.com"

        # Verify session updated
        assert session["user_name"] == "Nitish Patel"


def test_profile_update_info_validation(client, db):
    """POST /profile with validation errors should return 400."""
    # Insert another user to test duplicate email check
    db.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        ("Other User", "other@example.com", "hashed_pwd")
    )
    db.commit()

    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # 1. Missing name
        data = {"name": "", "email": "nitish@example.com"}
        response = client.post("/profile", data=data)
        assert response.status_code == 400
        assert b"Name and email are required." in response.data

        # 2. Invalid email format
        data = {"name": "Nitish Kumar", "email": "nitish-at-example.com"}
        response = client.post("/profile", data=data)
        assert response.status_code == 400
        assert b"Invalid email address format." in response.data

        # 3. Duplicate email
        data = {"name": "Nitish Kumar", "email": "other@example.com"}
        response = client.post("/profile", data=data)
        assert response.status_code == 400
        assert b"Email already registered." in response.data


def test_profile_update_password_success(client, db):
    """POST /profile/password with valid inputs should update DB, clear session, and redirect to login."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        data = {
            "current_password": "password123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = client.post("/profile/password", data=data)
        assert response.status_code == 302
        assert response.headers["Location"] == "/login"

        # Verify session is cleared
        assert "user_id" not in session

        # Verify database has updated hashed password
        user = db.execute("SELECT * FROM users WHERE id = 1").fetchone()
        assert check_password_hash(user["password"], "newpassword123")


def test_profile_update_password_validation(client, db):
    """POST /profile/password with validation errors should return 400."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # 1. Missing fields
        data = {"current_password": "", "new_password": "newpassword123", "confirm_password": "newpassword123"}
        response = client.post("/profile/password", data=data)
        assert response.status_code == 400
        assert b"All password fields are required." in response.data

        # 2. Incorrect current password
        data = {"current_password": "wrongpassword", "new_password": "newpassword123", "confirm_password": "newpassword123"}
        response = client.post("/profile/password", data=data)
        assert response.status_code == 400
        assert b"Incorrect current password." in response.data

        # 3. Short new password
        data = {"current_password": "password123", "new_password": "short", "confirm_password": "short"}
        response = client.post("/profile/password", data=data)
        assert response.status_code == 400
        assert b"Password must be at least 8 characters long." in response.data

        # 4. Mismatched confirm password
        data = {"current_password": "password123", "new_password": "newpassword123", "confirm_password": "mismatchpassword"}
        response = client.post("/profile/password", data=data)
        assert response.status_code == 400
        assert b"New passwords do not match." in response.data
