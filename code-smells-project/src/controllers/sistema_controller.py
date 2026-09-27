import logging
import sqlite3

from src.middlewares.error_handler import ValidationError
from src.models import admin_model, pedido_model, produto_model, usuario_model

logger = logging.getLogger(__name__)


def contagens():
    """Contagens para o health check; lança sqlite3.Error se o banco estiver indisponível."""
    return {
        "produtos": produto_model.contar(),
        "usuarios": usuario_model.contar(),
        "pedidos": pedido_model.contar(),
    }


def resetar_banco():
    admin_model.apagar_tudo()
    logger.warning("Banco de dados resetado via /admin/reset-db")


def executar_consulta(dados):
    dados = dados if isinstance(dados, dict) else {}
    sql = dados.get("sql", "")
    if not sql or not isinstance(sql, str):
        raise ValidationError("Query não informada")
    if not sql.strip().upper().startswith("SELECT"):
        raise ValidationError("Apenas consultas SELECT são permitidas")
    try:
        return admin_model.consultar(sql)
    except sqlite3.Error as err:
        raise ValidationError(f"Query inválida: {err}") from None
