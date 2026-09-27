from werkzeug.security import generate_password_hash

SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
)

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

HASH_PREFIXES = ("scrypt:", "pbkdf2:")

# Contas de demonstração: as senhas são gravadas apenas como hash.
USUARIOS_INICIAIS = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


def _migrar_senhas_em_texto_puro(conn):
    """Bancos criados pela versão antiga guardavam a senha em texto puro: converte para hash."""
    legadas = [
        row for row in conn.execute("SELECT id, senha FROM usuarios").fetchall()
        if row[1] is not None and not row[1].startswith(HASH_PREFIXES)
    ]
    conn.executemany(
        "UPDATE usuarios SET senha = ? WHERE id = ?",
        [(generate_password_hash(senha), usuario_id) for usuario_id, senha in legadas],
    )


def init_db(conn):
    """Cria o schema, migra senhas legadas e, com a tabela de produtos vazia, insere os dados de exemplo (idempotente)."""
    with conn:
        for statement in SCHEMA:
            conn.execute(statement)
        _migrar_senhas_em_texto_puro(conn)
        if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                PRODUTOS_INICIAIS,
            )
            conn.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                [(nome, email, generate_password_hash(senha), tipo) for nome, email, senha, tipo in USUARIOS_INICIAIS],
            )
