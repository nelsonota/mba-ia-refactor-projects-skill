from flask import Flask
from flask_cors import CORS

from .config.settings import Settings, validate_settings
from .middlewares.error_handler import register_error_handlers
from .models.database import close_db, initialize_database
from .views.routes import api


def create_app(config=None, initialize_db=False):
    app = Flask(__name__)
    app.config.from_object(validate_settings(Settings))
    if config:
        app.config.update(config)
    CORS(app)
    app.register_blueprint(api)
    app.teardown_appcontext(close_db)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db_command():
        """Create tables and seed the sample product catalog when needed."""
        initialize_database()
        print("Database initialized")

    if initialize_db:
        with app.app_context():
            initialize_database()
    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
