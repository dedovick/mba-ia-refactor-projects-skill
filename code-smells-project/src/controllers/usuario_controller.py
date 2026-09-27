import logging
import re

from werkzeug.security import check_password_hash, generate_password_hash

from src.middlewares.error_handler import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from src.models import usuario_model

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _texto(dados, campo):
    valor = dados.get(campo, "")
    return valor if isinstance(valor, str) else ""


def listar():
    return usuario_model.listar()


def obter(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return usuario


def criar(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    nome, email, senha = _texto(dados, "nome"), _texto(dados, "email"), _texto(dados, "senha")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Email inválido")
    if usuario_model.existe_email(email):
        raise ConflictError("Email já cadastrado")

    usuario_id = usuario_model.criar(nome, email, generate_password_hash(senha))
    logger.info("Usuário %s criado", usuario_id)
    return usuario_id


def autenticar(dados):
    dados = dados if isinstance(dados, dict) else {}
    email, senha = _texto(dados, "email"), _texto(dados, "senha")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    contas = usuario_model.buscar_credenciais(email)
    conta = next((c for c in contas if check_password_hash(c["senha_hash"] or "", senha)), None)
    if not conta:
        logger.info("Falha de login")
        raise UnauthorizedError("Email ou senha inválidos", com_sucesso=True)
    logger.info("Login bem-sucedido do usuário %s", conta["id"])
    return conta
