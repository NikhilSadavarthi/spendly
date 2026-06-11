# Spec: Registration

## Overview
This feature implements user registration, allowing new visitors to create an account on Spendly by providing their name, email, and password. This is step 02 of the Spendly roadmap, and it establishes user identity in the system, which is a prerequisite for user login, session management, and associating expenses with specific users.

## Depends on
- Step 01: Database Setup (establishes the `users` table and database connection helpers)

## Routes
- `GET /register` — Displays the registration form — public
- `POST /register` — Validates form inputs, hashes the password, inserts the user into the database, and redirects to the login page — public

## Database changes
No database changes. (The `users` table already has `id`, `name`, `email`, and `password` columns, which were created during the database setup phase).

## Templates
- **Create:** None
- **Modify:**
  - `templates/register.html` — Verify form submission target and ensure errors/flash messages are properly displayed.

## Files to change
- `app.py` — Configure a secret key for session/flash messages, import `get_db` and `generate_password_hash`, implement the `POST` handler for `/register` with validation logic, database insertion, and flash messaging.

## Files to create
- `tests/conftest.py` — Pytest configuration with fixtures for the Flask application test client and an isolated, temporary SQLite database.
- `tests/test_registration.py` — Automated test suite verifying registration page load, successful registration, duplicate email handling, validation errors (short password, invalid email format), and missing fields.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- Visiting `GET /register` returns the registration page (status 200).
- Submitting the form with valid inputs (name, unique and properly formatted email, password of 8+ characters) hashes the password using `werkzeug.security.generate_password_hash`, stores the user in the database, and redirects to `/login` with a success message.
- Submitting with an existing email displays "Email already registered" and returns a 400 status code.
- Submitting with a password of fewer than 8 characters displays "Password must be at least 8 characters long" and returns a 400 status code.
- Submitting with an invalid email format or empty name displays a clear validation error and returns a 400 status code.
- Running `pytest` runs and passes all tests in `tests/test_registration.py`.
