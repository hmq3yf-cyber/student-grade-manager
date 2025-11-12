from flask import Flask
from app.config import config
from app.models import db


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    from app.blueprints.students import students_bp
    from app.blueprints.grades import grades_bp
    from app.blueprints.export import export_bp
    
    app.register_blueprint(students_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(export_bp)
    
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    return app
