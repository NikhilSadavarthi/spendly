# Spec: Delete Expense

## Overview
Step 9 introduces the ability for a logged-in user to delete their own expenses. A "Delete" action button (represented by a trash icon) is added next to the "Edit" action button in the transactions table on the profile/dashboard page. Clicking it prompts for confirmation before sending a secure `POST` request to `/expenses/<id>/delete` to remove the expense from the database. This ensures that users can easily manage and correct their records, while maintaining security and avoiding accidental deletions.

## Depends on
- Step 1: Database Setup (`expenses` table exists with correct schema)
- Step 3: Login and Logout (`session["user_id"]` is set and verified)
- Step 5: Backend routes for Profile page / templates (recent transactions list)
- Step 8: Edit Expense (actions column added in profile template)

## Routes
- `POST /expenses/<int:id>/delete` — Delete the specified expense — logged-in only

## Database changes
No database changes. All required columns and tables already exist.

## Templates
- **Modify**: `templates/profile.html`
  - Inside the transactions table action column (in `recent_transactions` list), add a form with `method="POST"` that submits to `/expenses/{{ tx.id }}/delete`.
  - The form should contain a delete button with a trash icon (using Lucide icon `trash-2`).
  - Add `onsubmit="return confirm('Are you sure you want to delete this expense?');"` to the form to prevent accidental deletion.
  - Align the Edit link and Delete button horizontally inside a flexbox container in the actions cell.

## Files to change
- `app.py`:
  - Replace the GET-only placeholder at `/expenses/<int:id>/delete` with a full POST-only handler:
    - Route decorator: `@app.route("/expenses/<int:id>/delete", methods=["POST"])`
    - Login check: redirect to `/login` if `g.user` is None.
    - Expense ownership check: fetch the expense with `SELECT * FROM expenses WHERE id = ? AND user_id = ?`. If it doesn't exist or doesn't belong to the logged-in user, flash an error ("Expense not found.") and redirect to `/profile`.
    - Delete operation: execute `DELETE FROM expenses WHERE id = ? AND user_id = ?` and commit the transaction.
    - Flash a success message ("Expense deleted successfully!") and redirect to `/profile`.
- `templates/profile.html`:
  - Add the delete button form next to the edit link.
- `static/css/style.css`:
  - Add styling rules for `.action-btn-delete` to format the form and delete button, ensuring it has no background or border, and turns red (`var(--danger)`) on hover.

## Files to create
- `tests/test_delete_expense.py`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values
- Deletion MUST be requested via a `POST` method. `GET` requests to the delete route should result in 405 Method Not Allowed to prevent crawlers or accidental browser prefetching from deleting user data.
- Unauthenticated attempts to delete must redirect to `/login`.
- If the expense does not exist or belongs to another user, redirect to `/profile` with a flash message.
- Currency must always display as ₹.

## Tests to write
File: `tests/test_delete_expense.py`

### Route tests
`POST /expenses/<id>/delete` — unauthenticated:
- Redirects to `/login` (302)

`POST /expenses/<id>/delete` — authenticated, own expense:
- Redirects to `/profile` (302)
- Database row is removed
- Success flash message is shown

`POST /expenses/<id>/delete` — authenticated, other user's expense:
- Redirects to `/profile` (302)
- Database row is NOT removed
- Error flash message is shown

`POST /expenses/<id>/delete` — authenticated, non-existent id:
- Redirects to `/profile` (302)
- Error flash message is shown

`GET /expenses/<id>/delete` — authenticated:
- Returns 405 Method Not Allowed

## Definition of done
- [ ] Attempting to POST to `/expenses/<id>/delete` while logged out redirects to `/login`
- [ ] Attempting to POST to `/expenses/<id>/delete` for a non-existent or other user's expense redirects to `/profile` with a flash error message
- [ ] Attempting to GET `/expenses/<id>/delete` returns a 405 Method Not Allowed status code
- [ ] Clicking the delete trash icon triggers a browser confirmation dialog
- [ ] Canceling the confirmation dialog keeps the expense intact and does not submit the form
- [ ] Confirming the deletion removes the expense from the database and redirects to `/profile`
- [ ] A success flash message appears on `/profile` after successful deletion
- [ ] Deleted expenses no longer appear in the recent transactions table
- [ ] The user's total expenses count and total amount spent are correctly updated on the profile page after deletion
