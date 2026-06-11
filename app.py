from flask import Flask, render_template, request, redirect, url_for, flash
import os
from database.db import close_db, init_db, seed_db, DATABASE, get_db
from werkzeug.security import generate_password_hash

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


@app.route("/login")
def login():
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
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
