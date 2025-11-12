# Student Management System

A Flask-based web application for managing students, grades, and rankings with CSV export functionality.

## Features

- **Student Management**: Create, read, update, and delete student records
- **Grade Tracking**: Add and manage grades for each student
- **Rankings**: View student rankings based on average grades
- **CSV Export**: Download student and grade data as CSV files
- **Form Validation**: Built-in validation with user feedback
- **Responsive UI**: Bootstrap-based interface that works on all devices
- **CLI Support**: Command-line interface for interacting with the system

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with Flask-SQLAlchemy
- **Forms**: Flask-WTF with WTForms validation
- **Frontend**: Bootstrap 5 (CDN)
- **Testing**: pytest with Flask test client

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application supports environment-specific configurations through environment variables:

### Environment Variables

- `FLASK_ENV`: Application environment (`development`, `testing`, `production`). Default: `development`
- `SECRET_KEY`: Secret key for session management. Default: `dev-secret-key-change-in-production`
- `DATABASE_URL`: Database connection URL. Default: `sqlite:///students.db`
- `FLASK_HOST`: Host to bind the web server. Default: `0.0.0.0`
- `FLASK_PORT`: Port to bind the web server. Default: `5000`
- `FLASK_DEBUG`: Enable debug mode. Default: `True`

### Example Configuration

Create a `.env` file in the project root (optional):
```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///students.db
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

## Running the Application

### Quick Start

Use the provided start script to automatically set up and run the application:

```bash
./start.sh
```

This script will:
- Create a virtual environment if it doesn't exist
- Install dependencies if needed
- Start the web server

### Web Server

To launch the web server manually:

```bash
source venv/bin/activate  # Activate virtual environment
python run.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

For production, set environment variables:

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY=your-secure-secret-key
python run.py
```

Or use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

## Command-Line Interface (CLI)

The application includes a comprehensive CLI for managing students and grades from the command line. The CLI provides commands for CRUD operations, rankings, and data export.

### Running CLI Commands

#### Using the launcher script (recommended):
```bash
./cli.sh <command> [options]
```

#### Or directly with Python:
```bash
PYTHONPATH=/home/engine/project python cli/commands.py <command> [options]
```

### Global Options

- `--db PATH`: Specify a custom database file path (optional)
  - Example: `./cli.sh --db ./custom.db add-student --name "John" --email "john@example.com"`

### Student Commands

#### Add a Student
```bash
./cli.sh add-student --name "John Doe" --email "john@example.com"
```
Creates a new student record. Email must be unique.

**Options:**
- `--name TEXT`: Student name (prompted if not provided)
- `--email TEXT`: Student email (prompted if not provided)

**Exit Codes:**
- `0`: Success
- `1`: Error (duplicate email, invalid input, etc.)

#### List Students
```bash
./cli.sh list-students
./cli.sh list-students --student-id 1
```
Displays all students (or specific student) in a table format with ID, name, email, average grade, and grade count.

**Options:**
- `--student-id INTEGER`: Show only a specific student (optional)

#### Edit a Student
```bash
./cli.sh edit-student --student-id 1 --name "Jane Doe"
./cli.sh edit-student --student-id 1 --email "jane.doe@example.com"
./cli.sh edit-student --student-id 1 --name "Jane Doe" --email "jane@example.com"
```
Updates student name and/or email. If a field is not provided, it keeps the current value.

**Options:**
- `--student-id INTEGER`: Student ID to edit (required)
- `--name TEXT`: New name (optional)
- `--email TEXT`: New email (optional)

**Exit Codes:**
- `0`: Success
- `1`: Student not found, duplicate email, etc.

#### Delete a Student
```bash
./cli.sh delete-student --student-id 1
./cli.sh delete-student --student-id 1 --confirm
```
Deletes a student and all associated grades. Without `--confirm`, prompts for confirmation.

**Options:**
- `--student-id INTEGER`: Student ID to delete (required)
- `--confirm`: Skip confirmation prompt (optional)

**Exit Codes:**
- `0`: Success or deletion cancelled
- `1`: Student not found

### Grade Commands

#### Add a Grade
```bash
./cli.sh add-grade --student-id 1 --subject "Math" --score 85
./cli.sh add-grade --student-id 1 --subject "English" --score 92.5
```
Records a grade for a student. Score must be between 0 and 100.

**Options:**
- `--student-id INTEGER`: Student ID (required)
- `--subject TEXT`: Subject name (prompted if not provided)
- `--score FLOAT`: Grade score 0-100 (prompted if not provided)

**Exit Codes:**
- `0`: Success
- `1`: Student not found, invalid score, etc.

#### List Grades
```bash
./cli.sh list-grades
./cli.sh list-grades --student-id 1
```
Displays all grades or grades for a specific student in a table format.

**Options:**
- `--student-id INTEGER`: Show only grades for specific student (optional)

#### Edit a Grade
```bash
./cli.sh edit-grade --grade-id 1 --score 95
./cli.sh edit-grade --grade-id 1 --subject "Advanced Math" --score 95
```
Updates a grade's subject and/or score. If a field is not provided, it keeps the current value.

**Options:**
- `--grade-id INTEGER`: Grade ID to edit (required)
- `--subject TEXT`: New subject (optional)
- `--score FLOAT`: New score 0-100 (optional)

**Exit Codes:**
- `0`: Success
- `1`: Grade not found, invalid score, etc.

#### Delete a Grade
```bash
./cli.sh delete-grade --grade-id 1
./cli.sh delete-grade --grade-id 1 --confirm
```
Deletes a grade record. Without `--confirm`, prompts for confirmation.

**Options:**
- `--grade-id INTEGER`: Grade ID to delete (required)
- `--confirm`: Skip confirmation prompt (optional)

**Exit Codes:**
- `0`: Success or deletion cancelled
- `1`: Grade not found

### Rankings and Analytics

#### View Rankings
```bash
./cli.sh rankings
```
Displays student rankings sorted by average grade with medals for top 3 students.

**Output includes:**
- Rank (with medal 🥇🥈🥉 for top 3)
- Student name and email
- Average grade
- Number of grades

### Data Export

#### Export Students to CSV
```bash
./cli.sh export-students
./cli.sh export-students --output my_students.csv
```
Exports student data with averages to a CSV file.

**Options:**
- `--output TEXT`: Output filename (default: `students.csv`)

**CSV Columns:** ID, Name, Email, Average Grade, Number of Grades

#### Export Grades to CSV
```bash
./cli.sh export-grades
./cli.sh export-grades --output my_grades.csv
```
Exports grade records to a CSV file.

**Options:**
- `--output TEXT`: Output filename (default: `grades.csv`)

**CSV Columns:** Grade ID, Student Name, Subject, Score, Date

### Usage Examples

#### Complete Workflow
```bash
# Add students
./cli.sh add-student --name "Alice Smith" --email "alice@example.com"
./cli.sh add-student --name "Bob Johnson" --email "bob@example.com"

