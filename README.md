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

The application includes a CLI for interacting with the database.

### Available Commands

You can use the CLI either with the launcher script or directly with Python:

**Using the launcher script (recommended):**
```bash
./cli.sh add-student --name "John Doe" --email "john@example.com"
./cli.sh list-students
./cli.sh add-grade --student-id 1 --subject "Math" --score 85
./cli.sh rankings
./cli.sh export-students --output students.csv
```

**Or directly with Python:**
```bash
PYTHONPATH=/home/engine/project python cli/commands.py add-student --name "John Doe" --email "john@example.com"
PYTHONPATH=/home/engine/project python cli/commands.py list-students
PYTHONPATH=/home/engine/project python cli/commands.py add-grade --student-id 1 --subject "Math" --score 85
PYTHONPATH=/home/engine/project python cli/commands.py rankings
PYTHONPATH=/home/engine/project python cli/commands.py export-students --output students.csv
```

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
