# app.py - Complete version with server start code

from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def home():
    return """
    <h1>Welcome to my Business Expense Tracker!</h1>
    <p><a href='/add'>Add a New Expense</a></p>
    <p><a href='/expenses'>View All Expenses</a></p>  <!-- We'll add this later -->
    """

@app.route('/add')
def add_expense():
    return render_template('add_expense.html')

@app.route('/submit_expense', methods=['POST'])
def submit_expense():
    # Get ALL the form data including the new 'person' field
    date = request.form.get('date')
    person = request.form.get('person')
    amount = request.form.get('amount')
    category = request.form.get('category')
    description = request.form.get('description')
    approval_notes = request.form.get('approval_notes')
    
    # Show success message including who spent it
    flash(f'Expense of R{amount} by {person} for {category} saved successfully!', 'success')
    
    # Print to terminal so you can see it working
    print(f"Saved: {date} | {person} | R{amount} | {category} | {description}")
    if approval_notes:
        print(f"  Notes for manager: {approval_notes}")
    
    return redirect(url_for('add_expense'))

# ============================================
# THE MISSING PART - This starts the server!
# ============================================
if __name__ == '__main__':
    app.run(debug=True)