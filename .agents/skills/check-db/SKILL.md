---
name: check-db
description: Checks the SQLite database state, including table existence and record counts.
---

# Check DB Skill

Use this skill to inspect the state of the local SQLite database.

## When to use this
- The user asks about the state of the database or database setup.
- You need to verify if the database has been initialized or seeded.

## Instructions
1. Run the database checker script using the project's virtual environment:
   ```bash
   ./venv/bin/python .agents/skills/check-db/scripts/db_checker.py
   ```
2. Report the results to the user.
3. If the database file does not exist, explain how to run the app to initialize/seed it.
