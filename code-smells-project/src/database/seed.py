import logging
import secrets

from src.services import password_service

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descricao TEXT,
    preco REAL,
    estoque INTEGER,
    categoria TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    senha TEXT,
    tipo TEXT DEFAULT 'cliente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    status TEXT DEFAULT 'pendente',
    total REAL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    preco_unitario REAL
);
"""

PRODUTOS_INICIAIS = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Usuários de demonstração para desenvolvimento; as senhas são gravadas com hash.
CLIENTES_DEMO = [
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


def init_db(conn, admin_password=""):
    """Cria o schema e aplica o seed uma única vez (idempotente)."""
    with conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            _seed(conn, admin_password)
        _hash_legacy_passwords(conn)


def _seed(conn, admin_password):
    conn.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        PRODUTOS_INICIAIS,
    )
    if not admin_password:
        admin_password = secrets.token_urlsafe(16)
        logger.warning(
            "SEED_ADMIN_PASSWORD não definido: usuário admin criado com senha aleatória"
        )
    usuarios = [("Admin", "admin@loja.com", admin_password, "admin"), *CLIENTES_DEMO]
    conn.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        [(nome, email, password_service.hash_password(senha), tipo) for nome, email, senha, tipo in usuarios],
    )
    logger.info("Seed aplicado: %d produtos e %d usuários", len(PRODUTOS_INICIAIS), len(usuarios))


def _hash_legacy_passwords(conn):
    """Converte senhas em texto puro de bancos criados pela versão anterior."""
    rows = conn.execute("SELECT id, senha FROM usuarios").fetchall()
    legados = [
        (password_service.hash_password(row["senha"]), row["id"])
        for row in rows
        if row["senha"] and not password_service.is_hashed(row["senha"])
    ]
    if legados:
        conn.executemany("UPDATE usuarios SET senha = ? WHERE id = ?", legados)
        logger.warning("%d senha(s) em texto puro convertidas para hash", len(legados))
