import logging

from src.controllers import validators
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models import produto_model
from src.models.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN

logger = logging.getLogger(__name__)


def listar():
    produtos = produto_model.listar()
    logger.info("Listando %d produtos", len(produtos))
    return produtos


def obter(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", sucesso=False)
    return produto


def buscar(params):
    return produto_model.buscar(
        termo=params.get("q", ""),
        categoria=params.get("categoria") or None,
        preco_min=validators.parse_float_param(params.get("preco_min"), "preco_min"),
        preco_max=validators.parse_float_param(params.get("preco_max"), "preco_max"),
    )


def criar(dados):
    produto = _validar_produto(dados)
    produto_id = produto_model.criar(**produto)
    logger.info("Produto criado com ID: %s", produto_id)
    return produto_id


def atualizar(produto_id, dados):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto = _validar_produto(dados)
    produto_model.atualizar(produto_id, **produto)


def deletar(produto_id):
    if not produto_model.deletar(produto_id):
        raise NotFoundError("Produto não encontrado")
    logger.info("Produto %s deletado", produto_id)


def _validar_produto(dados):
    """Validação única usada por criação e atualização."""
    dados = validators.require_body(dados)
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    descricao = validators.optional_string(dados, "descricao", "")
    categoria = validators.optional_string(dados, "categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if not validators.is_number(preco):
        raise ValidationError("Preço deve ser numérico")
    if not validators.is_integer(estoque):
        raise ValidationError("Estoque deve ser um número inteiro")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {"nome": nome, "descricao": descricao, "preco": preco, "estoque": estoque, "categoria": categoria}
