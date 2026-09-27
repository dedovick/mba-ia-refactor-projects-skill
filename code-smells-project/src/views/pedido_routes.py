from flask import Blueprint, jsonify, request

from src.controllers import pedido_controller
from src.views.presenters import present_pedido

bp = Blueprint("pedidos", __name__)


@bp.post("/pedidos")
def criar_pedido():
    resultado = pedido_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


@bp.get("/pedidos")
def listar_todos_pedidos():
    return jsonify({"dados": [present_pedido(p) for p in pedido_controller.listar()], "sucesso": True}), 200


@bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    pedidos = pedido_controller.listar(usuario_id)
    return jsonify({"dados": [present_pedido(p) for p in pedidos], "sucesso": True}), 200


@bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    pedido_controller.atualizar_status(pedido_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
