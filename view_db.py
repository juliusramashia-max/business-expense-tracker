# view_db.py - Simple script to view your database

import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/expenses.db')
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Show all expenses
print("\nAll expenses:")
cursor.execute("SELECT * FROM expense;")
expenses = cursor.fetchall()

if expenses:
    for expense in expenses:
        print(expense)
else:
    print("  No expenses yet!")

# Show column names
print("\nColumn names:")
cursor.execute("PRAGMA table_info(expense);")
columns = cursor.fetchall()
for column in columns:
    print(f"  - {column[1]} ({column[2]})")

# Close connection
conn.close()
