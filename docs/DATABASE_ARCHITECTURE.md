# Student Library Management System - Database Architecture

## System Overview
The Student Library Management System is a comprehensive web application designed to manage library operations, including book circulation, user management, reservations, and fine tracking.

## Database Design

### 1. Entity Relationship Diagram (ERD)

The system consists of 7 main entities:

```
┌─────────────┐
│   Users     │
├─────────────┤
│ user_id (PK)│
│ user_type   │
│ email       │
│ password    │
│ first_name  │
│ last_name   │
│ phone       │
│ student_id  │
│ department  │
└─────────────┘
      │
      │ 1:N
      │
      └───────────────────────────────────┐
      │                                   │
      ├─── 1:N ──→ ┌──────────────────┐  │
      │            │ Book_Issues      │  │
      │            ├──────────────────┤  │
      │            │ issue_id (PK)    │  │
      │            │ user_id (FK)     │  │
      │            │ book_id (FK)     │  │
      │            │ issue_date       │  │
      │            │ due_date         │  │
      │            │ return_date      │  │
      │            │ status           │  │
      │            └──────────────────┘  │
      │                    │             │
      │                    │ 1:N         │
      │                    │             │
      │                    └─→ ┌───────┐ │
      │                        │ Fines │ │
      │                        └───────┘ │
      │                                  │
      ├─── 1:N ──→ ┌─────────────────┐  │
      │            │ Reservations    │  │
      │            ├─────────────────┤  │
      │            │ reservation_id  │  │
      │            │ user_id (FK)    │  │
      │            │ book_id (FK)    │  │
      │            │ reservation_date│  │
      │            │ status          │  │
      │            └─────────────────┘  │
      │                                  │
      └─── 1:N ──→ ┌──────────────────┐ │
                   │ Feedback         │ │
                   ├──────────────────┤ │
                   │ feedback_id (PK) │ │
                   │ user_id (FK)     │ │
                   │ feedback_text    │ │
                   │ rating           │ │
                   │ created_at       │ │
                   └──────────────────┘ │
                                        │
┌──────────────┐                        │
│    Books     │                        │
├──────────────┤                        │
│ book_id (PK) │                        │
│ isbn         │                        │
│ title        │◄───────────────────────┘
│ author       │
│ publisher    │
│ category     │
│ total_copies │
│ available    │
│ description  │
└──────────────┘
```

### 2. Relational Schema

#### Users Table
```sql
users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_type VARCHAR(20) NOT NULL, -- 'student', 'admin', 'librarian'
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Keys:**
- Primary Key: user_id
- Unique Keys: email, student_id
- Indexes: email, user_type

#### Books Table
```sql
books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    publication_year INT,
    category VARCHAR(100),
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Keys:**
- Primary Key: book_id
- Unique Key: isbn
- Indexes: title, author, category

#### Book_Issues Table
```sql
book_issues (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    book_id INT NOT NULL FOREIGN KEY REFERENCES books(book_id),
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'issued', -- 'issued', 'returned', 'overdue'
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Keys:**
- Primary Key: issue_id
- Foreign Keys: user_id (users), book_id (books)
- Indexes: user_id, book_id, status

#### Reservations Table
```sql
reservations (
    reservation_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    book_id INT NOT NULL FOREIGN KEY REFERENCES books(book_id),
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'fulfilled', 'cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Keys:**
- Primary Key: reservation_id
- Foreign Keys: user_id (users), book_id (books)
- Indexes: user_id, book_id, status

#### Fines Table
```sql
fines (
    fine_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    issue_id INT NOT NULL FOREIGN KEY REFERENCES book_issues(issue_id),
    fine_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'paid'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_date DATE
)
```

**Keys:**
- Primary Key: fine_id
- Foreign Keys: user_id (users), issue_id (book_issues)
- Indexes: user_id, status

#### Feedback Table
```sql
feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    feedback_text TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Keys:**
- Primary Key: feedback_id
- Foreign Key: user_id (users)

### 3. Relationships

1. **Users → Book_Issues** (1:N)
   - One user can have multiple book issues
   - Relationship: user_id in book_issues references users table

2. **Books → Book_Issues** (1:N)
   - One book can be issued multiple times
   - Relationship: book_id in book_issues references books table

3. **Users → Reservations** (1:N)
   - One user can make multiple reservations
   - Relationship: user_id in reservations references users table

4. **Books → Reservations** (1:N)
   - One book can be reserved by multiple users
   - Relationship: book_id in reservations references books table

5. **Users → Fines** (1:N)
   - One user can have multiple fines
   - Relationship: user_id in fines references users table

6. **Book_Issues → Fines** (1:N)
   - One issue can have one or multiple fines
   - Relationship: issue_id in fines references book_issues table

7. **Users → Feedback** (1:N)
   - One user can provide multiple feedback
   - Relationship: user_id in feedback references users table

### 4. Normalization

The database is normalized to **3NF (Third Normal Form)**:

- **1NF:** All attributes are atomic values
- **2NF:** All non-key attributes depend on the entire primary key
- **3NF:** No non-key attribute depends on another non-key attribute

### 5. Indexing Strategy

Indexes are created for:
- Frequently searched columns (email, title, author, category)
- Foreign keys (to speed up joins)
- Status columns (for filtering queries)

### 6. Data Integrity

- **Primary Keys:** Ensure unique identification of records
- **Foreign Keys:** Maintain referential integrity
- **Unique Constraints:** Prevent duplicate emails and ISBNs
- **Check Constraints:** Validate user_type and status values
- **NOT NULL Constraints:** Ensure required data is present

### 7. Triggers and Stored Procedures (Optional)

Future enhancements could include:
- Auto-update book available_copies on issue/return
- Auto-generate fines for overdue books
- Auto-update book_issues status to 'overdue'

### 8. Performance Considerations

- Indexes on frequently queried columns
- Proper data types (INT for IDs instead of VARCHAR)
- Denormalization of available_copies for quick access
- Regular database cleanup of old records

### 9. Security Measures

- Password hashing (SHA-256)
- Parameterized queries (to prevent SQL injection)
- Role-based access control (student/admin/librarian)
- Audit trails with created_at and updated_at timestamps
