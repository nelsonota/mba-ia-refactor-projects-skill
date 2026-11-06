from werkzeug.security import check_password_hash, generate_password_hash

from .database import get_db

VALID_CATEGORIES = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
ORDER_STATUSES = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))


def _dict_rows(rows):
    return [dict(row) for row in rows]


def list_products():
    return _dict_rows(get_db().execute("SELECT * FROM produtos").fetchall())


def get_product(product_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
    return dict(row) if row else None


def search_products(term="", category=None, min_price=None, max_price=None):
    clauses, params = [], []
    if term:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend((f"%{term}%", f"%{term}%"))
    if category:
        clauses.append("categoria = ?")
        params.append(category)
    if min_price is not None:
        clauses.append("preco >= ?")
        params.append(min_price)
    if max_price is not None:
        clauses.append("preco <= ?")
        params.append(max_price)
    query = "SELECT * FROM produtos" + (" WHERE " + " AND ".join(clauses) if clauses else "")
    return _dict_rows(get_db().execute(query, params).fetchall())


def create_product(data):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (data["nome"], data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral")),
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, data):
    db = get_db()
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (data["nome"], data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral"), product_id),
    )
    db.commit()


def delete_product(product_id):
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()


def list_users():
    return _dict_rows(get_db().execute("SELECT id, nome, email, tipo, criado_em FROM usuarios").fetchall())


def get_user(user_id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def create_user(name, email, password):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
        (name, email, generate_password_hash(password)),
    )
    db.commit()
    return cursor.lastrowid


def login_user(email, password):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if not row:
        return None
    stored_password = row["senha"]
    try:
        valid = check_password_hash(stored_password, password)
    except (ValueError, TypeError):
        valid = False
    if not valid and stored_password == password:
        db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (generate_password_hash(password), row["id"]))
        db.commit()
        valid = True
    if not valid:
        return None
    return {key: row[key] for key in ("id", "nome", "email", "tipo")}


def create_order(user_id, items):
    db = get_db()
    try:
        with db:
            total = 0
            normalized = []
            for item in items:
                product_id, quantity = item["produto_id"], item["quantidade"]
                product = db.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (product_id,)).fetchone()
                if product is None:
                    return {"erro": f"Produto {product_id} não encontrado"}
                if product["estoque"] < quantity:
                    return {"erro": f"Estoque insuficiente para {product['nome']}"}
                normalized.append((product_id, quantity, product["preco"]))
                total += product["preco"] * quantity
            cursor = db.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)", (user_id, "pendente", total))
            order_id = cursor.lastrowid
            for product_id, quantity, price in normalized:
                changed = db.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (quantity, product_id, quantity),
                ).rowcount
                if changed != 1:
                    raise ValueError("Estoque insuficiente")
                db.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, quantity, price),
                )
        return {"pedido_id": order_id, "total": total}
    except ValueError as error:
        return {"erro": str(error)}


def _orders(where="", params=()):
    db = get_db()
    orders = _dict_rows(db.execute("SELECT * FROM pedidos" + where, params).fetchall())
    if not orders:
        return orders
    order_ids = [order["id"] for order in orders]
    marks = ",".join("?" for _ in order_ids)
    items = db.execute(
        f"SELECT i.pedido_id, i.produto_id, p.nome AS produto_nome, i.quantidade, i.preco_unitario "
        f"FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id WHERE i.pedido_id IN ({marks})",
        order_ids,
    ).fetchall()
    by_order = {order_id: [] for order_id in order_ids}
    for item in items:
        by_order[item["pedido_id"]].append({
            "produto_id": item["produto_id"], "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"], "preco_unitario": item["preco_unitario"],
        })
    for order in orders:
        order["itens"] = by_order[order["id"]]
    return orders


def list_user_orders(user_id):
    return _orders(" WHERE usuario_id = ?", (user_id,))


def list_all_orders():
    return _orders()


def update_order_status(order_id, status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, order_id))
    db.commit()
    return True


def sales_report():
    db = get_db()
    total_orders, revenue = db.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM pedidos").fetchone()
    pending, approved, cancelled = db.execute(
        "SELECT SUM(status = ?), SUM(status = ?), SUM(status = ?) FROM pedidos",
        ("pendente", "aprovado", "cancelado"),
    ).fetchone()
    discount = next((revenue * rate for threshold, rate in DISCOUNT_TIERS if revenue > threshold), 0)
    return {
        "total_pedidos": total_orders, "faturamento_bruto": round(revenue, 2),
        "desconto_aplicavel": round(discount, 2), "faturamento_liquido": round(revenue - discount, 2),
        "pedidos_pendentes": pending or 0, "pedidos_aprovados": approved or 0,
        "pedidos_cancelados": cancelled or 0,
        "ticket_medio": round(revenue / total_orders, 2) if total_orders else 0,
    }


def reset_store():
    db = get_db()
    with db:
        db.execute("DELETE FROM itens_pedido")
        db.execute("DELETE FROM pedidos")
        db.execute("DELETE FROM produtos")
        db.execute("DELETE FROM usuarios")


def run_health_check():
    db = get_db()
    counts = {}
    for table, key in (("produtos", "produtos"), ("usuarios", "usuarios"), ("pedidos", "pedidos")):
        counts[key] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return {"status": "ok", "database": "connected", "counts": counts, "versao": "1.0.0", "ambiente": "producao"}
