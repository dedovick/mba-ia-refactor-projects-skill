from src.config.constants import STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE
from src.database.connection import get_db


class EstoqueInsuficiente(Exception):
    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id


def precos_e_estoques(produto_ids):
    """Mapa produto_id -> {nome, preco, estoque} para os ids informados."""
    ids = sorted(set(produto_ids))
    if not ids:
        return {}
    placeholders = ", ".join("?" for _ in ids)
    rows = get_db().execute(
        f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})", ids
    ).fetchall()
    return {row["id"]: {"nome": row["nome"], "preco": row["preco"], "estoque": row["estoque"]} for row in rows}


def criar(usuario_id, total, itens):
    """Grava pedido, itens e baixa de estoque numa única transação.

    `itens` é uma lista de (produto_id, quantidade, preco_unitario). A baixa só acontece se
    houver estoque; caso contrário a transação inteira é desfeita.
    """
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid
        for produto_id, quantidade, preco_unitario in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, produto_id, quantidade, preco_unitario),
            )
            baixa = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (quantidade, produto_id, quantidade),
            )
            if baixa.rowcount == 0:
                raise EstoqueInsuficiente(produto_id)
    return pedido_id


def listar(usuario_id=None):
    sql = """
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.id AS item_id, i.produto_id, i.quantidade, i.preco_unitario,
               COALESCE(pr.nome, 'Desconhecido') AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
    params = []
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        params.append(usuario_id)
    sql += " ORDER BY p.id, i.id"

    pedidos = {}
    for row in get_db().execute(sql, params).fetchall():
        pedido = pedidos.setdefault(row["id"], {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        })
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"],
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def atualizar_status(pedido_id, status):
    db = get_db()
    with db:
        cursor = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
    return cursor.rowcount > 0


def resumo_vendas():
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = ? THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """,
        (STATUS_PENDENTE, STATUS_APROVADO, STATUS_CANCELADO),
    ).fetchone()
    return dict(row)


def contar():
    return get_db().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
