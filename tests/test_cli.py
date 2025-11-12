import pytest
import os
import tempfile
from click.testing import CliRunner
from cli.commands import cli
from app import create_app
from app.models import db, Student, Grade


@pytest.fixture
def temp_db():
    """Create a temporary database for CLI testing."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def app_with_temp_db(temp_db):
    """Create an app instance with temporary database."""
    os.environ['DATABASE_URL'] = f'sqlite:///{temp_db}'
    app = create_app('default')
    with app.app_context():
        db.create_all()
    return app


class TestAddStudent:
    def test_add_student_success(self, cli_runner, temp_db):
        """Test adding a student successfully."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        
        assert result.exit_code == 0
        assert 'Student created successfully' in result.output
        assert 'John Doe' in result.output
        assert 'john@example.com' in result.output
    
    def test_add_student_duplicate_email(self, cli_runner, temp_db):
        """Test adding a student with duplicate email."""
        # Add first student
        result1 = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        assert result1.exit_code == 0
        
        # Try to add another with same email
        result2 = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Jane Doe',
            '--email', 'john@example.com'
        ])
        assert result2.exit_code == 1
        assert 'already registered' in result2.output
    
    def test_add_student_empty_name(self, cli_runner, temp_db):
        """Test adding a student with empty name."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', '',
            '--email', 'test@example.com'
        ])
        assert result.exit_code == 1
        assert 'cannot be empty' in result.output


class TestEditStudent:
    def test_edit_student_success(self, cli_runner, temp_db):
        """Test editing a student successfully."""
        # Add a student first
        add_result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        assert add_result.exit_code == 0
        
        # Edit the student
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-student',
            '--student-id', '1',
            '--name', 'John Updated'
        ])
        assert result.exit_code == 0
        assert 'Student updated successfully' in result.output
        assert 'John Updated' in result.output
    
    def test_edit_student_not_found(self, cli_runner, temp_db):
        """Test editing a non-existent student."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-student',
            '--student-id', '999',
            '--name', 'John'
        ])
        assert result.exit_code == 1
        assert 'not found' in result.output
    
    def test_edit_student_duplicate_email(self, cli_runner, temp_db):
        """Test editing student with duplicate email."""
        # Add two students
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Jane Doe',
            '--email', 'jane@example.com'
        ])
        
        # Try to edit first student to have second's email
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-student',
            '--student-id', '1',
            '--email', 'jane@example.com'
        ])
        assert result.exit_code == 1
        assert 'already registered' in result.output


class TestDeleteStudent:
    def test_delete_student_with_confirm_flag(self, cli_runner, temp_db):
        """Test deleting a student with --confirm flag."""
        # Add a student
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        
        # Delete with confirm flag
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'delete-student',
            '--student-id', '1',
            '--confirm'
        ])
        assert result.exit_code == 0
        assert 'deleted successfully' in result.output
    
    def test_delete_student_not_found(self, cli_runner, temp_db):
        """Test deleting a non-existent student."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'delete-student',
            '--student-id', '999',
            '--confirm'
        ])
        assert result.exit_code == 1
        assert 'not found' in result.output
    
    def test_delete_student_with_grades(self, cli_runner, temp_db):
        """Test deleting a student with grades."""
        # Add student
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        
        # Add a grade
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        # Delete student
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'delete-student',
            '--student-id', '1',
            '--confirm'
        ])
        assert result.exit_code == 0
        assert 'deleted successfully' in result.output
        assert 'grade' in result.output


class TestListStudents:
    def test_list_students_empty(self, cli_runner, temp_db):
        """Test listing students when there are none."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-students'
        ])
        assert result.exit_code == 0
        assert 'No students found' in result.output
    
    def test_list_students_with_data(self, cli_runner, temp_db):
        """Test listing students with data."""
        # Add students
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Alice Smith',
            '--email', 'alice@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Bob Johnson',
            '--email', 'bob@example.com'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-students'
        ])
        assert result.exit_code == 0
        assert 'Alice Smith' in result.output
        assert 'Bob Johnson' in result.output
        assert 'alice@example.com' in result.output
    
    def test_list_students_with_average(self, cli_runner, temp_db):
        """Test that average grades are displayed."""
        # Add student with grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '90'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'English',
            '--score', '80'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-students'
        ])
        assert result.exit_code == 0
        assert '85' in result.output
        assert '2' in result.output


class TestAddGrade:
    def test_add_grade_success(self, cli_runner, temp_db):
        """Test adding a grade successfully."""
        # Add student first
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        assert result.exit_code == 0
        assert 'Grade added successfully' in result.output
        assert 'Math' in result.output
        assert '85' in result.output
    
    def test_add_grade_invalid_score(self, cli_runner, temp_db):
        """Test adding a grade with invalid score."""
        # Add student first
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        
        # Try with score > 100
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '150'
        ])
        assert result.exit_code == 1
        assert 'between 0 and 100' in result.output
    
    def test_add_grade_student_not_found(self, cli_runner, temp_db):
        """Test adding a grade for non-existent student."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '999',
            '--subject', 'Math',
            '--score', '85'
        ])
        assert result.exit_code == 1
        assert 'not found' in result.output


class TestEditGrade:
    def test_edit_grade_success(self, cli_runner, temp_db):
        """Test editing a grade successfully."""
        # Add student and grade
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-grade',
            '--grade-id', '1',
            '--score', '95'
        ])
        assert result.exit_code == 0
        assert 'Grade updated successfully' in result.output
        assert '95' in result.output
    
    def test_edit_grade_not_found(self, cli_runner, temp_db):
        """Test editing a non-existent grade."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-grade',
            '--grade-id', '999',
            '--score', '85'
        ])
        assert result.exit_code == 1
        assert 'not found' in result.output
    
    def test_edit_grade_invalid_score(self, cli_runner, temp_db):
        """Test editing a grade with invalid score."""
        # Add student and grade
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'edit-grade',
            '--grade-id', '1',
            '--score', '-10'
        ])
        assert result.exit_code == 1
        assert 'between 0 and 100' in result.output


