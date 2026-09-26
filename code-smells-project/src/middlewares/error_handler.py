import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de domínio. O corpo segue o formato histórico da API: {"erro": ..., [extra]}."""

    status = 500

    def __init__(self, message, status=None, **extra):
        super().__init__(message)
        self.message = message
        self.extra = extra
        if status:
            self.status = status


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class NotFoundError(AppError):
    status = 404


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": err.message, **err.extra}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        # 404/405 do próprio Flask mantêm a resposta padrão do framework
        return err

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
