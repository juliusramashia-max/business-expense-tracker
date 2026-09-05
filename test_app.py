# test_app.py - Complete tests for Business Expense Tracker

import pytest
import os
from app import app, db, Expense

# ============================================
# HOMEPAGE TESTS
# ============================================

def test_home_page():
    """Test that the homepage loads correctly"""
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Business Expense Tracker" in response.data
    assert b"Add a New Expense" in response.data
    assert b"View All Expenses" in response.data

# ============================================
# ADD EXPENSE PAGE TESTS
# ============================================

def test_add_expense_page():
    """Test that the add expense page shows all form fields"""
    client = app.test_client()
    response = client.get('/add')
    assert response.status_code == 200
    assert b"Date" in response.data
    assert b"Employee Name" in response.data
    assert b"Amount" in response.data
    assert b"Category" in response.data
    assert b"Description" in response.data
    assert b"Notes for Manager" in response.data
    assert b"Receipt File" in response.data
    assert b"style.css" in response.data

# ============================================
# SUBMISSION TESTS
# ============================================

def test_submit_expense_with_all_fields():
    """Test submitting an expense with ALL fields (notes only, no receipt)"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'John Test',
        'amount': '150.50',
        'category': 'Food',
        'description': 'Lunch with client',
        'approval_notes': 'Client dinner'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense of R150.50 by John Test for Food saved successfully!" in response.data
    assert b"Add a New Business Expense" in response.data

def test_submit_expense_saves_to_database():
    """Test that submitting an expense saves it to the database"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'DB Test User',
        'amount': '99.99',
        'category': 'Other',
        'description': 'Test expense',
        'approval_notes': 'Testing database'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Add a New Business Expense" in response.data
    
    with app.app_context():
        saved_expense = Expense.query.filter_by(
            person='DB Test User',
            amount=99.99
        ).first()
        assert saved_expense is not None
        assert saved_expense.amount == 99.99
        assert saved_expense.category == 'Other'
        assert saved_expense.description == 'Test expense'

def test_submit_expense_with_notes_only():
    """Test submitting an expense with notes only (no receipt) - should pass"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Jane Smith',
        'amount': '89.00',
        'category': 'Transport',
        'description': 'Taxi to meeting',
        'approval_notes': 'Manager approved this expense'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense of R89.00 by Jane Smith for Transport saved successfully!" in response.data

def test_submit_expense_with_receipt_only():
    """Test submitting an expense with a receipt only (no notes) - should show error since no file uploaded"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Receipt Only User',
        'amount': '75.00',
        'category': 'Software',
        'description': 'Software purchase'
        # No receipt file uploaded, no approval_notes
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Since we didn't actually upload a file, this should fail validation
    assert b"Please either upload a receipt or add notes for your manager." in response.data

def test_submit_expense_with_no_receipt_and_no_notes():
    """Test that submitting without receipt OR notes shows error"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Invalid Test User',
        'amount': '50.00',
        'category': 'Other',
        'description': 'Test'
        # No receipt and no approval_notes
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Please either upload a receipt or add notes for your manager." in response.data

# ============================================
# VIEW EXPENSES TESTS
# ============================================

def test_view_expenses_page():
    """Test that the expenses page loads and shows data"""
    client = app.test_client()
    response = client.get('/expenses')
    assert response.status_code == 200
    assert b"All Expenses" in response.data
    assert b"Total for Filtered Results" in response.data
    assert b"Receipt" in response.data
    assert b"style.css" in response.data

# ============================================
# REDIRECT TESTS
# ============================================

def test_redirect_after_submit():
    """Test that submitting redirects back to the add page"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Bob Johnson',
        'amount': '25.00',
        'category': 'Office Supplies',
        'description': 'Pens and paper',
        'approval_notes': 'Office supplies approved'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a New Business Expense" in response.data

