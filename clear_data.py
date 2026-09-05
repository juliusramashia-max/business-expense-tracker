# clear_data.py - Delete all expenses but keep the database structure

from app import app, db, Expense

print("Deleting all expenses...")

with app.app_context():
    count = Expense.query.count()
    db.session.query(Expense).delete()
    db.session.commit()
    print(f"✅ Deleted {count} expenses!")
    print("✅ Database structure remains intact.")