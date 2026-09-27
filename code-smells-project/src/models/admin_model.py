from src.database.connection import get_db, get_read_only_db

TABELAS_EM_ORDEM_DE_REMOCAO = ("itens_pedido", "pedidos", "produtos", "usuarios")


def apagar_tudo():
    db = get_db()
    with db:
        for tabela in TABELAS_EM_ORDEM_DE_REMOCAO:
            db.execute(f"DELETE FROM {tabela}")


def consultar(sql):
    """Executa uma consulta numa conexão somente leitura: escritas falham no próprio SQLite."""
    rows = get_read_only_db().execute(sql).fetchall()
    return [dict(row) for row in rows]
