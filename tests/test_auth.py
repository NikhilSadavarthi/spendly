from flask import session

def test_login_page_loads(client):
    """GET /login should load the login form."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_login_successful(client, db):
    """POST /login with valid credentials should set session and redirect to profile."""
    # "nitish@example.com" is seeded by conftest/seed_db with password "password123"
    data = {
        "email": "nitish@example.com",
        "password": "password123"
    }
    with client:
        response = client.post("/login", data=data)
        assert response.status_code == 302
        assert response.headers["Location"] == "/profile"
        assert session.get("user_id") is not None
        assert session.get("user_name") == "Nitish Kumar"


def test_login_invalid_credentials(client):
    """POST /login with incorrect credentials should return 400 and show error."""
    # Wrong password
    data = {
        "email": "nitish@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert b"Invalid email or password" in response.data

    # Non-existent email
    data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert b"Invalid email or password" in response.data


def test_login_missing_fields(client):
    """POST /login with missing/empty fields should return 400."""
    # Missing email
    data = {
        "email": "",
        "password": "password123"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert b"All fields are required" in response.data

    # Missing password
    data = {
        "email": "nitish@example.com",
        "password": ""
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert b"All fields are required" in response.data


def test_login_invalid_email_format(client):
    """POST /login with invalid email format should return 400."""
    data = {
        "email": "invalid-email",
        "password": "password123"
    }
    response = client.post("/login", data=data)
    assert response.status_code == 400
    assert b"Invalid email address format" in response.data


def test_login_already_logged_in_redirects(client):
    """GET /login should redirect to landing page if user is already logged in."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"
        
        response = client.get("/login")
        assert response.status_code == 302
        assert response.headers["Location"] == "/"


def test_logout_successful(client):
    """GET /logout should clear the session and redirect to landing."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"
        
        response = client.get("/logout")
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
        assert "user_id" not in session
        assert "user_name" not in session
