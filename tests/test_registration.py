from werkzeug.security import check_password_hash

def test_register_page_loads(client):
    """GET /register should load the registration form."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create your account" in response.data
    assert b'name="name"' in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_register_successful(client, db):
    """POST /register with valid inputs should persist the user and redirect to login."""
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "supersecurepassword123"
    }
    
    # Send registration request
    response = client.post("/register", data=data)
    
    # Should redirect (302) to login page
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    # Verify user exists in the database
    cursor = db.execute("SELECT * FROM users WHERE email = ?", (data["email"],))
    user = cursor.fetchone()
    assert user is not None
    assert user["name"] == data["name"]
    
    # Verify password is encrypted (not stored as plaintext)
    assert user["password"] != data["password"]
    assert check_password_hash(user["password"], data["password"])


def test_register_duplicate_email(client):
    """POST /register with an already registered email should return 400 and show error."""
    # "nitish@example.com" is seeded by conftest/seed_db
    data = {
        "name": "Nitish Alternate",
        "email": "nitish@example.com",
        "password": "password12345"
    }
    
    response = client.post("/register", data=data)
    
    assert response.status_code == 400
    assert b"Email already registered" in response.data


def test_register_password_too_short(client):
    """POST /register with a short password should return 400 and show error."""
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "short"
    }
    
    response = client.post("/register", data=data)
    
    assert response.status_code == 400
    assert b"Password must be at least 8 characters long" in response.data


def test_register_invalid_email(client):
    """POST /register with an invalid email format should return 400 and show error."""
    data = {
        "name": "Jane Doe",
        "email": "not-an-email",
        "password": "password123"
    }
    
    response = client.post("/register", data=data)
    
    assert response.status_code == 400
    assert b"Invalid email address format" in response.data


def test_register_missing_fields(client):
    """POST /register with missing/empty fields should return 400."""
    # Missing name
    data = {
        "name": "",
        "email": "jane@example.com",
        "password": "password123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 400
    assert b"All fields are required" in response.data

    # Missing email
    data = {
        "name": "Jane Doe",
        "email": "",
        "password": "password123"
    }
    response = client.post("/register", data=data)
    assert response.status_code == 400

    # Missing password
    data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": ""
    }
    response = client.post("/register", data=data)
    assert response.status_code == 400
