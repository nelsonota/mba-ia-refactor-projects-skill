from flask import Flask
from flask_cors import CORS
from database import db
from src.config.settings import Settings
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import register_routes
from src.services.clock import utc_now


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Settings)
    if config_overrides:
        app.config.update(config_overrides)
    CORS(app)
    db.init_app(app)
    register_routes(app)
    @app.get('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(utc_now())}

    @app.get('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    register_error_handlers(app)

    with app.app_context():
        db.create_all()
    return app


