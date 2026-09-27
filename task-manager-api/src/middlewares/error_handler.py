import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from src.database.connection import db

logger = logging.getLogger(__name__)

GENERIC_ERROR_MESSAGE = 'Erro interno do servidor'


class AppError(Exception):
    status = 500

    def __init__(self, message, status=None):
        super().__init__(message)
        self.message = message
        if status:
            self.status = status


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        db.session.rollback()
        return jsonify({'error': err.message}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({'error': err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        db.session.rollback()
        logger.exception('Erro inesperado')
        return jsonify({'error': GENERIC_ERROR_MESSAGE}), 500
