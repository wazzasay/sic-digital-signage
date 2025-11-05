"""
Diagnostic script to check database status
"""

import sqlite3
from pathlib import Path

# Get the database path
db_path = Path(__file__).parent.parent / 'signage.db'

print(f"Checking database at: {db_path}")
print(f"Database exists: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")

    # Check content table structure
    if any(t[0] == 'content' for t in tables):
        cursor.execute("PRAGMA table_info(content)")
        columns = cursor.fetchall()
        print("\nContent table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("\nContent table not found!")

    conn.close()
else:
    print("\nDatabase file not found!")
