# Profile Page Design Implementation Plan

Implement the user profile view, statistics summary, profile info updates (name and email), and secure password updates.

## User Review Required

> [!NOTE]
> The profile page contains two separate forms: one for updating name and email, and one for changing the password. Updating the password successfully will clear the session and redirect the user to log in again with their new password.

## Open Questions

None. The user schema and database helper functions are already established in `database/db.py`.

## Proposed Changes

### Flask Application Route Handler

#### [MODIFY] [app.py](file:///home/nik/Desktop/expense-tracker/app.py)
- **Authentication Guard**: In the `/profile` and `/profile/password` routes, verify `g.user` is not `None`. If it is, flash a warning and redirect to `/login`.
- **GET `/profile`**:
  - Query the database for user stats:
    ```sql
    SELECT COUNT(*) as count, SUM(amount) as total FROM expenses WHERE user_id = ?
    ```
  - Default the sum to `0.0` if no expenses are returned.
  - Render `templates/profile.html` passing the stats.
- **POST `/profile` (Update Info)**:
  - Parse `name` and `email` from the form.
  - Validate: not empty, valid email format (contains `@` and `.`).
  - Validate email uniqueness: check if the email is already registered by another user.
    ```sql
    SELECT id FROM users WHERE email = ? AND id != ?
    ```
  - Update user name and email:
    ```sql
    UPDATE users SET name = ?, email = ? WHERE id = ?
    ```
  - Update `session["user_name"]` if the name changed.
  - Flash success message and redirect back to `/profile`.
- **POST `/profile/password` (Update Password)**:
  - Parse `current_password`, `new_password`, and `confirm_password` from the form.
  - Validate: not empty, `new_password` has at least 8 characters, and `new_password` matches `confirm_password`.
  - Validate that `current_password` matches `g.user['password']` using `check_password_hash()`.
  - Update password:
    ```sql
    UPDATE users SET password = ? WHERE id = ?
    ```
  - Clear the user session (`session.clear()`), flash a success message "Password updated successfully. Please log in again.", and redirect to `/login`.

### Templates

#### [CREATE] [templates/profile.html](file:///home/nik/Desktop/expense-tracker/templates/profile.html)
- Extend `base.html` and populate the page contents.
- Show flash messages/errors dynamically.
- Render profile header card:
  - Styled circle avatar displaying user's first letter of name (uppercase).
  - User's name and email.
- Render stats summary section:
  - Card 1: Total Expenses Tracked.
  - Card 2: Total Amount Spent (formatted in Rupees).
- Render forms container with two distinct forms:
  1. Profile Info Form: Fields for name and email.
  2. Change Password Form: Fields for current, new, and confirm password.

#### [MODIFY] [templates/base.html](file:///home/nik/Desktop/expense-tracker/templates/base.html)
- Ensure the navbar highlights the "Profile" link when the user is on the `/profile` page.

### Styling

#### [MODIFY] [static/css/style.css](file:///home/nik/Desktop/expense-tracker/static/css/style.css)
- Implement layout classes for:
  - Profile layout container.
  - Circle avatar using flex layout and background colors.
  - Statistics grid layout and statistics card styles.
  - Two-column responsive layout for profile update forms.

### Automated Tests

#### [CREATE] [tests/test_profile.py](file:///home/nik/Desktop/expense-tracker/tests/test_profile.py)
- `test_profile_page_unauthenticated_redirects`: Verifies that unauthorized users are redirected to login.
- `test_profile_page_loads_with_stats`: Verifies that logged-in users can load their profile, showing name, email, and correct seeded statistics.
- `test_profile_update_info_success`: Verifies successful profile updates (changing name/email) modify database records and update session name.
- `test_profile_update_info_validation`: Verifies input validations (empty name, invalid email, duplicate email) return 400.
- `test_profile_update_password_success`: Verifies successful password updates update database, hash passwords properly, clear sessions, and redirect.
- `test_profile_update_password_validation`: Verifies password validations (wrong current password, too short, mismatch new password) return 400.

## Verification Plan

### Automated Tests
- Run `pytest` via `venv/bin/python -m pytest tests/test_profile.py`.

### Manual Verification
- Start the Flask server: `./venv/bin/python app.py` and navigate to `http://localhost:5001/login`.
- Log in using seeded credentials: `nitish@example.com` / `password123`.
- Navigate to Profile page. Verify avatar, name, email, total expenses (4), and total amount spent (₹1,680.00).
- Edit the name and email, save, and confirm changes reflect in header, session, and DB.
- Change password: type valid current password and new password. Verify redirect to login, then sign in with the new password.
