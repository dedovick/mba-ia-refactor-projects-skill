from src.config.constants import STATUS_VALIDOS
from src.controllers.validators import is_positive_int
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models import pedido_model, usuario_model
from src.services import notification_service


def _validar_itens(itens):
    if not isinstance(itens, list) or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict) or not is_positive_int(item.get("produto_id")):
            raise ValidationError("Cada item precisa de um produto_id inteiro positivo")
        if not is_positive_int(item.get("quantidade")):
            raise ValidationError("Cada item precisa de uma quantidade inteira maior que zero")


def criar(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not is_positive_int(usuario_id):
        raise ValidationError("Usuario ID deve ser um inteiro positivo")
    _validar_itens(itens)
    if not usuario_model.buscar_por_id(usuario_id):
        raise ValidationError("Usuário " + str(usuario_id) + " não encontrado", com_sucesso=True)

    produtos = pedido_model.precos_e_estoques(item["produto_id"] for item in itens)
    total = 0
    linhas = []
    for item in itens:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado", com_sucesso=True)
        if produto["estoque"] < item["quantidade"]:
            raise ValidationError("Estoque insuficiente para " + produto["nome"], com_sucesso=True)
        total = total + (produto["preco"] * item["quantidade"])
        linhas.append((item["produto_id"], item["quantidade"], produto["preco"]))

    try:
        pedido_id = pedido_model.criar(usuario_id, total, linhas)
    except pedido_model.EstoqueInsuficiente as err:
        raise ValidationError("Estoque insuficiente para " + produtos[err.produto_id]["nome"],
                              com_sucesso=True) from None

    notification_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar(usuario_id=None):
    return pedido_model.listar(usuario_id)


def atualizar_status(pedido_id, dados):
    dados = dados if isinstance(dados, dict) else {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        raise ValidationError("Status inválido")
    if not pedido_model.atualizar_status(pedido_id, novo_status):
        raise NotFoundError("Pedido não encontrado")
    notification_service.status_alterado(pedido_id, novo_status)
