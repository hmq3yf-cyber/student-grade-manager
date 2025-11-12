import click
import os
import sys
from pathlib import Path
from tabulate import tabulate
from app import create_app
from app.models import db, Student, Grade
from app.services import StudentService, GradeService, ExportService


def get_app(db_path=None):
    """Create and configure app with optional custom database path."""
    app = create_app('default', db_path=db_path)
    return app


@click.group()
@click.option('--db', type=click.Path(), help='Path to SQLite database file')
@click.pass_context
def cli(ctx, db):
    """Student Management System CLI"""
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['db'] = db


@cli.command()
@click.option('--name', prompt=True, help='Student name')
@click.option('--email', prompt=True, help='Student email')
@click.pass_context
def add_student(ctx, name, email):
    """Add a new student."""
    if not name or not name.strip():
        click.echo('Error: Student name cannot be empty.', err=True)
        sys.exit(1)
    
    if not email or not email.strip():
        click.echo('Error: Student email cannot be empty.', err=True)
        sys.exit(1)
    
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        try:
            # Check if email already exists
            existing = Student.query.filter_by(email=email).first()
            if existing:
                click.echo(f'Error: Email "{email}" is already registered.', err=True)
                sys.exit(1)
            
            student = StudentService.create_student(name, email)
            click.echo(f'✓ Student created successfully!')
            click.echo(f'  Name: {student.name}')
            click.echo(f'  Email: {student.email}')
            click.echo(f'  ID: {student.id}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--student-id', type=int, required=True, help='Student ID')
@click.option('--name', help='New name (optional)')
@click.option('--email', help='New email (optional)')
@click.pass_context
def edit_student(ctx, student_id, name, email):
    """Edit an existing student."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        student = StudentService.get_student_by_id(student_id)
        if not student:
            click.echo(f'Error: Student with ID {student_id} not found.', err=True)
            sys.exit(1)
        
        # Use provided values or keep existing ones
        new_name = name if name else student.name
        new_email = email if email else student.email
        
        try:
            # Check if new email is already in use by another student
            if new_email != student.email:
                existing = Student.query.filter_by(email=new_email).first()
                if existing:
                    click.echo(f'Error: Email "{new_email}" is already registered.', err=True)
                    sys.exit(1)
            
            updated = StudentService.update_student(student_id, new_name, new_email)
            click.echo(f'✓ Student updated successfully!')
            click.echo(f'  ID: {updated.id}')
            click.echo(f'  Name: {updated.name}')
            click.echo(f'  Email: {updated.email}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--student-id', type=int, required=True, help='Student ID')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_student(ctx, student_id, confirm):
    """Delete a student and all their grades."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        student = StudentService.get_student_by_id(student_id)
        if not student:
            click.echo(f'Error: Student with ID {student_id} not found.', err=True)
            sys.exit(1)
        
        grade_count = len(student.grades)
        message = f'Delete student "{student.name}"'
        if grade_count > 0:
            message += f' and their {grade_count} grade(s)'
        message += '?'
        
        if not confirm and not click.confirm(message):
            click.echo('Deletion cancelled.')
            sys.exit(0)
        
        try:
            StudentService.delete_student(student_id)
            click.echo(f'✓ Student deleted successfully!')
            if grade_count > 0:
                click.echo(f'  {grade_count} grade(s) were also deleted.')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--student-id', type=int, help='Filter by student ID (optional)')
