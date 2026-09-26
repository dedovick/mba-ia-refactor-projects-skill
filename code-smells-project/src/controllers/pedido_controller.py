from src.controllers import validators
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models import pedido_model, produto_model
from src.models.constants import STATUS_PEDIDO_VALIDOS
from src.services import notification_service


def criar(dados):
    dados = validators.require_body(dados)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not validators.is_integer(usuario_id):
        raise ValidationError("Usuario ID deve ser um número inteiro")
    if not itens or not isinstance(itens, list):
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        _validar_item(item)

    itens_precificados = []
    total = 0
    for item in itens:
        produto = produto_model.buscar_por_id(item["produto_id"])
        if produto is None:
            raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado", sucesso=False)
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError("Estoque insuficiente para " + produto["nome"], sucesso=False)
        total = total + produto["preco"] * item["quantidade"]
        itens_precificados.append({
            "produto_id": item["produto_id"],
            "quantidade": item["quantidade"],
            "preco_unitario": produto["preco"],
        })

    try:
        pedido_id = pedido_model.criar(usuario_id, total, itens_precificados)
    except pedido_model.EstoqueInsuficiente as err:
        produto = produto_model.buscar_por_id(err.produto_id)
        raise ValidationError("Estoque insuficiente para " + produto["nome"], sucesso=False)

    notification_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar_todos():
    return pedido_model.listar()


def listar_por_usuario(usuario_id):
    return pedido_model.listar(usuario_id=usuario_id)


def atualizar_status(pedido_id, dados):
    dados = dados if isinstance(dados, dict) else {}
    novo_status = dados.get("status", "")

    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    if not pedido_model.atualizar_status(pedido_id, novo_status):
        raise NotFoundError("Pedido não encontrado")

    notification_service.status_alterado(pedido_id, novo_status)


def _validar_item(item):
    if not isinstance(item, dict):
        raise ValidationError("Item do pedido inválido")
    if not validators.is_integer(item.get("produto_id")):
        raise ValidationError("produto_id do item deve ser um número inteiro")
    quantidade = item.get("quantidade")
    if not validators.is_integer(quantidade) or quantidade <= 0:
        raise ValidationError("quantidade do item deve ser um inteiro maior que zero")
