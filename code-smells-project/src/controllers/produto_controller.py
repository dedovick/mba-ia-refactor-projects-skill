import logging

from src.config.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from src.controllers.validators import parse_optional_float, require_number, require_string
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models import produto_model

logger = logging.getLogger(__name__)


def _validar(dados):
    """Valida o corpo de criação/atualização e devolve os campos normalizados."""
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = require_string(dados["nome"], "Nome deve ser texto")
    descricao = require_string(dados.get("descricao", ""), "Descrição deve ser texto")
    preco = require_number(dados["preco"], "Preço deve ser numérico")
    estoque = require_number(dados["estoque"], "Estoque deve ser numérico")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

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
    return nome, descricao, preco, estoque, categoria


def listar():
    produtos = produto_model.listar()
    logger.debug("Listando %d produtos", len(produtos))
    return produtos


def obter(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", com_sucesso=True)
    return produto


def criar(dados):
    produto_id = produto_model.criar(*_validar(dados))
    logger.info("Produto %s criado", produto_id)
    return produto_id


def atualizar(produto_id, dados):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.atualizar(produto_id, *_validar(dados))


def remover(produto_id):
    if not produto_model.remover(produto_id):
        raise NotFoundError("Produto não encontrado")
    logger.info("Produto %s removido", produto_id)


def buscar(args):
    preco_min = parse_optional_float(args.get("preco_min"), "preco_min")
    preco_max = parse_optional_float(args.get("preco_max"), "preco_max")
    return produto_model.buscar(args.get("q", ""), args.get("categoria"), preco_min, preco_max)
