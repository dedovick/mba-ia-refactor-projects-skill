from flask import Blueprint, jsonify

from src.controllers import relatorio_controller
from src.views.presenters import sucesso

bp = Blueprint("relatorios", __name__)


@bp.get("/relatorios/vendas")
def relatorio_vendas():
    corpo, status = sucesso(relatorio_controller.vendas())
    return jsonify(corpo), status