class TestDeleteGrade:
    def test_delete_grade_with_confirm(self, cli_runner, temp_db):
        """Test deleting a grade with --confirm flag."""
        # Add student and grade
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'delete-grade',
            '--grade-id', '1',
            '--confirm'
        ])
        assert result.exit_code == 0
        assert 'deleted successfully' in result.output
    
    def test_delete_grade_not_found(self, cli_runner, temp_db):
        """Test deleting a non-existent grade."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'delete-grade',
            '--grade-id', '999',
            '--confirm'
        ])
        assert result.exit_code == 1
        assert 'not found' in result.output


class TestListGrades:
    def test_list_grades_empty(self, cli_runner, temp_db):
        """Test listing grades when there are none."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-grades'
        ])
        assert result.exit_code == 0
        assert 'No grades found' in result.output
    
    def test_list_grades_all(self, cli_runner, temp_db):
        """Test listing all grades."""
        # Add students with grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Jane Doe',
            '--email', 'jane@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '2',
            '--subject', 'English',
            '--score', '90'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-grades'
        ])
        assert result.exit_code == 0
        assert 'Math' in result.output
        assert 'English' in result.output
        assert 'John Doe' in result.output
        assert 'Jane Doe' in result.output
    
    def test_list_grades_by_student(self, cli_runner, temp_db):
        """Test listing grades for a specific student."""
        # Add students with grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Jane Doe',
            '--email', 'jane@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '2',
            '--subject', 'English',
            '--score', '90'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'list-grades',
            '--student-id', '1'
        ])
        assert result.exit_code == 0
        assert 'Grades for John Doe' in result.output
        assert 'Math' in result.output
        assert 'English' not in result.output


class TestRankings:
    def test_rankings_empty(self, cli_runner, temp_db):
        """Test rankings with no students."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'rankings'
        ])
        assert result.exit_code == 0
        assert 'No rankings available' in result.output
    
    def test_rankings_with_data(self, cli_runner, temp_db):
        """Test rankings with students and grades."""
        # Add students
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Alice Smith',
            '--email', 'alice@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Bob Johnson',
            '--email', 'bob@example.com'
        ])
        
        # Add grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '95'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'English',
            '--score', '90'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '2',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'rankings'
        ])
        assert result.exit_code == 0
        assert 'Rankings' in result.output
        assert 'Alice Smith' in result.output
        assert 'Bob Johnson' in result.output
        # Alice should be ranked higher (average 92.5 vs 85)


class TestExportStudents:
    def test_export_students_success(self, cli_runner, temp_db):
        """Test exporting students to CSV."""
        # Add students
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'Jane Doe',
            '--email', 'jane@example.com'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'export-students',
            '--output', 'test_students.csv'
        ])
        assert result.exit_code == 0
        assert 'exported successfully' in result.output
        
        # Verify file was created
        assert os.path.exists('test_students.csv')
        
        # Clean up
        os.remove('test_students.csv')
    
    def test_export_students_with_grades(self, cli_runner, temp_db):
        """Test exporting students with grades data."""
        # Add student with grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'export-students',
            '--output', 'test_students.csv'
        ])
        assert result.exit_code == 0
        
        # Read and verify content
        with open('test_students.csv', 'r') as f:
            content = f.read()
            assert 'John Doe' in content
            assert '85' in content
        
        # Clean up
        os.remove('test_students.csv')


class TestExportGrades:
    def test_export_grades_success(self, cli_runner, temp_db):
        """Test exporting grades to CSV."""
        # Add student and grades
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-grade',
            '--student-id', '1',
            '--subject', 'Math',
            '--score', '85'
        ])
        
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'export-grades',
            '--output', 'test_grades.csv'
        ])
        assert result.exit_code == 0
        assert 'exported successfully' in result.output
        
        # Verify file was created
        assert os.path.exists('test_grades.csv')
        
        # Read and verify content
        with open('test_grades.csv', 'r') as f:
            content = f.read()
            assert 'Math' in content
            assert 'John Doe' in content
            assert '85' in content
        
        # Clean up
        os.remove('test_grades.csv')


class TestDatabaseFlag:
    def test_cli_with_custom_db_path(self, cli_runner):
        """Test CLI with custom database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_db = os.path.join(tmpdir, 'custom.db')
            
            result = cli_runner.invoke(cli, [
                '--db', custom_db,
                'add-student',
                '--name', 'John Doe',
                '--email', 'john@example.com'
            ])
            
            assert result.exit_code == 0
            assert 'Student created successfully' in result.output
            assert os.path.exists(custom_db)


class TestExitCodes:
    def test_success_exit_code(self, cli_runner, temp_db):
        """Test that successful commands have exit code 0."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', 'John Doe',
            '--email', 'john@example.com'
        ])
        assert result.exit_code == 0
    
    def test_error_exit_code(self, cli_runner, temp_db):
        """Test that failed commands have exit code 1."""
        result = cli_runner.invoke(cli, [
            '--db', temp_db,
            'add-student',
            '--name', '',
            '--email', 'test@example.com'
        ])
        assert result.exit_code == 1
