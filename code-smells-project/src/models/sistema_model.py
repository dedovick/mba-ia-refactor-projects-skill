from src.database.connection import get_db, get_read_only_db

TABELAS_RESET = ("itens_pedido", "pedidos", "produtos", "usuarios")


def contar_registros():
    row = get_db().execute(
        """
        SELECT (SELECT COUNT(*) FROM produtos) AS produtos,
               (SELECT COUNT(*) FROM usuarios) AS usuarios,
               (SELECT COUNT(*) FROM pedidos) AS pedidos
        """
    ).fetchone()
    return dict(row)


def resetar_banco():
    db = get_db()
    with db:
        for tabela in TABELAS_RESET:
            db.execute(f"DELETE FROM {tabela}")


def executar_consulta_leitura(sql):
    """Executa uma consulta numa conexão somente leitura: escrita é recusada pelo SQLite."""
    return [dict(row) for row in get_read_only_db().execute(sql).fetchall()]
