# Spec: Backend Integration for Profile Page

## Overview
This feature connects the profile page frontend design with full backend logic and database integration. It replaces mock data with dynamic database queries, adds interactive HTML forms for profile updates (name/email) and password changes directly to the profile view, and updates the automated test suite to verify the dynamic, database-driven statistics and validation logic.

## Depends on
- Step 01: Database Setup
- Step 02: Registration
- Step 03: Login and Logout
- Step 04: Profile Page Design

## Routes
- `GET /profile` — Displays the profile dashboard with dynamic user details, statistics, recent transactions, and category breakdown. — logged-in
- `POST /profile` — Validates and updates user information (name and email) in the database and session. — logged-in
- `POST /profile/password` — Validates, hashes, and updates user password in the database, clears the session, and redirects to `/login`. — logged-in

## Database changes
No database changes.

## Templates
- **Modify:**
  - `templates/profile.html` — Update to display dynamic stats, user details, recent transactions list, and category breakdown. Add forms for profile update (name and email) and password changes. Implement a tabbed interface (Overview vs. Settings) to present a clean, modern user experience.

## Files to change
- `app.py` — Update the `/profile` route handlers to fetch the actual recent transactions, category-wise spending totals, and top categories from the database.
- `templates/profile.html` — Replace mock data with dynamic Jinja variables and loops, add the settings forms, and add a simple tab switcher script.
- `static/css/style.css` — Add CSS styles for tabs, form groups, input fields, labels, buttons, and alert states in the profile dashboard context.
- `tests/test_profile.py` — Update assertions from hardcoded mock values (`8` and `12,450.75`) to correct database-driven totals (`4` and `1,680.00` based on seeded test data) and verify form validations.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- Visiting `GET /profile` when not logged in redirects to `/login` with an appropriate warning message.
- Visiting `GET /profile` when logged in renders the profile page with status 200, showing the logged-in user's actual name and email.
- The profile page statistics card (Total Spent, Transactions, Top Category) displays correct database-driven totals.
- The Recent Transactions table displays the logged-in user's 5 most recent transactions.
- The Category Breakdown section displays user expenses grouped by category, with percentage bars calculated dynamically.
- The Profile settings forms are accessible and styled professionally.
- Submitting `POST /profile` with invalid details (empty name/email, invalid email format, or email registered by another user) returns status 400 and displays an error message.
- Submitting `POST /profile` with valid inputs updates the database, updates the session username, and reloads the profile page with a success message.
- Submitting `POST /profile/password` with invalid details (empty fields, mismatched passwords, weak passwords under 8 chars, or incorrect current password) returns status 400 and displays an error message.
- Submitting `POST /profile/password` with valid details updates the password in the database, clears the session, and redirects to `/login` with a success message.
- Running `pytest` runs and passes all tests in `tests/test_profile.py`.
