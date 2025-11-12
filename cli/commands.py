import click
from app import create_app
from app.models import db, Student, Grade
from app.services import StudentService, GradeService, ExportService


@click.group()
def cli():
    pass


@cli.command()
@click.option('--name', prompt='Student name', help='Name of the student')
@click.option('--email', prompt='Student email', help='Email of the student')
def add_student(name, email):
    app = create_app('default')
    with app.app_context():
        try:
            student = StudentService.create_student(name, email)
            click.echo(f'Student created: {student.name} (ID: {student.id})')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)


@cli.command()
def list_students():
    app = create_app('default')
    with app.app_context():
        students = StudentService.get_all_students()
        if not students:
            click.echo('No students found.')
            return
        
        click.echo('\nStudents:')
        click.echo('-' * 80)
        for student in students:
            avg = student.average_grade()
            click.echo(f'ID: {student.id} | Name: {student.name} | Email: {student.email} | Avg: {avg:.2f}')


@cli.command()
@click.option('--student-id', type=int, prompt='Student ID', help='ID of the student')
@click.option('--subject', prompt='Subject', help='Subject name')
@click.option('--score', type=float, prompt='Score', help='Grade score (0-100)')
def add_grade(student_id, subject, score):
    app = create_app('default')
    with app.app_context():
        student = StudentService.get_student_by_id(student_id)
        if not student:
            click.echo('Student not found.', err=True)
            return
        
        try:
            grade = GradeService.create_grade(student_id, subject, score)
            click.echo(f'Grade added: {grade.subject} - {grade.score}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)


@cli.command()
def rankings():
    app = create_app('default')
    with app.app_context():
        rankings = StudentService.get_rankings()
        if not rankings:
            click.echo('No rankings available.')
            return
        
        click.echo('\nStudent Rankings:')
        click.echo('-' * 80)
        for idx, item in enumerate(rankings, 1):
            student = item['student']
            avg = item['average']
            click.echo(f'{idx}. {student.name} - Average: {avg:.2f}')


@cli.command()
@click.option('--output', default='students.csv', help='Output filename')
def export_students(output):
    app = create_app('default')
    with app.app_context():
        try:
            csv_data = ExportService.export_students_to_csv()
            with open(output, 'w') as f:
                f.write(csv_data)
            click.echo(f'Students exported to {output}')
        except Exception as e:
            click.echo(f'Error: {str(e)}', err=True)


if __name__ == '__main__':
    cli()
