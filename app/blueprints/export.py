from flask import Blueprint, Response, flash, redirect, url_for
from app.services import ExportService

export_bp = Blueprint('export', __name__, url_prefix='/export')


@export_bp.route('/students')
def export_students():
    try:
        csv_data = ExportService.export_students_to_csv()
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=students.csv'}
        )
    except Exception as e:
        flash(f'Error exporting students: {str(e)}', 'danger')
        return redirect(url_for('students.list_students'))


@export_bp.route('/grades')
def export_grades():
    try:
        csv_data = ExportService.export_grades_to_csv()
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=grades.csv'}
        )
    except Exception as e:
        flash(f'Error exporting grades: {str(e)}', 'danger')
        return redirect(url_for('students.list_students'))
