from flask import jsonify, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register a fallback JSON error response for uncaught application errors."""

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error", exc_info=error)
        if request.endpoint == "api.health_check":
            return jsonify({"status": "erro", "detalhes": str(error)}), 500
        return jsonify({"erro": str(error)}), 500

    @app.errorhandler(HTTPException)
    def preserve_http_error(error):
        return error
