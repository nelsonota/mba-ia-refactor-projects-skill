"""Legacy function names delegated to the new persistence layer."""
from src.models.store import (
    create_order as criar_pedido,
    create_product as _create_product,
    create_user as _create_user,
    delete_product as deletar_produto,
    get_product as get_produto_por_id,
    get_user as get_usuario_por_id,
    list_all_orders as get_todos_pedidos,
    list_products as get_todos_produtos,
    list_user_orders as get_pedidos_usuario,
    list_users as get_todos_usuarios,
    login_user as login_usuario,
    sales_report as relatorio_vendas,
    search_products as buscar_produtos,
    update_order_status as atualizar_status_pedido,
    update_product as _update_product,
)


def criar_produto(nome, descricao, preco, estoque, categoria):
    return _create_product({"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria})


def atualizar_produto(produto_id, nome, descricao, preco, estoque, categoria):
    return _update_product(produto_id, {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria})


def criar_usuario(nome, email, senha, tipo="cliente"):
    return _create_user(nome, email, senha)
