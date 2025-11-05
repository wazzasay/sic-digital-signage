#!/usr/bin/env python3
"""
Database migration script to add duration_override column to playlist_items table
Run this script to update your database schema
"""

import os
from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='playlist_items'
                AND column_name='duration_override'
            """))

            if result.fetchone():
                print("✓ Column 'duration_override' already exists in playlist_items table")
                return

            # Add the duration_override column
            print("Adding duration_override column to playlist_items table...")
            db.session.execute(text("""
                ALTER TABLE playlist_items
                ADD COLUMN duration_override INTEGER
            """))
            db.session.commit()

            print("✓ Successfully added duration_override column!")
            print("✓ Migration complete!")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add duration_override to playlist_items")
    print("=" * 60)
    migrate()
