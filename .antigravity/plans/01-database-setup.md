# Database Setup Implementation Plan

Implement the SQLite database initialization, schema creation, database context teardown, and seed data setup.

## User Review Required

No critical breaking changes. The SQLite database file will be stored locally inside the [database/](file:///home/nik/Desktop/expense-tracker/database) directory.

## Open Questions

None. The schema is inferred from the application requirements:
- `users` table: For user authentication, storing names, emails, and hashed passwords.
- `expenses` table: Stores logged expenses with fields for category, amount, date, and description, linked to a specific user.

## Proposed Changes

### Database Layer

#### [MODIFY] [db.py](file:///home/nik/Desktop/expense-tracker/database/db.py)
- Implement `get_db()` to return a SQLite connection with row factory and foreign keys enabled.
- Implement `init_db()` to create `users` and `expenses` tables.
- Implement `seed_db()` to seed mock users and expenses if the database is empty.
- Implement `close_db(e=None)` to close the database connection.

### Flask Application Entrypoint

#### [MODIFY] [app.py](file:///home/nik/Desktop/expense-tracker/app.py)
- Register `close_db` handler using Flask's `@app.teardown_appcontext`.
- Initialize and seed the database on startup if the database file does not exist.

## Verification Plan

### Automated Tests
- No automated test suites currently exist.

### Manual Verification
- Run the Flask server: `python app.py` (or `./venv/bin/python app.py`).
- Verify the SQLite database file `database/expense_tracker.db` is created.
- Verify that we can query the database file using SQLite to ensure the tables are created and seeded correctly:
  ```bash
  sqlite3 database/expense_tracker.db "SELECT * FROM users;"
  sqlite3 database/expense_tracker.db "SELECT * FROM expenses;"
  ```
