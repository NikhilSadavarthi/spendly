# Spec: Profile Page Design

## Overview
This feature replaces the `/profile` stub with a beautifully designed, responsive profile page. It establishes the visual layout and templates for the profile view—including user information cards, edit profile forms, password change sections, and basic transaction statistics—using database queries to display user data and total expense counts before more complex expense filters are introduced.

## Depends on
- Step 01: Database Setup
- Step 02: Registration
- Step 03: Login and Logout

## Routes
- `GET /profile` — Displays the profile page showing user details and basic statistics. — logged-in
- `POST /profile` — Updates user information (name and email) with validation. — logged-in
- `POST /profile/password` — Updates user password with validation. — logged-in

## Database changes
No database changes.

## Templates
- **Create:**
  - `templates/profile.html` — User profile template containing details card, update forms, and statistics.
- **Modify:**
  - `templates/base.html` — Update navigation links to point to the new `/profile` route when logged in.

## Files to change
- `app.py` — Replace the placeholder `/profile` route with the full route handler, and add `/profile/password` POST handler.
- `static/css/style.css` — Add responsive layout styles, cards, form inputs, and buttons for the profile dashboard.

## Files to create
- `templates/profile.html`
- `tests/test_profile.py` — Automated tests to verify profile access, update validation, password modification, and access control.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- Visiting `GET /profile` when not logged in redirects to `/login` with an appropriate message.
- Visiting `GET /profile` when logged in renders the profile page with status 200.
- The profile page displays the user's name, email, and basic stats (e.g., number of expenses, total amount spent).
- Submitting `POST /profile` with empty name or email returns status 400 and displays validation error.
- Submitting `POST /profile` with an invalid email format returns status 400 and displays validation error.
- Submitting `POST /profile` with an email registered by another user returns status 400 and displays validation error.
- Submitting `POST /profile` with valid fields updates the details in the database and reloads the profile page with a success message.
- Submitting `POST /profile/password` with empty fields, mismatched passwords, or weak passwords (less than 8 characters) returns status 400 and displays validation error.
- Submitting `POST /profile/password` with an incorrect current password returns status 400 and displays validation error.
- Submitting `POST /profile/password` with valid details updates the password in the database, clears the session, and redirects to `/login` with a success message.

