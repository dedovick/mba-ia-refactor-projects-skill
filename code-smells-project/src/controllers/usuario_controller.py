import logging

from src.controllers import validators
from src.middlewares.error_handler import NotFoundError, UnauthorizedError, ValidationError
from src.models import usuario_model
from src.services import password_service

logger = logging.getLogger(__name__)


def listar():
    return usuario_model.listar()


def obter(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar(dados):
    dados = validators.require_body(dados)
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(valor, str) for valor in (nome, email, senha)):
        raise ValidationError("Nome, email e senha devem ser texto")
    validators.validate_email(email)

    usuario_id = usuario_model.criar(nome, email, password_service.hash_password(senha))
    logger.info("Usuário criado: id=%s", usuario_id)
    return usuario_id


def autenticar(dados):
    dados = dados if isinstance(dados, dict) else {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    usuario = usuario_model.buscar_por_email(email) if isinstance(email, str) else None
    if not usuario or not isinstance(senha, str) or not password_service.verify_password(usuario["senha"], senha):
        logger.info("Login falhou")
        raise UnauthorizedError("Email ou senha inválidos", sucesso=False)

    logger.info("Login bem-sucedido: usuario=%s", usuario["id"])
    return usuario
