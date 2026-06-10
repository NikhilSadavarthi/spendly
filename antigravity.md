# Antigravity Guidelines - Expense Tracker

This file provides context, commands, and rules for the Antigravity agent when working on this Flask-based Expense Tracker application.

## Tech Stack & Environment
- **Web Framework:** Flask (v3.1.3)
- **Database:** SQLite
- **Testing:** Pytest & pytest-flask
- **Python Version:** 3.10+ (using a local virtual environment in `./venv`)

## Core Development Commands

### Running the Application
- Run the Flask development server:
  ```bash
  python app.py
  # or using the virtual environment python:
  ./venv/bin/python app.py
  ```
- The application runs on port `5001` with debug mode enabled.

### Testing
- Run all test suites (once implemented):
  ```bash
  pytest
  # or using the virtual environment pytest:
  ./venv/bin/pytest
  ```

## Project Structure
- [app.py](file:///home/nik/Desktop/expense-tracker/app.py): Main application entrypoint containing route handlers.
- [database/db.py](file:///home/nik/Desktop/expense-tracker/database/db.py): Database setup and management functions.
- `templates/`: HTML templates for UI pages.
- `static/`: CSS and client-side JavaScript assets.

## Code Style & Rules
- **Preserve Instructions:** Do not remove comments marked with `Students will write this...` or similar instructions unless explicitly requested by the user.
- **SQLite Database:**
  - Always implement `get_db()` to return a SQLite connection with row factory (`sqlite3.Row`) and foreign keys enabled (`PRAGMA foreign_keys = ON;`).
  - Always clean up database connections using Flask's `@app.teardown_appcontext`.
- **HTML/CSS UI:**
  - Keep styling modern, responsive, and clean using standard vanilla CSS in static assets.
  - Follow accessible and semantic HTML tags.
