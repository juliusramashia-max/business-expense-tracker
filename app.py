# app.py - With Professional Styling

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ============================================
# DATABASE SETUP
# ============================================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================
# DATABASE TABLE
# ============================================

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    person = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    approval_notes = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.id}: {self.person} - R{self.amount}>'

# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    # CHANGED: Now uses the home.html template
    return render_template('home.html')

@app.route('/add')
def add_expense():
    return render_template('add_expense.html')

@app.route('/submit_expense', methods=['POST'])
def submit_expense():
    date = request.form.get('date')
    person = request.form.get('person')
    amount = request.form.get('amount')
    category = request.form.get('category')
    description = request.form.get('description')
    approval_notes = request.form.get('approval_notes')
    
    new_expense = Expense(
        date=date,
        person=person,
        amount=float(amount),
        category=category,
        description=description,
        approval_notes=approval_notes
    )
    
    db.session.add(new_expense)
    db.session.commit()
    
    flash(f'Expense of R{amount} by {person} for {category} saved successfully!', 'success')
    
    print(f"Saved to database: {date} | {person} | R{amount} | {category}")
    if approval_notes:
        print(f"  Notes for manager: {approval_notes}")
    
    return redirect(url_for('add_expense'))

@app.route('/expenses')
def view_expenses():
    all_expenses = Expense.query.order_by(Expense.date.desc()).all()
    total = sum(expense.amount for expense in all_expenses)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>All Expenses</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>📊 All Expenses</h1>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/add">➕ Add New Expense</a>
            </div>
    """
    
    if all_expenses:
        html += """
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Date</th>
                        <th>Person</th>
                        <th>Amount (R)</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for expense in all_expenses:
            html += f"""
                <tr>
                    <td>{expense.id}</td>
                    <td>{expense.date}</td>
                    <td>{expense.person}</td>
                    <td>R{expense.amount:.2f}</td>
                    <td>{expense.category}</td>
                    <td>{expense.description or '-'}</td>
                    <td>{expense.approval_notes or '-'}</td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
        
        html += f"""
            <div class="total-box">
                💰 Total Spent: R{total:.2f}
            </div>
        """
    else:
        html += """
            <div class="flash-message info">
                📭 No expenses found. <a href="/add">Add your first expense!</a>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# ============================================
# CREATE DATABASE TABLES
# ============================================

with app.app_context():
    db.create_all()

# ============================================
# RUN THE APP
# ============================================

if __name__ == '__main__':
    app.run(debug=True)