@click.pass_context
def list_students(ctx, student_id):
    """List all students with their average grades."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        if student_id:
            students = [StudentService.get_student_by_id(student_id)]
            if not students[0]:
                click.echo(f'Error: Student with ID {student_id} not found.', err=True)
                sys.exit(1)
        else:
            students = StudentService.get_all_students()
        
        if not students:
            click.echo('No students found.')
            sys.exit(0)
        
        table_data = []
        for student in students:
            avg = student.average_grade()
            grade_count = len(student.grades)
            table_data.append([
                student.id,
                student.name,
                student.email,
                f'{avg:.2f}',
                grade_count
            ])
        
        headers = ['ID', 'Name', 'Email', 'Average', 'Grades']
        click.echo('\n' + tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@cli.command()
@click.option('--student-id', type=int, required=True, help='Student ID')
@click.option('--subject', prompt=True, help='Subject name')
@click.option('--score', type=float, prompt=True, help='Grade score (0-100)')
@click.pass_context
def add_grade(ctx, student_id, subject, score):
    """Add a grade for a student."""
    if not subject or not subject.strip():
        click.echo('Error: Subject name cannot be empty.', err=True)
        sys.exit(1)
    
    if score < 0 or score > 100:
        click.echo('Error: Score must be between 0 and 100.', err=True)
        sys.exit(1)
    
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        student = StudentService.get_student_by_id(student_id)
        if not student:
            click.echo(f'Error: Student with ID {student_id} not found.', err=True)
            sys.exit(1)
        
        try:
            grade = GradeService.create_grade(student_id, subject, score)
            click.echo(f'✓ Grade added successfully!')
            click.echo(f'  Student: {student.name}')
            click.echo(f'  Subject: {grade.subject}')
            click.echo(f'  Score: {grade.score}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--grade-id', type=int, required=True, help='Grade ID')
@click.option('--subject', help='New subject (optional)')
@click.option('--score', type=float, help='New score (optional)')
@click.pass_context
def edit_grade(ctx, grade_id, subject, score):
    """Edit an existing grade."""
    if score is not None and (score < 0 or score > 100):
        click.echo('Error: Score must be between 0 and 100.', err=True)
        sys.exit(1)
    
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        grade = GradeService.get_grade_by_id(grade_id)
        if not grade:
            click.echo(f'Error: Grade with ID {grade_id} not found.', err=True)
            sys.exit(1)
        
        new_subject = subject if subject else grade.subject
        new_score = score if score is not None else grade.score
        
        try:
            updated = GradeService.update_grade(grade_id, new_subject, new_score)
            click.echo(f'✓ Grade updated successfully!')
            click.echo(f'  Student: {updated.student.name}')
            click.echo(f'  Subject: {updated.subject}')
            click.echo(f'  Score: {updated.score}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--grade-id', type=int, required=True, help='Grade ID')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_grade(ctx, grade_id, confirm):
    """Delete a grade."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        grade = GradeService.get_grade_by_id(grade_id)
        if not grade:
            click.echo(f'Error: Grade with ID {grade_id} not found.', err=True)
            sys.exit(1)
        
        message = f'Delete grade: {grade.subject} ({grade.score}) for {grade.student.name}?'
        
        if not confirm and not click.confirm(message):
            click.echo('Deletion cancelled.')
            sys.exit(0)
        
        try:
            GradeService.delete_grade(grade_id)
            click.echo(f'✓ Grade deleted successfully!')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--student-id', type=int, help='Filter by student ID (optional)')
@click.pass_context
def list_grades(ctx, student_id):
    """List grades, optionally filtered by student."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        if student_id:
            student = StudentService.get_student_by_id(student_id)
            if not student:
                click.echo(f'Error: Student with ID {student_id} not found.', err=True)
                sys.exit(1)
            grades = GradeService.get_grades_by_student(student_id)
            click.echo(f'\nGrades for {student.name}:')
        else:
            grades = Grade.query.all()
            if not grades:
                click.echo('No grades found.')
                sys.exit(0)
            click.echo('\nAll Grades:')
        
        if not grades:
            click.echo(f'No grades found.')
            sys.exit(0)
        
        table_data = []
        for grade in grades:
            table_data.append([
                grade.id,
                grade.student.name,
                grade.subject,
                grade.score,
                grade.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        headers = ['ID', 'Student', 'Subject', 'Score', 'Created']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@cli.command()
@click.pass_context
def rankings(ctx):
    """Display student rankings by average grade."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        rankings = StudentService.get_rankings()
        if not rankings:
            click.echo('No rankings available.')
            sys.exit(0)
        
        click.echo('\nStudent Rankings (sorted by average grade):')
        
        table_data = []
        for idx, item in enumerate(rankings, 1):
            student = item['student']
            avg = item['average']
            grade_count = len(student.grades)
            
            # Add medals for top 3
            medal = ''
            if idx == 1:
                medal = '🥇'
            elif idx == 2:
                medal = '🥈'
            elif idx == 3:
                medal = '🥉'
            
            rank_str = f'{medal} #{idx}'.strip()
            
            table_data.append([
                rank_str,
                student.name,
                student.email,
                f'{avg:.2f}',
                grade_count
            ])
        
        headers = ['Rank', 'Name', 'Email', 'Average', 'Grades']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo()


@cli.command()
@click.option('--output', default='students.csv', help='Output CSV filename')
@click.pass_context
def export_students(ctx, output):
    """Export students data to CSV file."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        try:
            csv_data = ExportService.export_students_to_csv()
            with open(output, 'w') as f:
                f.write(csv_data)
            
            # Count lines for feedback
            line_count = len(csv_data.strip().split('\n')) - 1
            click.echo(f'✓ Students exported successfully!')
            click.echo(f'  File: {output}')
            click.echo(f'  Records: {line_count}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


@cli.command()
@click.option('--output', default='grades.csv', help='Output CSV filename')
@click.pass_context
def export_grades(ctx, output):
    """Export grades data to CSV file."""
    app = get_app(ctx.obj.get('db'))
    with app.app_context():
        try:
            csv_data = ExportService.export_grades_to_csv()
            with open(output, 'w') as f:
                f.write(csv_data)
            
            # Count lines for feedback
            line_count = len(csv_data.strip().split('\n')) - 1
            click.echo(f'✓ Grades exported successfully!')
            click.echo(f'  File: {output}')
            click.echo(f'  Records: {line_count}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)
            sys.exit(1)


if __name__ == '__main__':
    cli(obj={})
