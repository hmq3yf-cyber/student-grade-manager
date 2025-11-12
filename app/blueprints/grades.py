from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app.services import GradeService, StudentService

grades_bp = Blueprint('grades', __name__, url_prefix='/grades')


class GradeForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Submit')


@grades_bp.route('/student/<int:student_id>')
def list_grades(student_id):
    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.list_students'))
    
    grades = GradeService.get_grades_by_student(student_id)
    return render_template('grades/list.html', student=student, grades=grades)


@grades_bp.route('/student/<int:student_id>/add', methods=['GET', 'POST'])
def add_grade(student_id):
    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('students.list_students'))
    
    form = GradeForm()
    form.student_id.choices = [(student.id, student.name)]
    form.student_id.data = student.id
    
    if form.validate_on_submit():
        try:
            GradeService.create_grade(student_id, form.subject.data, form.score.data)
            flash('Grade added successfully!', 'success')
            return redirect(url_for('grades.list_grades', student_id=student_id))
        except Exception as e:
            flash(f'Error adding grade: {str(e)}', 'danger')
    
    return render_template('grades/add.html', form=form, student=student)


@grades_bp.route('/<int:grade_id>/edit', methods=['GET', 'POST'])
def edit_grade(grade_id):
    grade = GradeService.get_grade_by_id(grade_id)
    if not grade:
        flash('Grade not found.', 'danger')
        return redirect(url_for('students.list_students'))
    
    form = GradeForm(obj=grade)
    form.student_id.choices = [(grade.student.id, grade.student.name)]
    
    if form.validate_on_submit():
        try:
            GradeService.update_grade(grade_id, form.subject.data, form.score.data)
            flash('Grade updated successfully!', 'success')
            return redirect(url_for('grades.list_grades', student_id=grade.student_id))
        except Exception as e:
            flash(f'Error updating grade: {str(e)}', 'danger')
    
    return render_template('grades/edit.html', form=form, grade=grade)


@grades_bp.route('/<int:grade_id>/delete', methods=['POST'])
def delete_grade(grade_id):
    grade = GradeService.get_grade_by_id(grade_id)
    if grade:
        student_id = grade.student_id
        if GradeService.delete_grade(grade_id):
            flash('Grade deleted successfully!', 'success')
        return redirect(url_for('grades.list_grades', student_id=student_id))
    else:
        flash('Grade not found.', 'danger')
        return redirect(url_for('students.list_students'))
