import logging
import sqlite3

from flask import Blueprint, current_app, jsonify, request

from src.config.constants import API_VERSION
from src.controllers import sistema_controller
from src.middlewares.auth import require_admin

logger = logging.getLogger(__name__)

bp = Blueprint("sistema", __name__)


@bp.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@bp.get("/health")
def health_check():
    try:
        counts = sistema_controller.contagens()
    except sqlite3.Error:
        logger.exception("Health check: banco indisponível")
        return jsonify({"status": "erro", "detalhes": "Banco de dados indisponível"}), 500
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": API_VERSION,
        "ambiente": current_app.config["APP_ENV"],
    }), 200


@bp.post("/admin/reset-db")
@require_admin
def reset_database():
    sistema_controller.resetar_banco()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


@bp.post("/admin/query")
@require_admin
def executar_query():
    dados = sistema_controller.executar_consulta(request.get_json(silent=True))
    return jsonify({"dados": dados, "sucesso": True}), 200
