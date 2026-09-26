from flask import Blueprint, jsonify, request

from src.controllers import pedido_controller
from src.views.presenters import sucesso

bp = Blueprint("pedidos", __name__)


@bp.post("/pedidos")
def criar_pedido():
    resultado = pedido_controller.criar(request.get_json(silent=True))
    corpo, status = sucesso(resultado, 201, mensagem="Pedido criado com sucesso")
    return jsonify(corpo), status


@bp.get("/pedidos")
def listar_todos_pedidos():
    corpo, status = sucesso(pedido_controller.listar_todos())
    return jsonify(corpo), status


@bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    corpo, status = sucesso(pedido_controller.listar_por_usuario(usuario_id))
    return jsonify(corpo), status


@bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    pedido_controller.atualizar_status(pedido_id, request.get_json(silent=True))
    corpo, status = sucesso(mensagem="Status atualizado")
    return jsonify(corpo), status
