# app.py - Updated for PythonAnywhere deployment

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import os  # NEW: For environment variables

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to something unique!

# ============================================
# DATABASE SETUP - Updated for PythonAnywhere
# ============================================

# Use absolute path for database on PythonAnywhere
# This works both locally and on PythonAnywhere
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'expenses.db')

# Ensure the instance directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================
# DATABASE TABLE (unchanged)
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
# ROUTES (unchanged from your working version)
# ============================================

@app.route('/')
def home():
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
    
    return redirect(url_for('add_expense'))

@app.route('/expenses')
def view_expenses():
    search_person = request.args.get('person', '')
    search_category = request.args.get('category', '')
    search_date_from = request.args.get('date_from', '')
    search_date_to = request.args.get('date_to', '')
    
    query = Expense.query
    
    if search_person:
        query = query.filter(Expense.person == search_person)
    
    if search_category:
        query = query.filter(Expense.category == search_category)
    
    if search_date_from:
        query = query.filter(Expense.date >= search_date_from)
    
    if search_date_to:
        query = query.filter(Expense.date <= search_date_to)
    
    filtered_expenses = query.order_by(Expense.date.desc()).all()
    filtered_total = sum(expense.amount for expense in filtered_expenses)
    
    persons = db.session.query(Expense.person).distinct().all()
    person_list = sorted([p[0] for p in persons if p[0]])
    
    categories = db.session.query(Expense.category).distinct().all()
    category_list = sorted([cat[0] for cat in categories if cat[0]])
    
    category_totals = db.session.query(
        Expense.category, 
        func.sum(Expense.amount).label('total')
    ).group_by(Expense.category).all()
    
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
                <a href="/expenses">🔄 Clear Filters</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>🔍 Search & Filter Expenses</h3>
                <form action="/expenses" method="GET" style="background: none; padding: 0; margin: 0;">
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: end;">
                        
                        <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 150px;">
                            <label style="display: block; font-weight: 600; font-size: 14px; margin-bottom: 5px;">👤 Person</label>
                            <select name="person" style="width: 100%; padding: 8px 12px; border: 2px solid #dce1e8; border-radius: 5px;">
                                <option value="">All Persons</option>
    """
    
    for person in person_list:
        selected = 'selected' if person == search_person else ''
        html += f'<option value="{person}" {selected}>{person}</option>'
    
    html += """
                            </select>
                        </div>
                        
                        <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 150px;">
                            <label style="display: block; font-weight: 600; font-size: 14px; margin-bottom: 5px;">📂 Category</label>
                            <select name="category" style="width: 100%; padding: 8px 12px; border: 2px solid #dce1e8; border-radius: 5px;">
                                <option value="">All Categories</option>
    """
    
    for category in category_list:
        selected = 'selected' if category == search_category else ''
        html += f'<option value="{category}" {selected}>{category}</option>'
    
    html += """
                            </select>
                        </div>
                        
                        <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 130px;">
                            <label style="display: block; font-weight: 600; font-size: 14px; margin-bottom: 5px;">📅 From</label>
                            <input type="date" name="date_from" value="""" + search_date_from + """" style="width: 100%; padding: 8px 12px; border: 2px solid #dce1e8; border-radius: 5px;">
                        </div>
                        
                        <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 130px;">
                            <label style="display: block; font-weight: 600; font-size: 14px; margin-bottom: 5px;">📅 To</label>
                            <input type="date" name="date_to" value="""" + search_date_to + """" style="width: 100%; padding: 8px 12px; border: 2px solid #dce1e8; border-radius: 5px;">
                        </div>
                        
                        <div style="display: flex; gap: 10px; align-items: center; padding-bottom: 2px;">
                            <button type="submit" class="btn btn-primary">🔍 Search</button>
                            <a href="/expenses" class="btn btn-secondary">🔄 Clear All</a>
                        </div>
                    </div>
                </form>
            </div>
            
            <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-bottom: 10px;">📊 Spending by Category (All Time)</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 15px;">
    """
    
    for category, total in category_totals:
        html += f"""
            <div style="background: white; padding: 10px 15px; border-radius: 5px; border: 1px solid #dce1e8;">
                <span style="font-weight: 600;">{category}:</span>
                <span style="color: #2c3e50;">R{total:.2f}</span>
                <a href="/expenses?category={category}" style="margin-left: 10px; font-size: 12px;">🔍</a>
            </div>
        """
    
    html += """
                </div>
            </div>
            
            <p><strong>""" + str(len(filtered_expenses)) + """</strong> expenses found</p>
    """
    
    if filtered_expenses:
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
        
        for expense in filtered_expenses:
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
            <div class="total-box" style="background: #27ae60;">
                💰 Total for Filtered Results: R{filtered_total:.2f}
            </div>
        """
    else:
        html += """
            <div class="flash-message info">
                📭 No expenses found matching your filters. <a href="/expenses">Clear filters</a> to see all expenses.
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