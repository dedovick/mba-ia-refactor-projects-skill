from src.database.connection import get_db
from src.models.constants import TIPO_USUARIO_PADRAO

COLUNAS = "id, nome, email, senha, tipo, criado_em"


def listar():
    return [dict(row) for row in get_db().execute(f"SELECT {COLUNAS} FROM usuarios").fetchall()]


def buscar_por_id(usuario_id):
    row = get_db().execute(f"SELECT {COLUNAS} FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return dict(row) if row else None


def buscar_por_email(email):
    row = get_db().execute(f"SELECT {COLUNAS} FROM usuarios WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def criar(nome, email, senha_hash, tipo=TIPO_USUARIO_PADRAO):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
    return cursor.lastrowid
