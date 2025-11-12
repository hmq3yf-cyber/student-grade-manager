import pytest
from app import create_app
from app.models import db, Student, Grade


@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_student(app):
    with app.app_context():
        student = Student(name='John Doe', email='john@example.com')
        db.session.add(student)
        db.session.commit()
        student_id = student.id
    
    class StudentProxy:
        def __init__(self, student_id):
            self.id = student_id
    
    return StudentProxy(student_id)


@pytest.fixture
def sample_students(app):
    with app.app_context():
        students = [
            Student(name='Alice Smith', email='alice@example.com'),
            Student(name='Bob Johnson', email='bob@example.com'),
            Student(name='Charlie Brown', email='charlie@example.com')
        ]
        for student in students:
            db.session.add(student)
        db.session.commit()
        return students


@pytest.fixture
def student_with_grades(app):
    with app.app_context():
        student = Student(name='Jane Doe', email='jane@example.com')
        db.session.add(student)
        db.session.commit()
        
        grades = [
            Grade(student_id=student.id, subject='Math', score=85.0),
            Grade(student_id=student.id, subject='English', score=90.0),
            Grade(student_id=student.id, subject='Science', score=78.0)
        ]
        for grade in grades:
            db.session.add(grade)
        db.session.commit()
        
        student_id = student.id
    
    class StudentProxy:
        def __init__(self, student_id):
            self.id = student_id
    
    return StudentProxy(student_id)
