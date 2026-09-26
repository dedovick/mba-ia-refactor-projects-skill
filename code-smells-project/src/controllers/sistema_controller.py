import logging
import sqlite3

from src.middlewares.error_handler import ValidationError
from src.models import sistema_model
from src.models.constants import API_VERSION

logger = logging.getLogger(__name__)


def health(ambiente):
    """Devolve (payload, saudável). Só estado; nenhuma configuração interna."""
    try:
        counts = sistema_model.contar_registros()
    except sqlite3.Error:
        logger.exception("Health check falhou")
        return {"status": "erro", "detalhes": "Banco de dados indisponível"}, False
    return {
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": API_VERSION,
        "ambiente": ambiente,
    }, True


def resetar_banco():
    sistema_model.resetar_banco()
    logger.warning("Banco de dados resetado via /admin/reset-db")


def executar_consulta(dados):
    dados = dados if isinstance(dados, dict) else {}
    sql = dados.get("sql", "")
    if not sql:
        raise ValidationError("Query não informada")
    if not isinstance(sql, str) or not sql.strip().upper().startswith("SELECT"):
        raise ValidationError("Apenas consultas SELECT são permitidas")
    try:
        return sistema_model.executar_consulta_leitura(sql)
    except sqlite3.Error as err:
        logger.info("Consulta admin recusada: %s", err)
        raise ValidationError("Consulta inválida ou não permitida")