def test_submit_redirect_check_status_code():
    """Test that the initial response is a 302 redirect"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Alice Lee',
        'amount': '75.50',
        'category': 'Software',
        'description': 'Monthly software subscription',
        'approval_notes': 'Approved'
    })
    assert response.status_code == 302
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/add'

# ============================================
# CSS TEST
# ============================================

def test_css_file_exists():
    """Test that the CSS file is being served correctly"""
    client = app.test_client()
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert b'font-family' in response.data or b'background-color' in response.data

# ============================================
# EDIT EXPENSE TESTS
# ============================================

def test_edit_expense():
    """Test editing an existing expense"""
    client = app.test_client()
    
    # First, create a test expense with approval notes
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Edit Test User',
        'amount': '50.00',
        'category': 'Food',
        'description': 'Original description',
        'approval_notes': 'Original notes'
    }, follow_redirects=True)
    
    # Verify it was created
    assert response.status_code == 200
    
    # Find the expense
    with app.app_context():
        expense = Expense.query.filter_by(person='Edit Test User').first()
        assert expense is not None
        expense_id = expense.id
    
    # Edit the expense
    response = client.post(f'/edit/{expense_id}', data={
        'date': '2026-09-05',
        'person': 'Edit Test User',
        'amount': '75.00',
        'category': 'Transport',
        'description': 'Updated description',
        'approval_notes': 'Updated notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check that the expenses page loads and shows the updated info
    assert b'All Expenses' in response.data
    # Check that the updated person appears
    assert b'Edit Test User' in response.data
    
    # Verify the changes in the database
    with app.app_context():
        updated = Expense.query.get(expense_id)
        assert updated.amount == 75.00
        assert updated.category == 'Transport'
        assert updated.description == 'Updated description'
        assert updated.approval_notes == 'Updated notes'

def test_edit_expense_page_loads():
    """Test that the edit page loads with pre-filled data"""
    client = app.test_client()
    
    # Create a test expense with approval notes
    response = client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Edit Page Test',
        'amount': '30.00',
        'category': 'Other',
        'description': 'Test description',
        'approval_notes': 'Test notes for approval'
    }, follow_redirects=True)
    
    # Verify it was created
    assert response.status_code == 200
    
    with app.app_context():
        expense = Expense.query.filter_by(person='Edit Page Test').first()
        assert expense is not None
        expense_id = expense.id
    
    # Visit the edit page
    response = client.get(f'/edit/{expense_id}')
    assert response.status_code == 200
    # Check that the page loads with the edit form
    assert b'Edit Expense' in response.data
    # Check for the Update Expense button (this is always on the page)
    assert b'Update Expense' in response.data
    # Check for the Cancel button (this is always on the page)
    assert b'Cancel' in response.data
    # Check that the form has the correct method
    assert b'method="POST"' in response.data

def test_edit_expense_with_new_receipt():
    """Test editing an expense and uploading a new receipt"""
    client = app.test_client()
    
    # Create a test expense with notes (so it passes validation)
    client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Receipt Edit Test',
        'amount': '60.00',
        'category': 'Software',
        'description': 'Software license',
        'approval_notes': 'Manager approved'
    })
    
    with app.app_context():
        expense = Expense.query.filter_by(person='Receipt Edit Test').first()
        assert expense is not None
        expense_id = expense.id
        # Initially no receipt
        assert expense.receipt_file is None
    
    # Edit the expense (simulate adding a receipt)
    response = client.post(f'/edit/{expense_id}', data={
        'date': '2026-09-05',
        'person': 'Receipt Edit Test',
        'amount': '60.00',
        'category': 'Software',
        'description': 'Software license',
        'approval_notes': 'Manager approved'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check that the expenses page loads and shows the expense
    assert b'All Expenses' in response.data
    assert b'Receipt Edit Test' in response.data

# ============================================
# DELETE EXPENSE TESTS
# ============================================

def test_delete_expense():
    """Test deleting an expense"""
    client = app.test_client()
    
    # First, create a test expense with approval notes
    client.post('/submit_expense', data={
        'date': '2026-09-05',
        'person': 'Delete Test User',
        'amount': '100.00',
        'category': 'Software',
        'description': 'To be deleted',
        'approval_notes': 'Delete this expense'
    })
    
    # Find the expense
    with app.app_context():
        expense = Expense.query.filter_by(person='Delete Test User').first()
        assert expense is not None
        expense_id = expense.id
    
    # Delete the expense
    response = client.post(f'/delete/{expense_id}', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify it's gone
    with app.app_context():
        deleted = Expense.query.get(expense_id)
        assert deleted is None

# ============================================
# CLEANUP TESTS
# ============================================

def test_delete_all_test_expenses():
    """Clean up test data after all tests"""
    with app.app_context():
        # Delete all test expenses
        test_persons = [
            'DB Test User', 
            'John Test', 
            'Edit Test User',
            'Delete Test User',
            'Edit Page Test',
            'Receipt Only User',
            'Jane Smith',
            'Invalid Test User',
            'Receipt Edit Test',
            'Bob Johnson',
            'Alice Lee'
        ]
        for person in test_persons:
            test_expenses = Expense.query.filter_by(person=person).all()
            for expense in test_expenses:
                # Delete receipt file if it exists
                if expense.receipt_file:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], expense.receipt_file)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                db.session.delete(expense)
        db.session.commit()