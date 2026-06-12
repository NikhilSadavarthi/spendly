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
        # Stats checks: count of 4, total of 1,680.00
        assert b"4" in response.data
        assert b"1,680.00" in response.data


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


def test_profile_date_filter_presets(client, db):
    """GET /profile with presets should calculate ranges relative to today and filter correctly."""
    import datetime
    import calendar

    # Log in as user 1
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Clear existing expenses to ensure deterministic tests
        db.execute("DELETE FROM expenses")
        db.commit()

        today = datetime.date.today()
        
        # Calculate preset boundaries
        # 1. This Month
        start_of_month = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=last_day)
        
        # 2. Last 30 Days
        start_last_30 = today - datetime.timedelta(days=30)
        
        # 3. This Year
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        
        # Insert test expenses
        # A. Inside this month, inside last 30, inside this year
        db.execute(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Food', 100.0, ?, 'This Month')",
            (today.strftime("%Y-%m-%d"),)
        )
        
        # B. Outside this month, but inside last 30, inside this year
        # (This is only possible if start of month is < 30 days ago, i.e., today.day < 30)
        # To be safe, let's insert a date exactly 25 days ago.
        date_25_days_ago = today - datetime.timedelta(days=25)
        # Check if 25 days ago is in a different month
        is_diff_month = date_25_days_ago.month != today.month
        db.execute(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Travel', 200.0, ?, '25 Days Ago')",
            (date_25_days_ago.strftime("%Y-%m-%d"),)
        )
        
        # C. Outside this month, outside last 30, but inside this year
        # Let's find a date in this year that is definitely outside last 30 days.
        if today.month > 2:
            date_this_year_outside_30 = today.replace(month=1, day=1)
            db.execute(
                "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Bills', 400.0, ?, 'This Year Outside 30')",
                (date_this_year_outside_30.strftime("%Y-%m-%d"),)
            )
            has_this_year_outside_30 = True
        else:
            has_this_year_outside_30 = False
            
        # D. Outside this year (Last Year)
        date_last_year = today.replace(year=today.year - 1, month=6, day=15)
        db.execute(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Health', 800.0, ?, 'Last Year')",
            (date_last_year.strftime("%Y-%m-%d"),)
        )
        
        db.commit()

        # Let's test "all" preset (All Time)
        response = client.get("/profile?filter_type=all")
        assert response.status_code == 200
        # Total count should be 3 or 4 depending on whether has_this_year_outside_30 is True
        expected_all_count = 4 if has_this_year_outside_30 else 3
        expected_all_sum = 1500.0 if has_this_year_outside_30 else 700.0
        assert str(expected_all_count).encode() in response.data
        assert f"{expected_all_sum:,.2f}".encode() in response.data

        # Let's test "this_month" preset
        response = client.get("/profile?filter_type=this_month")
        assert response.status_code == 200
        # Filtered to this month
        # This month expenses: 'This Month' (100.0) always. If 25 days ago is also in this month, it will be included.
        this_month_count = 1
        this_month_sum = 100.0
        if not is_diff_month:
            this_month_count += 1
            this_month_sum += 200.0
        assert str(this_month_count).encode() in response.data
        assert f"{this_month_sum:,.2f}".encode() in response.data

        # Let's test "last_30_days" preset
        response = client.get("/profile?filter_type=last_30_days")
        assert response.status_code == 200
        # Last 30 days: 'This Month' (100.0) and '25 Days Ago' (200.0) are both in last 30 days.
        # Total sum: 300.0
        assert b"2" in response.data
        assert b"300.00" in response.data

        # Let's test "this_year" preset
        response = client.get("/profile?filter_type=this_year")
        assert response.status_code == 200
        # This year expenses: 'This Month' (100.0), '25 Days Ago' (200.0) always.
        # Plus 'This Year Outside 30' (400.0) if has_this_year_outside_30.
        this_year_count = 3 if has_this_year_outside_30 else 2
        this_year_sum = 700.0 if has_this_year_outside_30 else 300.0
        assert str(this_year_count).encode() in response.data
        assert f"{this_year_sum:,.2f}".encode() in response.data


def test_profile_date_filter_custom_success(client, db):
    """GET /profile with custom date filters should restrict dashboard data correctly."""
    # Log in as user 1
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # Clear existing expenses
        db.execute("DELETE FROM expenses")
        
        # Insert test expenses
        db.execute("INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Food', 100.0, '2026-06-08', 'Day 1')")
        db.execute("INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Travel', 200.0, '2026-06-09', 'Day 2')")
        db.execute("INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Bills', 400.0, '2026-06-10', 'Day 3')")
        db.execute("INSERT INTO expenses (user_id, category, amount, date, description) VALUES (1, 'Health', 800.0, '2026-06-11', 'Day 4')")
        db.commit()

        # Filter: 2026-06-09 to 2026-06-10
        response = client.get("/profile?filter_type=custom&start_date=2026-06-09&end_date=2026-06-10")
        assert response.status_code == 200
        # Should show 2 expenses (200.0 and 400.0)
        # Total sum: 600.0
        assert b"2" in response.data
        assert b"600.00" in response.data
        assert b"Showing expenses from <strong>2026-06-09</strong> to <strong>2026-06-10</strong>" in response.data
        assert b"value=\"2026-06-09\"" in response.data
        assert b"value=\"2026-06-10\"" in response.data


def test_profile_date_filter_custom_validation_errors(client, db):
    """GET /profile with invalid custom parameters should return status 400."""
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Nitish Kumar"

        # 1. Missing start or end date
        response = client.get("/profile?filter_type=custom&start_date=2026-06-08&end_date=")
        assert response.status_code == 400
        assert b"Both start date and end date are required for custom filter." in response.data

        # 2. Start date after end date
        response = client.get("/profile?filter_type=custom&start_date=2026-06-10&end_date=2026-06-08")
        assert response.status_code == 400
        assert b"Start date cannot be after end date." in response.data

        # 3. Invalid date format
        response = client.get("/profile?filter_type=custom&start_date=2026-06-08&end_date=invalid-date")
        assert response.status_code == 400
        assert b"Invalid date format. Please use YYYY-MM-DD." in response.data

