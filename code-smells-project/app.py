"""Backward-compatible entry point; the composition root lives in src.app."""

from src.app import app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
