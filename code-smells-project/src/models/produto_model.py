from src.database.connection import get_db

COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def listar():
    return [dict(row) for row in get_db().execute(f"SELECT {COLUNAS} FROM produtos").fetchall()]


def buscar_por_id(produto_id):
    row = get_db().execute(f"SELECT {COLUNAS} FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return dict(row) if row else None


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    clauses, params = [], []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        params.append(preco_max)
    sql = f"SELECT {COLUNAS} FROM produtos" + (" WHERE " + " AND ".join(clauses) if clauses else "")
    return [dict(row) for row in get_db().execute(sql, params).fetchall()]


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    with db:
        cursor = db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
    return cursor.rowcount > 0


def deletar(produto_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    return cursor.rowcount > 0