# List students
./cli.sh list-students

# Add grades
./cli.sh add-grade --student-id 1 --subject "Math" --score 95
./cli.sh add-grade --student-id 1 --subject "English" --score 87
./cli.sh add-grade --student-id 2 --subject "Math" --score 78
./cli.sh add-grade --student-id 2 --subject "English" --score 92

# View grades for a student
./cli.sh list-grades --student-id 1

# View rankings
./cli.sh rankings

# Export data
./cli.sh export-students --output results.csv
./cli.sh export-grades --output grades.csv
```

#### Using a Custom Database
```bash
# Create students in a custom database
./cli.sh --db /tmp/students_test.db add-student --name "Test User" --email "test@example.com"

# View students in custom database
./cli.sh --db /tmp/students_test.db list-students

# Export from custom database
./cli.sh --db /tmp/students_test.db export-students --output test_results.csv
```

### Error Handling

The CLI provides clear error messages for:
- Missing required parameters
- Invalid input (e.g., scores outside 0-100 range)
- Non-existent records (student not found, grade not found)
- Duplicate emails
- Invalid database paths

All error messages are printed to stderr with appropriate exit code 1 for easy integration with scripts.

## Database

### Shared Database Configuration

Both the web application and CLI share the same SQLite database configuration defined in `app/config.py`. The database file is created automatically at `students.db` in the project root.

### Database Schema

**Students Table:**
- `id`: Primary key
- `name`: Student name (required)
- `email`: Student email (unique, required)
- `created_at`: Timestamp

**Grades Table:**
- `id`: Primary key
- `student_id`: Foreign key to students
- `subject`: Subject name (required)
- `score`: Grade score 0-100 (required)
- `created_at`: Timestamp

### Database Initialization

The database is automatically initialized when the application starts. Tables are created if they don't exist.

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

Run specific test files:

```bash
pytest tests/test_web.py
```

### Test Coverage

The test suite includes:
- Index route tests
- Student CRUD operations
- Grade management
- Rankings display
- CSV export functionality
- Form validation
- Cascade delete operations

## Web Interface Usage

### Students

1. **View Students**: Navigate to `/students/` to see all students
2. **Add Student**: Click "Add New Student" and fill in the form
3. **Edit Student**: Click "Edit" next to a student record
4. **Delete Student**: Click "Delete" (confirms before deletion)

### Grades

1. **View Grades**: Click "Grades" next to a student in the student list
2. **Add Grade**: Click "Add Grade" on the grades page
3. **Edit Grade**: Click "Edit" next to a grade record
4. **Delete Grade**: Click "Delete" (confirms before deletion)

### Rankings

Navigate to `/students/rankings` to view student rankings by average grade. Rankings display:
- Student rank (with medals for top 3)
- Student name and email
- Average grade
- Number of grades

### CSV Export

Export data from the navigation menu:
- **Export Students**: Downloads `students.csv` with student data and averages
- **Export Grades**: Downloads `grades.csv` with all grade records

## Project Structure

```
.
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── models.py                # SQLAlchemy models
│   ├── services.py              # Business logic layer
│   ├── blueprints/              # Flask blueprints
│   │   ├── students.py          # Student routes
│   │   ├── grades.py            # Grade routes
│   │   └── export.py            # Export routes
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── students/
│   │   └── grades/
│   └── static/                  # Static files
│       └── css/
│           └── custom.css
├── cli/
│   └── commands.py              # CLI commands
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   └── test_web.py              # Functional tests
├── run.py                       # Web server entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Architecture

The application follows a layered architecture:

1. **Presentation Layer**: Flask blueprints and templates
2. **Service Layer**: Business logic in `services.py`
3. **Data Layer**: SQLAlchemy models in `models.py`

This separation allows the web interface and CLI to share the same business logic and database configuration.

## Flash Messages

The application uses Flask's flash messaging system to provide user feedback:
- **Success**: Green alerts for successful operations
- **Danger**: Red alerts for errors
- **Info**: Blue alerts for informational messages

## Form Validation

Forms include built-in validation:
- Required fields
- Email format validation
- Score range validation (0-100)
- Unique email constraint

Validation errors are displayed inline with the form fields.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is open source and available under the MIT License.
