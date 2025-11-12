import csv
from io import StringIO
from app.models import db, Student, Grade
from sqlalchemy import func


class StudentService:
    @staticmethod
    def get_all_students():
        return Student.query.order_by(Student.name).all()
    
    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)
    
    @staticmethod
    def create_student(name, email):
        student = Student(name=name, email=email)
        db.session.add(student)
        db.session.commit()
        return student
    
    @staticmethod
    def update_student(student_id, name, email):
        student = Student.query.get(student_id)
        if student:
            student.name = name
            student.email = email
            db.session.commit()
        return student
    
    @staticmethod
    def delete_student(student_id):
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_rankings():
        students = Student.query.all()
        rankings = []
        for student in students:
            avg = student.average_grade()
            if avg > 0:
                rankings.append({
                    'student': student,
                    'average': avg
                })
        rankings.sort(key=lambda x: x['average'], reverse=True)
        return rankings


class GradeService:
    @staticmethod
    def get_grades_by_student(student_id):
        return Grade.query.filter_by(student_id=student_id).order_by(Grade.created_at.desc()).all()
    
    @staticmethod
    def create_grade(student_id, subject, score):
        grade = Grade(student_id=student_id, subject=subject, score=score)
        db.session.add(grade)
        db.session.commit()
        return grade
    
    @staticmethod
    def update_grade(grade_id, subject, score):
        grade = Grade.query.get(grade_id)
        if grade:
            grade.subject = subject
            grade.score = score
            db.session.commit()
        return grade
    
    @staticmethod
    def delete_grade(grade_id):
        grade = Grade.query.get(grade_id)
        if grade:
            db.session.delete(grade)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_grade_by_id(grade_id):
        return Grade.query.get(grade_id)


class ExportService:
    @staticmethod
    def export_students_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Email', 'Average Grade', 'Number of Grades'])
        
        students = Student.query.all()
        for student in students:
            writer.writerow([
                student.id,
                student.name,
                student.email,
                round(student.average_grade(), 2),
                len(student.grades)
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_grades_to_csv():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Grade ID', 'Student Name', 'Subject', 'Score', 'Date'])
        
        grades = Grade.query.join(Student).order_by(Student.name, Grade.created_at).all()
        for grade in grades:
            writer.writerow([
                grade.id,
                grade.student.name,
                grade.subject,
                grade.score,
                grade.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return output.getvalue()
