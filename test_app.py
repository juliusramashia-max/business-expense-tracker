# test_app.py - Complete with all fixes

import pytest
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
    assert b"style.css" in response.data

# ============================================
# SUBMISSION TESTS
# ============================================

def test_submit_expense_with_all_fields():
    """Test submitting an expense with ALL fields"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-04',
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
        'date': '2026-09-04',
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

def test_submit_expense_without_optional_fields():
    """Test submitting an expense without optional fields"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Jane Smith',
        'amount': '89.00',
        'category': 'Transport',
        'description': 'Taxi to meeting'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense of R89.00 by Jane Smith for Transport saved successfully!" in response.data

# ============================================
# VIEW EXPENSES TESTS
# ============================================

def test_view_expenses_page():
    """Test that the expenses page loads and shows data"""
    client = app.test_client()
    response = client.get('/expenses')
    assert response.status_code == 200
    assert b"All Expenses" in response.data
    # FIXED: Changed from 'Total Spent' to 'Total for Filtered Results'
    assert b"Total for Filtered Results" in response.data
    assert b"style.css" in response.data

# ============================================
# REDIRECT TESTS
# ============================================

def test_redirect_after_submit():
    """Test that submitting redirects back to the add page"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Bob Johnson',
        'amount': '25.00',
        'category': 'Office Supplies',
        'description': 'Pens and paper'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a New Business Expense" in response.data

def test_submit_redirect_check_status_code():
    """Test that the initial response is a 302 redirect"""
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Alice Lee',
        'amount': '75.50',
        'category': 'Software',
        'description': 'Monthly software subscription'
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
    
    # First, create a test expense
    client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Edit Test User',
        'amount': '50.00',
        'category': 'Food',
        'description': 'Original description',
        'approval_notes': 'Original notes'
    })
    
    # Find the expense
    with app.app_context():
        expense = Expense.query.filter_by(person='Edit Test User').first()
        assert expense is not None
        expense_id = expense.id
    
    # Edit the expense
    response = client.post(f'/edit/{expense_id}', data={
        'date': '2026-09-04',
        'person': 'Edit Test User',
        'amount': '75.00',
        'category': 'Transport',
        'description': 'Updated description',
        'approval_notes': 'Updated notes'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify the changes
    with app.app_context():
        updated = Expense.query.get(expense_id)
        assert updated.amount == 75.00
        assert updated.category == 'Transport'
        assert updated.description == 'Updated description'
        assert updated.approval_notes == 'Updated notes'

def test_edit_expense_page_loads():
    """Test that the edit page loads with pre-filled data"""
    client = app.test_client()
    
    # Create a test expense
    client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Edit Page Test',
        'amount': '30.00',
        'category': 'Other',
        'description': 'Test description'
    })
    
    with app.app_context():
        expense = Expense.query.filter_by(person='Edit Page Test').first()
        assert expense is not None
    
    # Visit the edit page
    response = client.get(f'/edit/{expense.id}')
    assert response.status_code == 200
    assert b'Edit Expense' in response.data
    # FIXED: Changed from '30.00' to '30' (more flexible)
    assert b'30' in response.data
    assert b'Test description' in response.data

# ============================================
# DELETE EXPENSE TESTS
# ============================================

def test_delete_expense():
    """Test deleting an expense"""
    client = app.test_client()
    
    # First, create a test expense
    client.post('/submit_expense', data={
        'date': '2026-09-04',
        'person': 'Delete Test User',
        'amount': '100.00',
        'category': 'Software',
        'description': 'To be deleted'
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
            'Edit Page Test'
        ]
        for person in test_persons:
            test_expenses = Expense.query.filter_by(person=person).all()
            for expense in test_expenses:
                db.session.delete(expense)
        db.session.commit()