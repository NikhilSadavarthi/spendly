# Spec: Login and Logout

## Overview
This feature implements user session management, allowing registered users to securely log in to their Spendly accounts and log out when finished. This is step 03 of the Spendly roadmap, and it builds upon user registration to establish a secure, stateful session. Implementing login and logout is a prerequisite for protecting user-specific routes (such as the profile page and the expense dashboard) and ensuring that users can only view and manage their own financial data.

## Depends on
- Step 01: Database Setup
- Step 02: Registration

## Routes
- `GET /login` — Displays the login form. If already logged in, redirects to the landing page. — public
- `POST /login` — Validates credentials, checks hashed password, logs user in by storing user ID and name in session, and redirects to the landing page. — public
- `GET /logout` — Clears the user session, flashes a logout message, and redirects to the landing page. — logged-in

## Database changes
No database changes.

## Templates
- **Create:** None
- **Modify:**
  - `templates/base.html` — Update navigation links. If the user is logged in (`g.user` is defined), show "Profile" and "Sign out" links. If not logged in, show "Sign in" and "Get started" links.
  - `templates/landing.html` — Update the main CTA buttons so that if the user is logged in, they redirect to the profile page (upcoming Step 4) instead of the registration page.

## Files to change
- `app.py` — Configure imports for `session`, `g`, and `check_password_hash`. Implement `before_request` handler to set `g.user` based on session `user_id`. Update `/login` to support both `GET` and `POST` methods, implement credential check and session creation. Implement `/logout` to clear session and redirect.

## Files to create
- `tests/test_auth.py` — Automated test suite verifying login page load, login session persistence, authentication failure modes (wrong password, missing user), and logout session clearing.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- Visiting `GET /login` when not logged in returns the login form (status 200).
- Visiting `GET /login` when already logged in redirects to the landing page `/` (status 302).
- Submitting `POST /login` with empty email or password returns a 400 status code and displays "All fields are required."
- Submitting `POST /login` with an invalid email format returns a 400 status code and displays "Invalid email address format."
- Submitting `POST /login` with an email that does not exist or an incorrect password returns a 400 status code and displays "Invalid email or password."
- Submitting `POST /login` with valid credentials stores the user's ID in the session, sets a success flash message, and redirects to `/` (status 302).
- The navigation bar dynamically displays the user's name and links to "Profile" and "Sign out" when logged in, and "Sign in" and "Get started" when logged out.
- Visiting `GET /logout` clears the session, sets a success flash message "You have been logged out.", and redirects to `/` (status 302).
- Running `pytest` runs and passes all tests in `tests/test_auth.py`.
