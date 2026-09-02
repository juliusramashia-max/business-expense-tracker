# test_app.py - Clean version with fixed redirect test

import pytest
from app import app

def test_home_page():
    """Test that the homepage loads correctly"""
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Add a New Expense" in response.data

def test_add_expense_page():
    """Test that the add expense page shows all form fields"""
    client = app.test_client()
    response = client.get('/add')
    assert response.status_code == 200
    
    # Check that ALL form fields exist
    assert b"Date" in response.data
    assert b"Employee Name" in response.data
    assert b"Amount" in response.data
    assert b"Category" in response.data
    assert b"Description" in response.data
    assert b"Notes for Manager" in response.data

def test_submit_expense_with_all_fields():
    """Test submitting an expense with ALL fields"""
    client = app.test_client()
    
    response = client.post('/submit_expense', data={
        'date': '2026-09-01',
        'person': 'John Doe',
        'amount': '150.50',
        'category': 'Food',
        'description': 'Lunch with client',
        'approval_notes': 'Client dinner for ABC Corp project'
    }, follow_redirects=True)  # Better: Use follow_redirects
    
    assert response.status_code == 200
    assert b"Expense of R150.50 by John Doe for Food saved successfully!" in response.data
    assert b"Add a New Business Expense" in response.data

def test_submit_expense_without_optional_fields():
    """Test submitting an expense without optional fields (approval_notes is optional)"""
    client = app.test_client()
    
    response = client.post('/submit_expense', data={
        'date': '2026-09-01',
        'person': 'Jane Smith',
        'amount': '89.00',
        'category': 'Transport',
        'description': 'Taxi to meeting'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Expense of R89.00 by Jane Smith for Transport saved successfully!" in response.data

def test_submit_expense_missing_required_fields():
    """Test that submitting without required fields fails gracefully"""
    client = app.test_client()
    
    response = client.post('/submit_expense', data={
        'person': 'John Doe',
        'amount': '150.50',
        'category': 'Food'
        # date is intentionally missing
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should still show the add page
    assert b"Add a New Business Expense" in response.data

def test_redirect_after_submit():
    """Test that submitting redirects back to the add page using follow_redirects"""
    client = app.test_client()
    
    # Use follow_redirects=True to automatically handle the redirect
    response = client.post('/submit_expense', data={
        'date': '2026-09-01',
        'person': 'Bob Johnson',
        'amount': '25.00',
        'category': 'Office Supplies',
        'description': 'Pens and paper'  # Added this field
    }, follow_redirects=True)  # Auto-follows the redirect
    
    # After auto-following, status code should be 200
    assert response.status_code == 200
    
    # We should now be on the add page
    assert b"Add a New Business Expense" in response.data
    
    # And we should see the success message
    assert b"Expense of R25.00 by Bob Johnson for Office Supplies saved successfully!" in response.data

def test_submit_redirect_check_status_code():
    """Alternative test: Check that the initial response is a 302 redirect without following"""
    client = app.test_client()
    
    # Don't follow the redirect - just get the first response
    response = client.post('/submit_expense', data={
        'date': '2026-09-01',
        'person': 'Alice Lee',
        'amount': '75.50',
        'category': 'Software',
        'description': 'Monthly software subscription'
    })
    
    # Status code 302 = Redirect
    assert response.status_code == 302
    
    # Check that the Location header exists (tells us where to redirect)
    assert 'Location' in response.headers
    
    # The redirect should point to the add page
    assert response.headers['Location'] == '/add'
