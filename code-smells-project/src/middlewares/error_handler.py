import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de domínio. `com_sucesso=True` inclui `"sucesso": false` no corpo, como o contrato original."""

    status = 500

    def __init__(self, mensagem, com_sucesso=False):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.com_sucesso = com_sucesso

    def to_dict(self):
        corpo = {"erro": self.mensagem}
        if self.com_sucesso:
            corpo["sucesso"] = False
        return corpo


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify(err.to_dict()), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({"erro": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
