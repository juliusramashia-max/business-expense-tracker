# app.py - Complete Business Expense Tracker with Receipt Uploads

from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ============================================
# DATABASE SETUP
# ============================================

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'expenses.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ============================================
# FILE UPLOAD CONFIGURATION
# ============================================

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# ============================================
# FILE UPLOAD HELPER FUNCTIONS
# ============================================

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# DATABASE MODEL
# ============================================

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    person = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    approval_notes = db.Column(db.String(200), nullable=True)
    receipt_file = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.id}: {self.person} - R{self.amount}>'

# ============================================
# ROUTES
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
    
    # Handle file upload
    receipt_file = None
    if 'receipt' in request.files:
        file = request.files['receipt']
        if file and file.filename != '' and allowed_file(file.filename):
            # Secure the filename
            filename = secure_filename(file.filename)
            # Add timestamp to make it unique
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            # Save the file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            receipt_file = unique_filename
    
    # Validation: require either receipt or approval notes
    if not receipt_file and not approval_notes:
        flash('Please either upload a receipt or add notes for your manager.', 'error')
        return redirect(url_for('add_expense'))
    
    new_expense = Expense(
        date=date,
        person=person,
        amount=float(amount),
        category=category,
        description=description,
        approval_notes=approval_notes,
        receipt_file=receipt_file
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
                        <th>Receipt</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for expense in filtered_expenses:
            receipt_html = '-'
            if expense.receipt_file:
                receipt_html = f'<a href="/uploads/{expense.receipt_file}" target="_blank">📄 View</a>'
            
            html += f"""
                <tr>
                    <td>{expense.id}</td>
                    <td>{expense.date}</td>
                    <td>{expense.person}</td>
                    <td>R{expense.amount:.2f}</td>
                    <td>{expense.category}</td>
                    <td>{expense.description or '-'}</td>
                    <td>{expense.approval_notes or '-'}</td>
                    <td>{receipt_html}</td>
                    <td>
                        <a href="/edit/{expense.id}" class="btn btn-primary" style="padding: 5px 10px; font-size: 12px; text-decoration: none; color: white; background: #3498db; border-radius: 4px;">✏️ Edit</a>
                        <button onclick="confirmDelete({expense.id})" class="btn btn-danger" style="padding: 5px 10px; font-size: 12px; color: white; background: #e74c3c; border: none; border-radius: 4px; cursor: pointer;">🗑️ Delete</button>
                    </td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
            
            <script>
                function confirmDelete(expenseId) {
                    if (confirm('Are you sure you want to delete this expense? This action cannot be undone!')) {
                        var form = document.createElement('form');
                        form.method = 'POST';
                        form.action = '/delete/' + expenseId;
                        document.body.appendChild(form);
                        form.submit();
                    }
                }
            </script>
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
# EDIT EXPENSE
# ============================================

def render_edit_form(expense):
    """Helper function to render the edit form"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Expense</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>✏️ Edit Expense #{expense_id}</h1>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/expenses">📊 View All Expenses</a>
            </div>
            
            <form action="/edit/{expense_id}" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="date">📅 Date:</label>
                    <input type="date" id="date" name="date" value="{date}" required>
                </div>
                
                <div class="form-group">
                    <label for="person">👤 Employee Name:</label>
                    <input type="text" id="person" name="person" value="{person}" required>
                </div>
                
                <div class="form-group">
                    <label for="amount">💰 Amount (in R):</label>
                    <input type="number" id="amount" name="amount" step="0.01" value="{amount}" required>
                </div>
                
                <div class="form-group">
                    <label for="category">📂 Category:</label>
                    <select id="category" name="category" required>
                        <option value="Food" {food_selected}>🍔 Food</option>
                        <option value="Transport" {transport_selected}>🚗 Transport</option>
                        <option value="Office Supplies" {office_selected}>📎 Office Supplies</option>
                        <option value="Software" {software_selected}>💻 Software</option>
                        <option value="Other" {other_selected}>📦 Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="description">📝 Description:</label>
                    <textarea id="description" name="description" rows="3">{description}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="approval_notes">📋 Notes for Manager:</label>
                    <textarea id="approval_notes" name="approval_notes" rows="2">{approval_notes}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="receipt">📎 Receipt File:</label>
                    <input type="file" id="receipt" name="receipt" accept=".pdf,.png,.jpg,.jpeg,.gif,.doc,.docx">
    """
    
    if expense.receipt_file:
        html += f"""
                    <div style="margin-top: 5px; color: #28a745;">
                        📄 Current file: {expense.receipt_file}
                        <a href="/delete_receipt/{expense.id}" style="color: #dc3545; margin-left: 10px;" onclick="return confirm('Delete this receipt?')">🗑️ Remove</a>
                    </div>
        """
    
    html += """
                </div>
                
                <div class="form-group">
                    <button type="submit" class="btn btn-success">💾 Update Expense</button>
                    <a href="/expenses" class="btn btn-secondary">❌ Cancel</a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """.format(
        expense_id=expense.id,
        date=expense.date,
        person=expense.person,
        amount=expense.amount,
        description=expense.description or '',
        approval_notes=expense.approval_notes or '',
        food_selected='selected' if expense.category == 'Food' else '',
        transport_selected='selected' if expense.category == 'Transport' else '',
        office_selected='selected' if expense.category == 'Office Supplies' else '',
        software_selected='selected' if expense.category == 'Software' else '',
        other_selected='selected' if expense.category == 'Other' else ''
    )
    
    return html

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    if request.method == 'POST':
        # Update fields
        expense.date = request.form.get('date')
        expense.person = request.form.get('person')
        expense.amount = float(request.form.get('amount'))
        expense.category = request.form.get('category')
        expense.description = request.form.get('description')
        expense.approval_notes = request.form.get('approval_notes')
        
        # Handle file upload
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename != '' and allowed_file(file.filename):
                # Delete old file if it exists
                if expense.receipt_file:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], expense.receipt_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new file
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                expense.receipt_file = unique_filename
        
        # Validation: require either receipt or approval notes
        if not expense.receipt_file and not expense.approval_notes:
            flash('Please either upload a receipt or add notes for your manager.', 'error')
            return render_edit_form(expense)
        
        db.session.commit()
        
        flash(f'Expense #{expense.id} updated successfully!', 'success')
        return redirect(url_for('view_expenses'))
    
    return render_edit_form(expense)

# ============================================
# DELETE EXPENSE
# ============================================

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    # Delete the receipt file if it exists
    if expense.receipt_file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], expense.receipt_file)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    expense_info = f"{expense.person} - R{expense.amount} ({expense.category})"
    
    db.session.delete(expense)
    db.session.commit()
    
    flash(f'Expense #{expense_id} ({expense_info}) deleted successfully!', 'success')
    return redirect(url_for('view_expenses'))

# ============================================
# DELETE RECEIPT
# ============================================

@app.route('/delete_receipt/<int:expense_id>')
def delete_receipt(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    
    if expense.receipt_file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], expense.receipt_file)
        if os.path.exists(filepath):
            os.remove(filepath)
        expense.receipt_file = None
        db.session.commit()
        flash('Receipt removed successfully!', 'success')
    
    return redirect(url_for('edit_expense', expense_id=expense_id))

# ============================================
# SERVE UPLOADED FILES
# ============================================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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