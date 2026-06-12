# Spec: Add Expense

## Overview
Step 7 adds the ability for authenticated users to log new expenses. It provides a dedicated form interface at `/expenses/add` to capture category, amount, date, and description. The form performs server-side validation to ensure that all required fields are present, the category is valid, the amount is positive, and the date is well-formed. Successful entries are saved to the SQLite database, and the user is redirected back to their profile dashboard with a success message, where the new transaction and updated stats are immediately visible.

## Depends on
- Step 1: Database Setup (`expenses` table must exist)
- Step 3: Login and Logout (authentication mechanism must exist)
- Step 4: Profile Page Design (dashboard where expenses are displayed and linked)

## Routes
- `GET /expenses/add` — renders the "Add Expense" form — logged-in
- `POST /expenses/add` — validates and saves the new expense — logged-in

If a non-logged-in user attempts to access either route, they must be redirected to `/login` with a flash message: "Please log in to access this page."

## Database changes
No database changes. The `expenses` table already contains the required columns: `id`, `user_id`, `category`, `amount`, `date`, and `description`.

## Templates
- **Create:**
  - `templates/add_expense.html` — Form template for adding a new expense, extending `base.html`.
- **Modify:**
  - `templates/profile.html` — Add a prominent "+ Add Expense" CTA button/link on the profile page dashboard (within the overview tab) that redirects the user to `/expenses/add`.

## Files to change
- `app.py`
  - Update `/expenses/add` route to handle both `GET` and `POST` requests.
  - Implement authentication checks (redirecting to `/login` if not authenticated).
  - On `GET`, render the `add_expense.html` template, pre-populating the date input with today's date.
  - On `POST`, extract and validate form data:
    - `amount` must be a positive float greater than 0.
    - `category` must be one of: `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`.
    - `date` must be a valid ISO format date (`YYYY-MM-DD`).
    - `description` should be trimmed and optional.
  - Save valid expenses to the database under the current user's ID.
  - Redirect to `/profile` with a flash message: "Expense added successfully!".
- `templates/profile.html`
  - Add the "+ Add Expense" CTA button next to the filter bar or header.

## Files to create
- `templates/add_expense.html`
- `tests/test_add_expense.py`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Form validation:
  - Return `400 Bad Request` with an appropriate error message if validation fails.
  - Ensure the category matches the allowed options exactly (case-sensitive on backend validation).
- Handle database commit/rollback properly inside try-except blocks.

## Definition of done
- [ ] Visiting `/expenses/add` without logging in redirects to `/login` with a flash message.
- [ ] Logged-in users see the Add Expense form at `/expenses/add` with fields: Category (dropdown), Amount, Date, and Description.
- [ ] The Date field defaults to today's date in `YYYY-MM-DD` format.
- [ ] Submitting the form with valid data inserts a record in `expenses` database table, redirects to `/profile`, and flashes "Expense added successfully!".
- [ ] The new expense is immediately visible in the "Recent Transactions" table and correctly updates "Total Spent", "Transactions", and "By Category" breakdown on the dashboard.
- [ ] Submitting with an amount of 0, negative, or non-numeric returns a 400 error page or validation message and does not save to DB.
- [ ] Submitting with an invalid date format returns a 400 error.
- [ ] Submitting with an invalid or empty category returns a 400 error.
- [ ] The cancel button on the form page redirects the user back to the profile page without adding anything.
- [ ] Run `pytest tests/test_add_expense.py` and ensure all tests pass.
