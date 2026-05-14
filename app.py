from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from database.database import LibraryDatabase
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
db = LibraryDatabase()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.get_user(session['user_id'])
        if user['user_type'] not in ['admin', 'librarian']:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        return f(*args, **kwargs)
    return decorated_function

# AUTHENTICATION ROUTES
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        result = db.add_user(
            user_type='student',
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            password=data['password'],
            student_id=data.get('student_id'),
            department=data.get('department')
        )
        return jsonify(result)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = db.authenticate_user(data['email'], data['password'])
        if user:
            session['user_id'] = user['user_id']
            session['user_type'] = user['user_type']
            session['name'] = f"{user['first_name']} {user['last_name']}"
            return jsonify({'status': 'success', 'message': 'Login successful'})
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# DASHBOARD ROUTES
@app.route('/dashboard')
@login_required
def dashboard():
    user = db.get_user(session['user_id'])
    if user['user_type'] in ['admin', 'librarian']:
        return render_template('admin_dashboard.html', user=user)
    return render_template('student_dashboard.html', user=user)

# BOOK ROUTES
@app.route('/api/books')
@login_required
def get_books():
    books = db.get_available_books()
    return jsonify(books)

@app.route('/api/books/search')
@login_required
def search_books():
    query = request.args.get('q')
    search_type = request.args.get('type', 'title')
    books = db.search_books(query, search_type)
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
@admin_required
def add_book():
    data = request.get_json()
    result = db.add_book(
        isbn=data.get('isbn'),
        title=data['title'],
        author=data['author'],
        publisher=data.get('publisher'),
        publication_year=data.get('publication_year'),
        category=data.get('category'),
        total_copies=data.get('total_copies', 1),
        description=data.get('description')
    )
    return jsonify(result)

@app.route('/books')
@login_required
def books():
    return render_template('books.html')

# ISSUE ROUTES
@app.route('/api/issues', methods=['POST'])
@login_required
def issue_book():
    data = request.get_json()
    result = db.issue_book(session['user_id'], data['book_id'], data.get('days', 14))
    return jsonify(result)

@app.route('/api/issues/<int:issue_id>', methods=['POST'])
@login_required
def return_book(issue_id):
    result = db.return_book(issue_id)
    return jsonify(result)

@app.route('/api/my-books')
@login_required
def my_books():
    books = db.get_user_books(session['user_id'])
    return jsonify(books)

@app.route('/my-books')
@login_required
def view_my_books():
    return render_template('my_books.html')

# RESERVATION ROUTES
@app.route('/api/reservations', methods=['POST'])
@login_required
def reserve_book():
    data = request.get_json()
    result = db.reserve_book(session['user_id'], data['book_id'])
    return jsonify(result)

@app.route('/api/my-reservations')
@login_required
def my_reservations():
    reservations = db.get_user_reservations(session['user_id'])
    return jsonify(reservations)

@app.route('/reservations')
@login_required
def view_reservations():
    return render_template('reservations.html')

# FINE ROUTES
@app.route('/api/fines')
@login_required
def get_fines():
    fines = db.get_user_fines(session['user_id'])
    return jsonify(fines)

@app.route('/fines')
@login_required
def view_fines():
    return render_template('fines.html')

@app.route('/api/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
def pay_fine(fine_id):
    result = db.pay_fine(fine_id)
    return jsonify(result)

# ADMIN ROUTES
@app.route('/api/overdue-books')
@admin_required
def overdue_books():
    overdue = db.get_overdue_books()
    return jsonify(overdue)

@app.route('/admin/overdue')
@admin_required
def view_overdue():
    return render_template('admin/overdue.html')

@app.route('/api/feedback')
@admin_required
def get_feedback():
    feedback = db.get_feedback()
    return jsonify(feedback)

@app.route('/admin/feedback')
@admin_required
def view_feedback():
    return render_template('admin/feedback.html')

# FEEDBACK ROUTE
@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    result = db.add_feedback(session['user_id'], data['feedback_text'], data.get('rating'))
    return jsonify(result)

@app.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True)
