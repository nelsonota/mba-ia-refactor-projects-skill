from flask import jsonify
from werkzeug.exceptions import HTTPException
from src.views.validation import InvalidRequestData
from src.errors import ServiceOperationError
from database import db


def register_error_handlers(app):
    @app.errorhandler(InvalidRequestData)
    def handle_invalid_request_data(_error):
        return jsonify({'error': 'Dados inválidos'}), 400

    @app.errorhandler(ServiceOperationError)
    def handle_service_operation_error(error):
        db.session.rollback()
        return jsonify({'error': str(error)}), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception('Unhandled request error')
        db.session.rollback()
        return jsonify({'error': 'Erro interno'}), 500
