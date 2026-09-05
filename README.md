# 💰 Business Expense Tracker

A full-stack web application for recording, managing, and analysing business expenses. Built with Python, Flask, and SQLite.

🔗 **Live Demo:** [https://jaymoh.pythonanywhere.com](https://jaymoh.pythonanywhere.com)

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Routes](#api-routes)
- [Deployment](#deployment)
- [License](#license)
- [Author](#author)



## ✨ Features

### Core Features
- ➕ **Add Expenses** - Record date, person, amount, category, description, and notes
- 📊 **View All Expenses** - See all expenses in a sortable table
- 🔍 **Search & Filter** - Filter by person, category, or date range
- 💰 **Total Calculation** - Automatically calculates totals for filtered results
- 📂 **Category Summary** - View spending totals by category



### Advanced Features
- 📎 **Receipt Upload** - Upload supporting documents (PDF, PNG, JPG, etc.)
- ✅ **Validation** - Receipt OR manager notes required
- ✏️ **Edit Expenses** - Update any expense details
- 🗑️ **Delete Expenses** - Remove expenses with confirmation
- 📄 **Receipt Management** - View, delete, and replace receipts
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop



## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python 3.7+, Flask, Flask-SQLAlchemy |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Testing** | pytest |
| **Version Control** | Git, GitHub |
| **Deployment** | PythonAnywhere |




## 📸 Screenshots

### Homepage
![Homepage](screenshots/homepage.png)

### Add Expense Form
![Add Expense](screenshots/add_expense.png)

### Expenses Table with Receipts
![Expenses Table](screenshots/expenses_table.png)

### Edit Expense
![Edit Expense](screenshots/edit_expense.png)

> **Note:** Add screenshots to a `screenshots/` folder in your repository.

---

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment (recommended)


### Step 1: Clone the Repository

```bash
git clone https://github.com/juliusramashia-max/business-expense-tracker.git
cd business-expense-tracker

Step 2: Create a Virtual Environment
Windows
bash
python -m venv venv
venv\Scripts\activate
Mac/Linux
bash
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
bash
pip install flask flask-sqlalchemy pytest

Step 4: Set Up the Database
bash
# Create the database structure
python -c "from app import app, db; with app.app_context(): db.create_all(); print('Database created!')"

# Or run the app once to create it automatically
python app.py

Step 5: Run the App
bash
python app.py

Step 6: Open in Browser
Open your browser and go to: http://127.0.0.1:5000

🔧 Running the App
Development Mode
bash
python app.py
The app will run with debug=True, meaning:

Auto-restarts when code changes

Detailed error messages in the browser

Interactive debugger

Production Mode
On PythonAnywhere, the app runs automatically. No additional steps needed.

🧪 Running Tests
Run All Tests
bash
pytest test_app.py -v
Run Specific Test
bash
pytest test_app.py::test_home_page -v
Run Tests with Coverage
bash
pip install pytest-cov
pytest test_app.py -v --cov=app
Expected output:

text
test_home_page PASSED
test_add_expense_page PASSED
test_submit_expense_with_all_fields PASSED
test_submit_expense_saves_to_database PASSED
test_submit_expense_without_optional_fields PASSED
test_view_expenses_page PASSED
test_redirect_after_submit PASSED
test_submit_redirect_check_status_code PASSED
test_css_file_exists PASSED
test_edit_expense PASSED
test_edit_expense_page_loads PASSED
test_delete_expense PASSED
test_delete_all_test_expenses PASSED

13 passed in 1.23s


📁 Project Structure
text
business-expense-tracker/
├── app.py                 # Main Flask application
├── test_app.py            # Test suite (pytest)
├── view_db.py             # Helper script to view database contents
├── create_db.py           # Helper script to create database
├── migrate_db.py          # Database migration script
├── clear_data.py          # Script to delete test data
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignored files
├── README.md              # Project documentation
├── instance/              # Database files (not in Git)
│   └── expenses.db        # SQLite database
├── uploads/               # Uploaded receipt files (not in Git)
├── static/                # Static assets
│   └── style.css          # CSS styles
└── templates/             # HTML templates
    ├── home.html          # Homepage
    ├── add_expense.html   # Add expense form
    └── edit.html          # Edit expense form (rendered in app.py)


🗄️ Database Schema

Expense Table
Column	Type	Description
id	INTEGER	Primary key (auto-increment)
date	VARCHAR(20)	Date of expense
person	VARCHAR(100)	Person who incurred the expense
amount	FLOAT	Expense amount in Rands
category	VARCHAR(50)	Expense category (Food, Transport, etc.)
description	VARCHAR(200)	Optional description
approval_notes	VARCHAR(200)	Optional notes for manager
receipt_file	VARCHAR(200)	Filename of uploaded receipt
created_at	DATETIME	Timestamp when record was created

🔗 API Routes
Route	Method	Description
/	GET	Homepage
/add	GET	Add expense form
/submit_expense	POST	Submit new expense
/expenses	GET	View all expenses (supports filters)
/edit/<id>	GET	Edit expense form
/edit/<id>	POST	Update expense
/delete/<id>	POST	Delete expense
/delete_receipt/<id>	GET	Delete receipt file
/uploads/<filename>	GET	View uploaded receipt

Filter Parameters (for /expenses)
Parameter	Example	Description
person	?person=John	Filter by person
category	?category=Food	Filter by category
date_from	?date_from=2026-09-01	Start date
date_to	?date_to=2026-09-30	End date

🌐 Deployment
Deploy to PythonAnywhere
Push code to GitHub:

bash
git push
SSH into PythonAnywhere:

bash
cd /home/Jaymoh
git clone https://github.com/juliusramashia-max/business-expense-tracker.git
cd business-expense-tracker

Install dependencies:

bash
pip install --user flask flask-sqlalchemy
Set up the database:

bash
python3 -c "from app import app, db; with app.app_context(): db.create_all(); print('Database created!')"

Configure the web app:

Source code: https://www.pythonanywhere.com/user/Jaymoh/files/home/Jaymoh/business-expense-tracker

Working directory: https://www.pythonanywhere.com/user/Jaymoh/files/home/Jaymoh/business-expense-tracker

Reload the web app

Access your app: https://jaymoh.pythonanywhere.com/

📦 Requirements
Create a requirements.txt file:

txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
pytest==8.2.2
pytest-cov==5.0.0
Install with:

bash
pip install -r requirements.txt
🐛 Troubleshooting
Error: ModuleNotFoundError: No module named 'flask'
bash
pip install flask flask-sqlalchemy
Error: No module named 'app' on PythonAnywhere
Check your WSGI configuration and ensure the source code path is correct.

Error: table expense has no column named receipt_file
Run the migration script:

bash
python migrate_db.py
Error: The term 'git' is not recognized
Install Git from: https://git-scm.com/downloads

Error: sqlite3 command not found
Use Python's built-in SQLite support instead, or install DB Browser for SQLite.



🛡️ Security Notes
app.secret_key should be changed to a random string in production

The instance/ folder contains the database and should not be committed to Git

The uploads/ folder contains user files and should not be committed to Git

Always use secure_filename() when handling uploaded files



🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature-name

Make your changes

Run tests: pytest test_app.py -v

Commit: git commit -m "Description of changes"

Push: git push origin feature-name

Open a pull request


📄 License
This project is open source and available under the MIT License.


👨‍💻 Author
Julius Ramashia

GitHub: @juliusramashia-max

Live App: jaymoh.pythonanywhere.com


🙏 Acknowledgements
Flask Documentation

SQLAlchemy Documentation

PythonAnywhere

pytest Documentation


📊 Project Status
✅ Complete - All core features implemented and tested
✅ Deployed - Live on PythonAnywhere
✅ Production Ready - Full CRUD, search, filter, and receipt upload


🎯 Roadmap (Future Features)
□ User authentication (login/register)
□ Export expenses to CSV/Excel
□ Charts and analytics dashboard
□ Email notifications
□ Multi-currency support

Built with ❤️ by Julius Ramashia
