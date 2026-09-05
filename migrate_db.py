# migrate_db.py - Alternative version

import sqlite3
import os

def migrate():
    db_path = os.path.join('instance', 'expenses.db')
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. Run your app first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(expense)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'receipt_file' not in columns:
        print("Adding receipt_file column...")
        cursor.execute("ALTER TABLE expense ADD COLUMN receipt_file VARCHAR(200)")
        conn.commit()
        print("✅ receipt_file column added successfully!")
    else:
        print("✅ receipt_file column already exists. Nothing to do.")
    
    conn.close()

if __name__ == '__main__':
    migrate()