from datetime import datetime

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.database import db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import report_bp, task_bp, user_bp


def create_app(config=None, *, create_tables=True):
    app = Flask(__name__)
    app.config.from_object(Settings)
    if config:
        app.config.update(config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    register_error_handlers(app)
    if create_tables:
        with app.app_context():
            db.create_all()
    return app
