from src.config.constants import TIPO_USUARIO_PADRAO
from src.database.connection import get_db

CAMPOS = ("id", "nome", "email", "tipo", "criado_em")


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS}


def listar():
    return [_to_dict(row) for row in get_db().execute("SELECT * FROM usuarios").fetchall()]


def buscar_por_id(usuario_id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _to_dict(row) if row else None


def existe_email(email):
    return get_db().execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone() is not None


def buscar_credenciais(email):
    """Contas com o e-mail informado, incluindo o hash da senha (uso interno do login)."""
    rows = get_db().execute("SELECT * FROM usuarios WHERE email = ? ORDER BY id", (email,)).fetchall()
    return [{**_to_dict(row), "senha_hash": row["senha"]} for row in rows]


def criar(nome, email, senha_hash, tipo=TIPO_USUARIO_PADRAO):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
    return cursor.lastrowid


def contar():
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
