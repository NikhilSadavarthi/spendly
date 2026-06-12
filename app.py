from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os
import datetime
import calendar
from database.db import close_db, init_db, seed_db, DATABASE, get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

# Register database close teardown
@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

# Initialize and seed database if it doesn't exist
with app.app_context():
    if not os.path.exists(DATABASE):
        init_db()
        seed_db()

@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()



# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # 1. Validation: check if fields are present and not empty
        if not name or not email or not password:
            return render_template("register.html", error="All fields are required."), 400

        # 2. Validation: email format check
        if "@" not in email or "." not in email.split("@")[-1]:
            return render_template("register.html", error="Invalid email address format."), 400

        # 3. Validation: password length check
        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters long."), 400

        # 4. Check if email already exists
        db = get_db()
        cursor = db.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            return render_template("register.html", error="Email already registered."), 400

        # 5. Insert new user
        hashed_password = generate_password_hash(password)
        try:
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            db.commit()
        except Exception as e:
            db.rollback()
            return render_template("register.html", error="An error occurred during registration. Please try again."), 500

        flash("Registration successful! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="All fields are required."), 400

        if "@" not in email or "." not in email.split("@")[-1]:
            return render_template("login.html", error="Invalid email address format."), 400

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid email or password."), 400

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


def get_profile_dashboard_data(db, user_id, start_date=None, end_date=None):
    query_params = [user_id]
    date_filter = ""
    if start_date:
        date_filter += " AND date >= ?"
        query_params.append(start_date)
    if end_date:
        date_filter += " AND date <= ?"
        query_params.append(end_date)

    stats_query = f"SELECT COUNT(*) as count, COALESCE(SUM(amount), 0.0) as total FROM expenses WHERE user_id = ?{date_filter}"
    stats = db.execute(stats_query, query_params).fetchone()
    total_expenses_count = stats["count"]
    total_amount_spent = stats["total"]

    tx_query = f"SELECT id, category, amount, date, description FROM expenses WHERE user_id = ?{date_filter} ORDER BY date DESC, id DESC LIMIT 5"
    recent_transactions = db.execute(tx_query, query_params).fetchall()

    cat_query = f"SELECT category, SUM(amount) as amount_sum FROM expenses WHERE user_id = ?{date_filter} GROUP BY category ORDER BY amount_sum DESC"
    category_breakdown_rows = db.execute(cat_query, query_params).fetchall()

    category_breakdown = []
    top_category = None
    if category_breakdown_rows:
        top_category = category_breakdown_rows[0]["category"]
        for row in category_breakdown_rows:
            pct = 0.0
            if total_amount_spent > 0:
                pct = (row["amount_sum"] / total_amount_spent) * 100
            category_breakdown.append({
                "category": row["category"],
                "amount_sum": row["amount_sum"],
                "percentage": pct
            })

    return {
        "total_expenses_count": total_expenses_count,
        "total_amount_spent": total_amount_spent,
        "recent_transactions": recent_transactions,
        "category_breakdown": category_breakdown,
        "top_category": top_category
    }


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if g.user is None:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    db = get_db()
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            data = get_profile_dashboard_data(db, g.user["id"])
            return render_template(
                "profile.html",
                error="Name and email are required.",
                filter_type="all",
                start_date="",
                end_date="",
                start_date_val=None,
                end_date_val=None,
                **data
            ), 400

        if "@" not in email or "." not in email.split("@")[-1]:
            data = get_profile_dashboard_data(db, g.user["id"])
            return render_template(
                "profile.html",
                error="Invalid email address format.",
                filter_type="all",
                start_date="",
                end_date="",
                start_date_val=None,
                end_date_val=None,
                **data
            ), 400

        # Check for duplicate email (excluding current user)
        cursor = db.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, g.user["id"]))
        if cursor.fetchone() is not None:
            data = get_profile_dashboard_data(db, g.user["id"])
            return render_template(
                "profile.html",
                error="Email already registered.",
                filter_type="all",
                start_date="",
                end_date="",
                start_date_val=None,
                end_date_val=None,
                **data
            ), 400

        # Update user info
        try:
            db.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, g.user["id"]))
            db.commit()
            session["user_name"] = name
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            db.rollback()
            data = get_profile_dashboard_data(db, g.user["id"])
            return render_template(
                "profile.html",
                error="An error occurred. Please try again.",
                filter_type="all",
                start_date="",
                end_date="",
                start_date_val=None,
                end_date_val=None,
                **data
            ), 500

    # GET request: fetch user statistics with optional date filtering
    filter_type = request.args.get("filter_type", "all").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    if filter_type not in ["all", "this_month", "last_30_days", "this_year", "custom"]:
        filter_type = "all"

    start_date_val = None
    end_date_val = None
    error = None

    today = datetime.date.today()

    if filter_type == "this_month":
        start_date_val = today.replace(day=1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date_val = today.replace(day=last_day).strftime("%Y-%m-%d")
    elif filter_type == "last_30_days":
        start_date_val = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        end_date_val = today.strftime("%Y-%m-%d")
    elif filter_type == "this_year":
        start_date_val = today.replace(month=1, day=1).strftime("%Y-%m-%d")
        end_date_val = today.replace(month=12, day=31).strftime("%Y-%m-%d")
    elif filter_type == "custom":
        if not start_date or not end_date:
            error = "Both start date and end date are required for custom filter."
        else:
            try:
                parsed_start = datetime.date.fromisoformat(start_date)
                parsed_end = datetime.date.fromisoformat(end_date)
                if parsed_start > parsed_end:
                    error = "Start date cannot be after end date."
                else:
                    start_date_val = start_date
                    end_date_val = end_date
            except ValueError:
                error = "Invalid date format. Please use YYYY-MM-DD."

    if error:
        # Fallback to no filter, return status 400
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error=error,
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 400

    data = get_profile_dashboard_data(db, g.user["id"], start_date_val, end_date_val)
    return render_template(
        "profile.html",
        filter_type=filter_type,
        start_date=start_date,
        end_date=end_date,
        start_date_val=start_date_val,
        end_date_val=end_date_val,
        **data
    )


@app.route("/profile/password", methods=["POST"])
def profile_password():
    if g.user is None:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    db = get_db()

    if not current_password or not new_password or not confirm_password:
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error="All password fields are required.",
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 400

    if not check_password_hash(g.user["password"], current_password):
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error="Incorrect current password.",
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 400

    if len(new_password) < 8:
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error="Password must be at least 8 characters long.",
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 400

    if new_password != confirm_password:
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error="New passwords do not match.",
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 400

    # Hash and update
    hashed_password = generate_password_hash(new_password)
    try:
        db.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, g.user["id"]))
        db.commit()
    except Exception as e:
        db.rollback()
        data = get_profile_dashboard_data(db, g.user["id"])
        return render_template(
            "profile.html",
            error="An error occurred. Please try again.",
            filter_type="all",
            start_date="",
            end_date="",
            start_date_val=None,
            end_date_val=None,
            **data
        ), 500

    # Clear session and redirect to login
    session.clear()
    flash("Password updated successfully. Please log in again.", "success")
    return redirect(url_for("login"))


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
