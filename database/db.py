# Students will write this file in Step 1 — Database Setup
# This file should contain:
#   get_db()   — returns a SQLite connection with row_factory and foreign keys enabled
#   init_db()  — creates all tables using CREATE TABLE IF NOT EXISTS
#   seed_db()  — inserts sample data for development

import sqlite3
import os
from flask import g
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(__file__), 'expense_tracker.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
        g._database = db
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    
    # Create expenses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')
    db.commit()

def seed_db():
    db = get_db()
    
    # Check if we already have users
    cursor = db.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Insert a test user
        hashed_password = generate_password_hash("password123")
        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            ("Nitish Kumar", "nitish@example.com", hashed_password)
        )
        db.commit()
        
        # Get the user ID
        user_row = db.execute("SELECT id FROM users WHERE email = ?", ("nitish@example.com",)).fetchone()
        user_id = user_row['id']
        
        # Insert some sample expenses
        expenses_to_seed = [
            (user_id, "Food", 250.0, "2026-06-09", "Dinner at restaurant"),
            (user_id, "Travel", 150.0, "2026-06-10", "Auto ride"),
            (user_id, "Bills", 1200.0, "2026-06-08", "Internet subscription"),
            (user_id, "Food", 80.0, "2026-06-10", "Tea and snacks")
        ]
        db.executemany(
            "INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses_to_seed
        )
        db.commit()
