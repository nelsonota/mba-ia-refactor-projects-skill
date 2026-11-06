"""Compatibility entry point; implementation lives in src.app."""
from src.app import app
from src.models.database import initialize_database


if __name__ == "__main__":
    with app.app_context():
        initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
