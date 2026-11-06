from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({"erro": "Requisição inválida"}), 400

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        app.logger.exception("Unhandled request error")
        return jsonify({"erro": "Erro interno"}), 500
