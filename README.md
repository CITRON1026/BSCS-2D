# Student Library Management System

## Project Overview

A comprehensive web-based library management system designed for educational institutions. The system enables students to browse books, issue/return books, make reservations, track fines, and provide feedback. Librarians and administrators can manage the book catalog, track overdue items, and monitor system usage.

## Features

### Student Features
- **User Registration & Login** - Secure authentication
- **Browse Books** - Search by title, author, or category
- **Issue Books** - Borrow books with automatic due date calculation
- **Return Books** - Easy book return process
- **Reservations** - Reserve unavailable books
- **Track Fines** - View pending fines and payment status
- **Leave Feedback** - Rate and comment on library services
- **Dashboard** - View borrowing statistics and activity

### Admin/Librarian Features
- **Book Management** - Add, edit, and manage book catalog
- **Overdue Tracking** - Monitor overdue books and users
- **Fine Management** - Calculate and process fines
- **User Management** - Manage student accounts
- **Feedback Review** - View and analyze user feedback
- **System Reports** - Generate usage reports

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.0** - Web framework
- **SQLite3** - Database
- **Jinja2** - Template engine

### Frontend
- **HTML5** - Structure
- **CSS3/Bootstrap 5** - Styling
- **JavaScript/jQuery** - Interactivity

### Database
- **SQLite** - Relational database
- **7 Main Tables** with proper relationships
- **Full ACID compliance**

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CITRON1026/BSCS-2D.git
   cd BSCS-2D
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python
   >>> from database.database import LibraryDatabase
   >>> db = LibraryDatabase()
   >>> exit()
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Database Schema

### Tables
1. **users** - User accounts (students, admins, librarians)
2. **books** - Book catalog
3. **book_issues** - Book borrowing records
4. **reservations** - Book reservations
5. **fines** - Fine records
6. **feedback** - User feedback

For detailed schema information, see `docs/DATABASE_ARCHITECTURE.md`

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Books
- `GET /api/books` - Get all available books
- `GET /api/books/search` - Search books
- `POST /api/books` - Add new book (admin only)

### Book Issues
- `POST /api/issues` - Issue a book
- `POST /api/issues/<id>` - Return a book
- `GET /api/my-books` - Get user's issued books

### Reservations
- `POST /api/reservations` - Reserve a book
- `GET /api/my-reservations` - Get user's reservations

### Fines
- `GET /api/fines` - Get user's fines
- `POST /api/fines/<id>/pay` - Pay a fine

### Admin
- `GET /api/overdue-books` - Get overdue books
- `GET /api/feedback` - Get all feedback

## File Structure

```
BSCS-2D/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── database/
│   ├── schema.sql           # Database schema
│   ├── database.py          # Database operations class
│   └── library_system.db    # SQLite database file
├── templates/
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── student_dashboard.html  # Student dashboard
│   ├── admin_dashboard.html    # Admin dashboard
│   ├── books.html          # Book browsing
│   ├── my_books.html       # User's borrowed books
│   ├── reservations.html   # Reservations
│   ├── fines.html          # Fine management
│   ├── feedback.html       # Feedback form
│   └── admin/
│       ├── overdue.html    # Overdue books (admin)
│       └── feedback.html   # Feedback review (admin)
└── docs/
    └── DATABASE_ARCHITECTURE.md  # Detailed database documentation
```

## Usage Examples

### Register as a Student
1. Go to `/register`
2. Fill in your details
3. Create account
4. Login with your credentials

### Borrow a Book
1. Navigate to "Books"
2. Search or browse available books
3. Click "Issue Book"
4. Book will be issued for 14 days by default

### Return a Book
1. Go to "My Books"
2. Find the issued book
3. Click "Return"
4. Book will be returned to available inventory

### Reserve a Book
1. If a book is unavailable, click "Reserve"
2. You'll be notified when the book is available

## Sample Data

To add sample books, use the admin panel or run:

```python
from database.database import LibraryDatabase

db = LibraryDatabase()
db.add_book(
    isbn="978-0134685991",
    title="Effective Java",
    author="Joshua Bloch",
    publisher="Addison-Wesley",
    publication_year=2018,
    category="Programming",
    total_copies=5,
    description="A guide to writing effective and maintainable Java programs"
)
```

## Security Features

- **Password Hashing** - SHA-256 encryption
- **SQL Injection Prevention** - Parameterized queries
- **Session Management** - Secure user sessions
- **Role-Based Access Control** - Different permissions for different user types
- **Input Validation** - Client and server-side validation

## Performance Optimizations

- **Database Indexing** - On frequently searched columns
- **Query Optimization** - Efficient SQL queries
- **Caching** - Where applicable
- **Pagination** - For large result sets

## Troubleshooting

### Database Issues
- Delete `library_system.db` to reset the database
- Run the initialization script again

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

### Import Errors
- Make sure virtual environment is activated
- Install all requirements: `pip install -r requirements.txt`

## Future Enhancements

- [ ] Email notifications for due dates
- [ ] Mobile app
- [ ] QR code scanning for books
- [ ] Book recommendations engine
- [ ] Integration with payment gateways
- [ ] Advanced analytics dashboard
- [ ] API documentation (Swagger)

## Contributors

- CITRON1026 - Lead Developer

## License

MIT License - Free to use and modify

## Support

For issues or questions, please create an issue on GitHub.

## Acknowledgments

- Flask documentation
- Bootstrap framework
- SQLite3
- jQuery library
