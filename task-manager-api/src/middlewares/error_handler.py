from flask import current_app
from werkzeug.exceptions import HTTPException, InternalServerError


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        current_app.logger.exception("Unhandled application error", exc_info=error)
        return InternalServerError().get_response()
