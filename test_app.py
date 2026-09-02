# test_app.py - Updated with fixes

import pytest
from app import app, db, Expense

def test_home_page():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Business Expense Tracker" in response.data
    assert b"Add a New Expense" in response.data
    assert b"View All Expenses" in response.data

def test_add_expense_page():
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

def test_submit_expense_with_all_fields():
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-02',
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
        'date': '2026-09-02',
        'person': 'DB Test User',
        'amount': '99.99',
        'category': 'Other',  # Use existing category
        'description': 'Test expense',
        'approval_notes': 'Testing database'
    }, follow_redirects=True)
    
    # Check page loaded
    assert response.status_code == 200
    assert b"Add a New Business Expense" in response.data
    
    # Verify database saved it
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
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-02',
        'person': 'Jane Smith',
        'amount': '89.00',
        'category': 'Transport',
        'description': 'Taxi to meeting'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense of R89.00 by Jane Smith for Transport saved successfully!" in response.data

def test_view_expenses_page():
    client = app.test_client()
    response = client.get('/expenses')
    assert response.status_code == 200
    assert b"All Expenses" in response.data
    assert b"Total Spent" in response.data
    assert b"style.css" in response.data

def test_redirect_after_submit():
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-02',
        'person': 'Bob Johnson',
        'amount': '25.00',
        'category': 'Office Supplies',
        'description': 'Pens and paper'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Add a New Business Expense" in response.data

def test_submit_redirect_check_status_code():
    client = app.test_client()
    response = client.post('/submit_expense', data={
        'date': '2026-09-02',
        'person': 'Alice Lee',
        'amount': '75.50',
        'category': 'Software',
        'description': 'Monthly software subscription'
    })
    assert response.status_code == 302
    assert 'Location' in response.headers
    assert response.headers['Location'] == '/add'

def test_css_file_exists():
    client = app.test_client()
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert b'font-family' in response.data or b'background-color' in response.data

def test_delete_all_test_expenses():
    """Clean up test data after all tests"""
    with app.app_context():
        # Delete all test expenses (using person names we used in tests)
        test_persons = ['DB Test User', 'John Test', 'Test User']
        for person in test_persons:
            test_expenses = Expense.query.filter_by(person=person).all()
            for expense in test_expenses:
                db.session.delete(expense)
        db.session.commit()