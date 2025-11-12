import pytest
from app.models import db, Student, Grade


class TestIndexRoute:
    def test_index_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Welcome to Student Management System' in response.data


class TestStudentRoutes:
    def test_list_students_empty(self, client):
        response = client.get('/students/')
        assert response.status_code == 200
        assert b'No students found' in response.data
    
    def test_list_students_with_data(self, client, sample_students):
        response = client.get('/students/')
        assert response.status_code == 200
        assert b'Alice Smith' in response.data
        assert b'Bob Johnson' in response.data
        assert b'Charlie Brown' in response.data
    
    def test_create_student_get(self, client):
        response = client.get('/students/create')
        assert response.status_code == 200
        assert b'Add New Student' in response.data
    
    def test_create_student_post_success(self, client, app):
        response = client.post('/students/create', data={
            'name': 'Test Student',
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Student created successfully!' in response.data
        
        with app.app_context():
            student = Student.query.filter_by(email='test@example.com').first()
            assert student is not None
            assert student.name == 'Test Student'
    
    def test_create_student_duplicate_email(self, client, sample_student):
        response = client.post('/students/create', data={
            'name': 'Another Student',
            'email': 'john@example.com'
        })
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_create_student_invalid_email(self, client):
        response = client.post('/students/create', data={
            'name': 'Test Student',
            'email': 'invalid-email'
        })
        
        assert response.status_code == 200
        assert b'Invalid email address' in response.data
    
    def test_edit_student_get(self, client, sample_student):
        response = client.get(f'/students/{sample_student.id}/edit')
        assert response.status_code == 200
        assert b'Edit Student' in response.data
        assert b'John Doe' in response.data
    
    def test_edit_student_post_success(self, client, app, sample_student):
        response = client.post(f'/students/{sample_student.id}/edit', data={
            'name': 'John Updated',
            'email': 'john.updated@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Student updated successfully!' in response.data
        
        with app.app_context():
            student = Student.query.get(sample_student.id)
            assert student.name == 'John Updated'
            assert student.email == 'john.updated@example.com'
    
    def test_edit_student_not_found(self, client):
        response = client.get('/students/9999/edit', follow_redirects=True)
        assert response.status_code == 200
        assert b'Student not found' in response.data
    
    def test_delete_student(self, client, app, sample_student):
        student_id = sample_student.id
        response = client.post(f'/students/{student_id}/delete', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Student deleted successfully!' in response.data
        
        with app.app_context():
            student = Student.query.get(student_id)
            assert student is None
    
    def test_rankings_empty(self, client):
        response = client.get('/students/rankings')
        assert response.status_code == 200
        assert b'No rankings available' in response.data
    
    def test_rankings_with_data(self, client, app, sample_students):
        with app.app_context():
            alice = Student.query.filter_by(name='Alice Smith').first()
            bob = Student.query.filter_by(name='Bob Johnson').first()
            
            db.session.add(Grade(student_id=alice.id, subject='Math', score=95.0))
            db.session.add(Grade(student_id=alice.id, subject='English', score=90.0))
            db.session.add(Grade(student_id=bob.id, subject='Math', score=85.0))
            db.session.commit()
        
        response = client.get('/students/rankings')
        assert response.status_code == 200
        assert b'Student Rankings' in response.data
        assert b'Alice Smith' in response.data
        assert b'Bob Johnson' in response.data


class TestGradeRoutes:
    def test_list_grades_for_student(self, client, student_with_grades):
        response = client.get(f'/grades/student/{student_with_grades.id}')
        assert response.status_code == 200
        assert b'Grades for Jane Doe' in response.data
        assert b'Math' in response.data
        assert b'English' in response.data
        assert b'Science' in response.data
    
    def test_list_grades_student_not_found(self, client):
        response = client.get('/grades/student/9999', follow_redirects=True)
        assert response.status_code == 200
        assert b'Student not found' in response.data
    
    def test_add_grade_get(self, client, sample_student):
        response = client.get(f'/grades/student/{sample_student.id}/add')
        assert response.status_code == 200
        assert b'Add Grade for John Doe' in response.data
    
    def test_add_grade_post_success(self, client, app, sample_student):
        response = client.post(f'/grades/student/{sample_student.id}/add', data={
            'student_id': sample_student.id,
            'subject': 'History',
            'score': 88.5
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Grade added successfully!' in response.data
        
        with app.app_context():
            grade = Grade.query.filter_by(subject='History').first()
            assert grade is not None
            assert grade.score == 88.5
    
    def test_add_grade_invalid_score(self, client, sample_student):
        response = client.post(f'/grades/student/{sample_student.id}/add', data={
            'student_id': sample_student.id,
            'subject': 'History',
            'score': 150
        })
        
        assert response.status_code == 200
        assert b'Number must be between 0 and 100' in response.data
    
    def test_edit_grade_get(self, client, app, student_with_grades):
        with app.app_context():
            grade = Grade.query.filter_by(subject='Math').first()
            grade_id = grade.id
        
        response = client.get(f'/grades/{grade_id}/edit')
        assert response.status_code == 200
        assert b'Edit Grade for Jane Doe' in response.data
    
    def test_edit_grade_post_success(self, client, app, student_with_grades):
        with app.app_context():
            grade = Grade.query.filter_by(subject='Math').first()
            grade_id = grade.id
        
        response = client.post(f'/grades/{grade_id}/edit', data={
            'student_id': student_with_grades.id,
            'subject': 'Mathematics',
            'score': 95.0
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Grade updated successfully!' in response.data
        
        with app.app_context():
            updated_grade = Grade.query.get(grade_id)
            assert updated_grade.subject == 'Mathematics'
            assert updated_grade.score == 95.0
    
    def test_delete_grade(self, client, app, student_with_grades):
        with app.app_context():
            grade = Grade.query.filter_by(subject='Math').first()
            grade_id = grade.id
            student_id = grade.student_id
        
        response = client.post(f'/grades/{grade_id}/delete', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Grade deleted successfully!' in response.data
        
        with app.app_context():
            deleted_grade = Grade.query.get(grade_id)
            assert deleted_grade is None


class TestExportRoutes:
    def test_export_students_csv(self, client, sample_students):
        response = client.get('/export/students')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert b'ID,Name,Email,Average Grade,Number of Grades' in response.data
        assert b'Alice Smith' in response.data
        assert b'Bob Johnson' in response.data
    
    def test_export_grades_csv(self, client, student_with_grades):
        response = client.get('/export/grades')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert b'Grade ID,Student Name,Subject,Score,Date' in response.data
        assert b'Jane Doe' in response.data
        assert b'Math' in response.data


class TestFormValidation:
    def test_student_form_missing_name(self, client):
        response = client.post('/students/create', data={
            'email': 'test@example.com'
        })
        assert response.status_code == 200
        assert b'This field is required' in response.data
    
    def test_student_form_missing_email(self, client):
        response = client.post('/students/create', data={
            'name': 'Test Student'
        })
        assert response.status_code == 200
        assert b'This field is required' in response.data
    
    def test_grade_form_missing_subject(self, client, sample_student):
        response = client.post(f'/grades/student/{sample_student.id}/add', data={
            'student_id': sample_student.id,
            'score': 85.0
        })
        assert response.status_code == 200
        assert b'This field is required' in response.data


class TestCascadeDelete:
    def test_delete_student_with_grades(self, client, app, student_with_grades):
        student_id = student_with_grades.id
        
        with app.app_context():
            grade_count = Grade.query.filter_by(student_id=student_id).count()
            assert grade_count == 3
        
        response = client.post(f'/students/{student_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        with app.app_context():
            student = Student.query.get(student_id)
            assert student is None
            
            remaining_grades = Grade.query.filter_by(student_id=student_id).count()
            assert remaining_grades == 0
