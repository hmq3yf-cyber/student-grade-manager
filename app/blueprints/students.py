from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from app.services import StudentService
from app.models import Student

students_bp = Blueprint('students', __name__, url_prefix='/students')


class StudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')
    
    def __init__(self, student_id=None, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.student_id = student_id
    
    def validate_email(self, field):
        existing = Student.query.filter_by(email=field.data).first()
        if existing and (self.student_id is None or existing.id != self.student_id):
            raise ValidationError('Email already registered.')


@students_bp.route('/')
def list_students():
    students = StudentService.get_all_students()
    return render_template('students/list.html', students=students)


@students_bp.route('/create', methods=['GET', 'POST'])
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        try:
            StudentService.create_student(form.name.data, form.email.data)
            flash('Student created successfully!', 'success')
            return redirect(url_for('students.list_students'))
        except Exception as e:
            flash(f'Error creating student: {str(e)}', 'danger')
    return render_template('students/create.html', form=form)


@students_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.list_students'))
    
    form = StudentForm(student_id=student_id, obj=student)
    if form.validate_on_submit():
        try:
            StudentService.update_student(student_id, form.name.data, form.email.data)
            flash('Student updated successfully!', 'success')
            return redirect(url_for('students.list_students'))
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'danger')
    
    return render_template('students/edit.html', form=form, student=student)


@students_bp.route('/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    if StudentService.delete_student(student_id):
        flash('Student deleted successfully!', 'success')
    else:
        flash('Student not found.', 'danger')
    return redirect(url_for('students.list_students'))


@students_bp.route('/rankings')
def rankings():
    rankings = StudentService.get_rankings()
    return render_template('students/rankings.html', rankings=rankings)
