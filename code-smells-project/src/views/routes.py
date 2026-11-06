import hmac

from flask import Blueprint, current_app, jsonify, request, session

from ..controllers import store_controller as controller


api = Blueprint("api", __name__)


@api.before_app_request
def require_admin_for_sensitive_routes():
    protected_endpoints = {
        "listar_usuarios", "buscar_usuario", "listar_todos_pedidos",
        "atualizar_status_pedido", "relatorio_vendas", "reset_database", "execute_query",
        "criar_produto", "atualizar_produto", "deletar_produto",
    }
    configured_token = current_app.config.get("ADMIN_TOKEN")
    provided = request.headers.get("X-Admin-Token", "")
    valid_admin = bool(configured_token) and hmac.compare_digest(
        provided.encode("utf-8"), configured_token.encode("utf-8")
    )
    if request.endpoint in {f"api.{name}" for name in protected_endpoints}:
        if not configured_token:
            return jsonify({"erro": "Acesso administrativo indisponível"}), 503
        if not valid_admin:
            return jsonify({"erro": "Não autorizado"}), 401
        return None

    if request.endpoint in {"api.criar_pedido", "api.listar_pedidos_usuario"}:
        if valid_admin:
            return None
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"erro": "Autenticação necessária"}), 401
        if request.endpoint == "api.listar_pedidos_usuario" and request.view_args.get("usuario_id") != user_id:
            return jsonify({"erro": "Acesso negado"}), 403
    return None


@api.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja", "versao": "1.0.0",
        "endpoints": {"produtos": "/produtos", "usuarios": "/usuarios", "pedidos": "/pedidos",
                      "login": "/login", "relatorios": "/relatorios/vendas", "health": "/health"},
    })


api.add_url_rule("/produtos", "listar_produtos", controller.listar_produtos, methods=["GET"])
api.add_url_rule("/produtos/busca", "buscar_produtos", controller.buscar_produtos, methods=["GET"])
api.add_url_rule("/produtos/<int:produto_id>", "buscar_produto", controller.buscar_produto, methods=["GET"])
api.add_url_rule("/produtos", "criar_produto", controller.criar_produto, methods=["POST"])
api.add_url_rule("/produtos/<int:produto_id>", "atualizar_produto", controller.atualizar_produto, methods=["PUT"])
api.add_url_rule("/produtos/<int:produto_id>", "deletar_produto", controller.deletar_produto, methods=["DELETE"])
api.add_url_rule("/usuarios", "listar_usuarios", controller.listar_usuarios, methods=["GET"])
api.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", controller.buscar_usuario, methods=["GET"])
api.add_url_rule("/usuarios", "criar_usuario", controller.criar_usuario, methods=["POST"])
api.add_url_rule("/login", "login", controller.login, methods=["POST"])
api.add_url_rule("/pedidos", "criar_pedido", controller.criar_pedido, methods=["POST"])
api.add_url_rule("/pedidos", "listar_todos_pedidos", controller.listar_todos_pedidos, methods=["GET"])
api.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", controller.listar_pedidos_usuario, methods=["GET"])
api.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", controller.atualizar_status_pedido, methods=["PUT"])
api.add_url_rule("/relatorios/vendas", "relatorio_vendas", controller.relatorio_vendas, methods=["GET"])
api.add_url_rule("/health", "health_check", controller.health_check, methods=["GET"])
api.add_url_rule("/admin/reset-db", "reset_database", controller.reset_database, methods=["POST"])
api.add_url_rule("/admin/query", "execute_query", controller.execute_query, methods=["POST"])
