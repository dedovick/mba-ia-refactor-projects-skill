from flask import Blueprint, current_app, jsonify, request

from src.controllers import sistema_controller
from src.middlewares.auth import require_admin
from src.models.constants import API_VERSION
from src.views.presenters import sucesso

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
    corpo, saudavel = sistema_controller.health(current_app.config["APP_ENV"])
    return jsonify(corpo), 200 if saudavel else 500


@bp.post("/admin/reset-db")
@require_admin
def reset_database():
    sistema_controller.resetar_banco()
    corpo, status = sucesso(mensagem="Banco de dados resetado")
    return jsonify(corpo), status


@bp.post("/admin/query")
@require_admin
def executar_query():
    corpo, status = sucesso(sistema_controller.executar_consulta(request.get_json(silent=True)))
    return jsonify(corpo), status
