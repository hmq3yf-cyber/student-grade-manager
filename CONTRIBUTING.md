# Contributing to Student Management System

Thank you for your interest in contributing to this project!

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Running Tests

Run the test suite before submitting any changes:

```bash
pytest -v
```

For test coverage:

```bash
pytest --cov=app tests/
```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Keep functions small and focused on a single responsibility
- Add docstrings for complex functions
- Use the service layer for business logic
- Keep routes thin - delegate to services

## Project Structure

- `app/` - Main application code
  - `blueprints/` - Flask blueprints for route organization
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS and other static files
  - `models.py` - Database models
  - `services.py` - Business logic layer
  - `config.py` - Application configuration
- `cli/` - Command-line interface
- `tests/` - Test suite

## Making Changes

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Write or update tests as needed
4. Run the test suite to ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

## Reporting Issues

When reporting issues, please include:

- A clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
