"""
Migration: Add display_mode column to content table

This adds the display_mode column to control how content is displayed:
- 'fit': Scale to fit (letterbox/pillarbox with black bars, no cropping)
- 'fill': Scale to fill (crop content to fill screen, no stretching)

Default is 'fit' to preserve aspect ratio without cropping.
"""

import sqlite3
import sys
from pathlib import Path

# Get the database path
db_path = Path(__file__).parent.parent / 'signage.db'

def migrate():
    """Add display_mode column to content table"""
    # Check if database exists
    if not db_path.exists():
        print("✓ Database doesn't exist yet - no migration needed")
        print("  The display_mode column will be created when the database is initialized")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if content table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content'")
        if not cursor.fetchone():
            print("✓ Content table doesn't exist yet - no migration needed")
            print("  The display_mode column will be created when the database is initialized")
            return

        # Check if column already exists
        cursor.execute("PRAGMA table_info(content)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'display_mode' in columns:
            print("✓ display_mode column already exists")
            return

        # Add the column with default value
        cursor.execute("""
            ALTER TABLE content
            ADD COLUMN display_mode VARCHAR(20) DEFAULT 'fit'
        """)

        conn.commit()
        print("✓ Successfully added display_mode column to content table")
        print("  - Default value: 'fit' (scale to fit, no cropping)")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error during migration: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    print("Running migration: Add display_mode column")
    migrate()
