from flask import Blueprint, jsonify, request

from src.controllers import usuario_controller
from src.views.presenters import present_login, present_usuario

bp = Blueprint("usuarios", __name__)


@bp.get("/usuarios")
def listar_usuarios():
    usuarios = usuario_controller.listar()
    return jsonify({"dados": [present_usuario(u) for u in usuarios], "sucesso": True}), 200


@bp.get("/usuarios/<int:usuario_id>")
def buscar_usuario(usuario_id):
    return jsonify({"dados": present_usuario(usuario_controller.obter(usuario_id)), "sucesso": True}), 200


@bp.post("/usuarios")
def criar_usuario():
    usuario_id = usuario_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@bp.post("/login")
def login():
    usuario = usuario_controller.autenticar(request.get_json(silent=True))
    return jsonify({"dados": present_login(usuario), "sucesso": True, "mensagem": "Login OK"}), 200
