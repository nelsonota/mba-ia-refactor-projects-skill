from .models import store


def validate_product(payload):
    if not isinstance(payload, dict):
        return "Dados inválidos"
    for field in ("nome", "preco", "estoque"):
        if field not in payload:
            return {"nome": "Nome é obrigatório", "preco": "Preço é obrigatório", "estoque": "Estoque é obrigatório"}[field]
    if not isinstance(payload["nome"], str) or not 2 <= len(payload["nome"]) <= 200:
        return "Nome inválido"
    if not isinstance(payload["preco"], (int, float)) or payload["preco"] < 0:
        return "Preço inválido"
    if not isinstance(payload["estoque"], int) or payload["estoque"] < 0:
        return "Estoque inválido"
    if payload.get("categoria", "geral") not in store.VALID_CATEGORIES:
        return "Categoria inválida"
    return None


def validate_order(payload):
    if not isinstance(payload, dict):
        return "Dados inválidos"
    if not isinstance(payload.get("usuario_id"), int) or payload["usuario_id"] <= 0:
        return "Usuario ID é obrigatório"
    items = payload.get("itens")
    if not isinstance(items, list) or not items:
        return "Pedido deve ter pelo menos 1 item"
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("produto_id"), int) or not isinstance(item.get("quantidade"), int) or item["quantidade"] <= 0:
            return "Item de pedido inválido"
    return None
