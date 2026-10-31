import secrets

from flask import Blueprint, current_app, jsonify, request


def _admin_authorized():
    configured_token = current_app.config.get("ADMIN_TOKEN")
    supplied_token = request.headers.get("Authorization", "")
    expected_header = f"Bearer {configured_token}" if configured_token else ""
    return bool(configured_token) and secrets.compare_digest(supplied_token, expected_header)


def create_routes(controller, get_db):
    routes = Blueprint("api", __name__)

    routes.add_url_rule("/", "index", lambda: jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos", "usuarios": "/usuarios",
            "pedidos": "/pedidos", "login": "/login",
            "relatorios": "/relatorios/vendas", "health": "/health",
        },
    }), methods=["GET"])

    endpoint_map = [
        ("/produtos", "listar_produtos", controller.listar_produtos, ["GET"]),
        ("/produtos/busca", "buscar_produtos", controller.buscar_produtos, ["GET"]),
        ("/produtos/<int:id>", "buscar_produto", controller.buscar_produto, ["GET"]),
        ("/produtos", "criar_produto", controller.criar_produto, ["POST"]),
        ("/produtos/<int:id>", "atualizar_produto", controller.atualizar_produto, ["PUT"]),
        ("/produtos/<int:id>", "deletar_produto", controller.deletar_produto, ["DELETE"]),
        ("/usuarios", "listar_usuarios", controller.listar_usuarios, ["GET"]),
        ("/usuarios/<int:id>", "buscar_usuario", controller.buscar_usuario, ["GET"]),
        ("/usuarios", "criar_usuario", controller.criar_usuario, ["POST"]),
        ("/login", "login", controller.login, ["POST"]),
        ("/pedidos", "criar_pedido", controller.criar_pedido, ["POST"]),
        ("/pedidos", "listar_todos_pedidos", controller.listar_todos_pedidos, ["GET"]),
        ("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", controller.listar_pedidos_usuario, ["GET"]),
        ("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", controller.atualizar_status_pedido, ["PUT"]),
        ("/relatorios/vendas", "relatorio_vendas", controller.relatorio_vendas, ["GET"]),
        ("/health", "health_check", controller.health_check, ["GET"]),
    ]
    for rule, name, view, methods in endpoint_map:
        routes.add_url_rule(rule, name, view, methods=methods)

    @routes.route("/admin/reset-db", methods=["POST"])
    def reset_database():
        if not _admin_authorized():
            return jsonify({"erro": "Não autorizado"}), 401
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        print("!!! BANCO DE DADOS RESETADO !!!")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    return routes
