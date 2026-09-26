from flask import Blueprint, jsonify, request

from src.controllers import produto_controller
from src.views.presenters import present_produto, sucesso

bp = Blueprint("produtos", __name__)


@bp.get("/produtos")
def listar_produtos():
    produtos = produto_controller.listar()
    corpo, status = sucesso([present_produto(p) for p in produtos])
    return jsonify(corpo), status


@bp.get("/produtos/busca")
def buscar_produtos():
    resultados = produto_controller.buscar(request.args)
    corpo, status = sucesso([present_produto(p) for p in resultados], total=len(resultados))
    return jsonify(corpo), status


@bp.get("/produtos/<int:id>")
def buscar_produto(id):
    corpo, status = sucesso(present_produto(produto_controller.obter(id)))
    return jsonify(corpo), status


@bp.post("/produtos")
def criar_produto():
    produto_id = produto_controller.criar(request.get_json(silent=True))
    corpo, status = sucesso({"id": produto_id}, 201, mensagem="Produto criado")
    return jsonify(corpo), status


@bp.put("/produtos/<int:id>")
def atualizar_produto(id):
    produto_controller.atualizar(id, request.get_json(silent=True))
    corpo, status = sucesso(mensagem="Produto atualizado")
    return jsonify(corpo), status


@bp.delete("/produtos/<int:id>")
def deletar_produto(id):
    produto_controller.deletar(id)
    corpo, status = sucesso(mensagem="Produto deletado")
    return jsonify(corpo), status
