import os
import sqlite3

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'database', 'expense_tracker.db'))

def check_database():
    print(f"Checking database at: {DATABASE_PATH}")
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database file does not exist. Run the Flask application to initialize and seed it.")
        return

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall() if not row['name'].startswith('sqlite_')]
        print(f"Found tables: {', '.join(tables)}")
        
        for table in ['users', 'expenses']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"📊 Table '{table}': {count} records found.")
            else:
                print(f"❌ Table '{table}' is missing!")
                
        conn.close()
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_database()
