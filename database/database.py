import sqlite3
import os
from datetime import datetime, timedelta
import hashlib

class LibraryDatabase:
    def __init__(self, db_path='library_system.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with schema"""
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            with open('database/schema.sql', 'r') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
            
            conn.commit()
            conn.close()
            print(f"Database initialized at {self.db_path}")
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # USER MANAGEMENT
    def add_user(self, user_type, first_name, last_name, email, phone, password, student_id=None, department=None):
        """Add new user to the system"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_type, first_name, last_name, email, phone, password_hash, student_id, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_type, first_name, last_name, email, phone, self.hash_password(password), student_id, department))
            
            conn.commit()
            user_id = cursor.lastrowid
            return {'status': 'success', 'user_id': user_id, 'message': 'User added successfully'}
        except sqlite3.IntegrityError:
            return {'status': 'error', 'message': 'Email already exists'}
        finally:
            conn.close()
    
    def get_user(self, user_id):
        """Get user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', 
                      (email, self.hash_password(password)))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    # BOOK MANAGEMENT
    def add_book(self, isbn, title, author, publisher, publication_year, category, total_copies, description=None):
        """Add new book to library"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO books (isbn, title, author, publisher, publication_year, category, total_copies, available_copies, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (isbn, title, author, publisher, publication_year, category, total_copies, total_copies, description))
            
            conn.commit()
            book_id = cursor.lastrowid
            return {'status': 'success', 'book_id': book_id, 'message': 'Book added successfully'}
        except sqlite3.IntegrityError:
            return {'status': 'error', 'message': 'ISBN already exists'}
        finally:
            conn.close()
    
    def get_book(self, book_id):
        """Get book details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        book = cursor.fetchone()
        conn.close()
        
        return dict(book) if book else None
    
    def search_books(self, query, search_type='title'):
        """Search books by title, author, or category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if search_type == 'title':
            cursor.execute('SELECT * FROM books WHERE title LIKE ? AND available_copies > 0', (f'%{query}%',))
        elif search_type == 'author':
            cursor.execute('SELECT * FROM books WHERE author LIKE ? AND available_copies > 0', (f'%{query}%',))
        elif search_type == 'category':
            cursor.execute('SELECT * FROM books WHERE category LIKE ? AND available_copies > 0', (f'%{query}%',))
        
        books = cursor.fetchall()
        conn.close()
        
        return [dict(book) for book in books]
    
    def get_available_books(self):
        """Get all available books"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books WHERE available_copies > 0 ORDER BY title')
        books = cursor.fetchall()
        conn.close()
        
        return [dict(book) for book in books]
    
    # BOOK ISSUE MANAGEMENT
    def issue_book(self, user_id, book_id, days=14):
        """Issue a book to a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check book availability
            cursor.execute('SELECT available_copies FROM books WHERE book_id = ?', (book_id,))
            book = cursor.fetchone()
            
            if not book or book['available_copies'] <= 0:
                return {'status': 'error', 'message': 'Book not available'}
            
            # Calculate due date
            due_date = (datetime.now() + timedelta(days=days)).date()
            
            # Create issue record
            cursor.execute('''
                INSERT INTO book_issues (user_id, book_id, due_date, status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, book_id, due_date, 'issued'))
            
            # Update available copies
            cursor.execute('UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?', (book_id,))
            
            conn.commit()
            issue_id = cursor.lastrowid
            return {'status': 'success', 'issue_id': issue_id, 'due_date': str(due_date), 'message': 'Book issued successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def return_book(self, issue_id):
        """Return a borrowed book"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get issue details
            cursor.execute('SELECT * FROM book_issues WHERE issue_id = ?', (issue_id,))
            issue = cursor.fetchone()
            
            if not issue:
                return {'status': 'error', 'message': 'Issue record not found'}
            
            if issue['status'] == 'returned':
                return {'status': 'error', 'message': 'Book already returned'}
            
            # Update issue status
            cursor.execute('UPDATE book_issues SET return_date = ?, status = ? WHERE issue_id = ?',
                          (datetime.now().date(), 'returned', issue_id))
            
            # Update book availability
            cursor.execute('UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?',
                          (issue['book_id'],))
            
            conn.commit()
            return {'status': 'success', 'message': 'Book returned successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def get_user_books(self, user_id):
        """Get all books issued to a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bi.issue_id, b.title, b.author, bi.issue_date, bi.due_date, bi.status
            FROM book_issues bi
            JOIN books b ON bi.book_id = b.book_id
            WHERE bi.user_id = ?
            ORDER BY bi.issue_date DESC
        ''', (user_id,))
        
        issues = cursor.fetchall()
        conn.close()
        
        return [dict(issue) for issue in issues]
    
    def get_overdue_books(self):
        """Get all overdue books"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bi.issue_id, u.first_name, u.last_name, u.email, b.title,
                   bi.due_date, julianday('now') - julianday(bi.due_date) as days_overdue
            FROM book_issues bi
            JOIN users u ON bi.user_id = u.user_id
            JOIN books b ON bi.book_id = b.book_id
            WHERE bi.status = 'issued' AND bi.due_date < date('now')
            ORDER BY bi.due_date
        ''')
        
        overdue = cursor.fetchall()
        conn.close()
        
        return [dict(item) for item in overdue]
    
    # RESERVATION MANAGEMENT
    def reserve_book(self, user_id, book_id):
        """Reserve a book"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO reservations (user_id, book_id, status)
                VALUES (?, ?, ?)
            ''', (user_id, book_id, 'pending'))
            
            conn.commit()
            reservation_id = cursor.lastrowid
            return {'status': 'success', 'reservation_id': reservation_id, 'message': 'Book reserved successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def get_user_reservations(self, user_id):
        """Get user's reservations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.reservation_id, b.title, b.author, r.reservation_date, r.status
            FROM reservations r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = ?
            ORDER BY r.reservation_date DESC
        ''', (user_id,))
        
        reservations = cursor.fetchall()
        conn.close()
        
        return [dict(res) for res in reservations]
    
    # FINE MANAGEMENT
    def calculate_fine(self, issue_id, daily_rate=5):
        """Calculate fine for overdue book"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM book_issues WHERE issue_id = ?', (issue_id,))
        issue = cursor.fetchone()
        
        if not issue or issue['status'] == 'returned':
            conn.close()
            return {'status': 'error', 'message': 'Invalid issue record'}
        
        due_date = datetime.strptime(issue['due_date'], '%Y-%m-%d')
        today = datetime.now()
        
        if today > due_date:
            days_overdue = (today - due_date).days
            fine_amount = days_overdue * daily_rate
        else:
            fine_amount = 0
        
        conn.close()
        return {'fine_amount': fine_amount, 'days_overdue': max(0, (today - due_date).days)}
    
    def add_fine(self, user_id, issue_id, fine_amount):
        """Add fine to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO fines (user_id, issue_id, fine_amount, status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, issue_id, fine_amount, 'pending'))
            
            conn.commit()
            fine_id = cursor.lastrowid
            return {'status': 'success', 'fine_id': fine_id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def pay_fine(self, fine_id):
        """Mark fine as paid"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE fines SET status = ?, paid_date = ? WHERE fine_id = ?',
                          ('paid', datetime.now().date(), fine_id))
            conn.commit()
            return {'status': 'success', 'message': 'Fine paid successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def get_user_fines(self, user_id):
        """Get all fines for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM fines WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        fines = cursor.fetchall()
        conn.close()
        
        return [dict(fine) for fine in fines]
    
    # FEEDBACK MANAGEMENT
    def add_feedback(self, user_id, feedback_text, rating):
        """Add feedback from user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO feedback (user_id, feedback_text, rating)
                VALUES (?, ?, ?)
            ''', (user_id, feedback_text, rating))
            
            conn.commit()
            return {'status': 'success', 'message': 'Feedback submitted successfully'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            conn.close()
    
    def get_feedback(self):
        """Get all feedback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.feedback_id, u.first_name, u.last_name, f.feedback_text, f.rating, f.created_at
            FROM feedback f
            JOIN users u ON f.user_id = u.user_id
            ORDER BY f.created_at DESC
        ''')
        
        feedback = cursor.fetchall()
        conn.close()
        
        return [dict(item) for item in feedback]
