from src.database.connection import get_db
from src.models.constants import STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE


class EstoqueInsuficiente(Exception):
    def __init__(self, produto_id):
        super().__init__(produto_id)
        self.produto_id = produto_id


def criar(usuario_id, total, itens):
    """Grava pedido, itens e baixa de estoque numa única transação.

    `itens` é uma lista de dicts com produto_id, quantidade e preco_unitario.
    A baixa só acontece se ainda houver estoque; caso contrário tudo é desfeito.
    """
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, STATUS_PENDENTE, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            baixa = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if baixa.rowcount == 0:
                raise EstoqueInsuficiente(item["produto_id"])
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
    params = ()
    if usuario_id is not None:
        sql += " WHERE p.usuario_id = ?"
        params = (usuario_id,)
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


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    with db:
        cursor = db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
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
