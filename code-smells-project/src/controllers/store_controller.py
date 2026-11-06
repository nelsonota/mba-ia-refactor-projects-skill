import logging
import hmac

from flask import current_app, jsonify, request, session

from ..models import database, store
from ..services import validate_order, validate_product

logger = logging.getLogger(__name__)


def _failure(error, status=400):
    return jsonify({"erro": error}), status


def _server_error():
    logger.exception("Request failed")
    return _failure("Erro interno", 500)


def _json_object():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def listar_produtos():
    try:
        return jsonify({"dados": store.list_products(), "sucesso": True}), 200
    except Exception:
        return _server_error()


def buscar_produto(produto_id):
    try:
        product = store.get_product(produto_id)
        return (jsonify({"dados": product, "sucesso": True}), 200) if product else _failure("Produto não encontrado", 404)
    except Exception:
        return _server_error()


def criar_produto():
    payload = _json_object()
    error = validate_product(payload)
    if error:
        return _failure(error)
    try:
        product_id = store.create_product(payload)
        return jsonify({"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}), 201
    except Exception:
        return _server_error()


def atualizar_produto(produto_id):
    payload = _json_object()
    error = validate_product(payload)
    if error:
        return _failure(error)
    try:
        if not store.get_product(produto_id):
            return _failure("Produto não encontrado", 404)
        store.update_product(produto_id, payload)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except Exception:
        return _server_error()


def deletar_produto(produto_id):
    try:
        if not store.get_product(produto_id):
            return _failure("Produto não encontrado", 404)
        store.delete_product(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except Exception:
        return _server_error()


def buscar_produtos():
    try:
        minimum = request.args.get("preco_min")
        maximum = request.args.get("preco_max")
        results = store.search_products(
            request.args.get("q", ""), request.args.get("categoria"),
            float(minimum) if minimum is not None else None,
            float(maximum) if maximum is not None else None,
        )
        return jsonify({"dados": results, "total": len(results), "sucesso": True}), 200
    except (TypeError, ValueError):
        return _failure("Faixa de preço inválida")
    except Exception:
        return _server_error()


def listar_usuarios():
    try:
        return jsonify({"dados": store.list_users(), "sucesso": True}), 200
    except Exception:
        return _server_error()


def buscar_usuario(usuario_id):
    try:
        user = store.get_user(usuario_id)
        return (jsonify({"dados": user, "sucesso": True}), 200) if user else _failure("Usuário não encontrado", 404)
    except Exception:
        return _server_error()


def criar_usuario():
    payload = _json_object()
    if not payload or not all(isinstance(payload.get(field), str) and payload[field] for field in ("nome", "email", "senha")):
        return _failure("Nome, email e senha são obrigatórios")
    try:
        user_id = store.create_user(payload["nome"], payload["email"], payload["senha"])
        return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201
    except Exception:
        return _server_error()


def login():
    payload = _json_object()
    if not payload or not payload.get("email") or not payload.get("senha"):
        return _failure("Email e senha são obrigatórios")
    try:
        user = store.login_user(payload["email"], payload["senha"])
        if not user:
            session.clear()
            return _failure("Email ou senha inválidos", 401)
        session.clear()
        session["user_id"] = user["id"]
        session["user_type"] = user["tipo"]
        return jsonify({"dados": user, "sucesso": True, "mensagem": "Login OK"}), 200
    except Exception:
        return _server_error()


def criar_pedido():
    payload = _json_object()
    error = validate_order(payload)
    if error:
        return _failure(error)
    configured_token = current_app.config.get("ADMIN_TOKEN")
    provided_token = request.headers.get("X-Admin-Token", "")
    is_admin = bool(configured_token) and hmac.compare_digest(
        provided_token.encode("utf-8"), configured_token.encode("utf-8")
    )
    if session.get("user_id") is not None and session["user_id"] != payload["usuario_id"] and not is_admin:
        return _failure("Acesso negado", 403)
    if session.get("user_id") is None and not is_admin:
        return _failure("Autenticação necessária", 401)
    try:
        result = store.create_order(payload["usuario_id"], payload["itens"])
        if "erro" in result:
            return _failure(result["erro"])
        return jsonify({"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except Exception:
        return _server_error()


def listar_pedidos_usuario(usuario_id):
    try:
        return jsonify({"dados": store.list_user_orders(usuario_id), "sucesso": True}), 200
    except Exception:
        return _server_error()


def listar_todos_pedidos():
    try:
        return jsonify({"dados": store.list_all_orders(), "sucesso": True}), 200
    except Exception:
        return _server_error()


def atualizar_status_pedido(pedido_id):
    payload = _json_object()
    status = payload.get("status") if payload else None
    if status not in store.ORDER_STATUSES:
        return _failure("Status inválido")
    try:
        store.update_order_status(pedido_id, status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception:
        return _server_error()


def relatorio_vendas():
    try:
        return jsonify({"dados": store.sales_report(), "sucesso": True}), 200
    except Exception:
        return _server_error()


def health_check():
    try:
        return jsonify(store.run_health_check()), 200
    except Exception:
        return jsonify({"status": "erro", "detalhes": "Serviço indisponível"}), 500


def reset_database():
    try:
        store.reset_store()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
    except Exception:
        return _server_error()


def execute_query():
    current_app.logger.warning("Arbitrary SQL endpoint is disabled")
    return _failure("Endpoint desativado", 410)
