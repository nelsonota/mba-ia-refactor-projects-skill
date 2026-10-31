from flask import Flask
from flask_cors import CORS

from src.config.settings import load_settings
from src.controllers import api_controller
from src.middlewares.error_handler import register_error_handlers
from src.models.database import close_db, get_db, configure_database
from src.views.routes import create_routes


def create_app(settings=None):
    app = Flask(__name__)
    app.config.update(load_settings())
    if settings:
        app.config.update(settings)
    configure_database(app.config["DATABASE_PATH"])
    CORS(app)
    app.register_blueprint(create_routes(api_controller, get_db))
    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
