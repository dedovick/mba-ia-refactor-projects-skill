from flask import Blueprint, jsonify, request

from src.controllers import usuario_controller
from src.views.presenters import present_usuario, present_usuario_login, sucesso

bp = Blueprint("usuarios", __name__)


@bp.get("/usuarios")
def listar_usuarios():
    corpo, status = sucesso([present_usuario(u) for u in usuario_controller.listar()])
    return jsonify(corpo), status


@bp.get("/usuarios/<int:id>")
def buscar_usuario(id):
    corpo, status = sucesso(present_usuario(usuario_controller.obter(id)))
    return jsonify(corpo), status


@bp.post("/usuarios")
def criar_usuario():
    usuario_id = usuario_controller.criar(request.get_json(silent=True))
    corpo, status = sucesso({"id": usuario_id}, 201)
    return jsonify(corpo), status


@bp.post("/login")
def login():
    usuario = usuario_controller.autenticar(request.get_json(silent=True))
    corpo, status = sucesso(present_usuario_login(usuario), mensagem="Login OK")
    return jsonify(corpo), status
