import hmac
from functools import wraps

from flask import current_app, request

from src.middlewares.error_handler import UnauthorizedError

ADMIN_TOKEN_HEADER = "X-Admin-Token"


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        esperado = current_app.config.get("ADMIN_TOKEN", "")
        informado = request.headers.get(ADMIN_TOKEN_HEADER, "")
        if not esperado or not hmac.compare_digest(informado.encode(), esperado.encode()):
            raise UnauthorizedError("Não autorizado")
        return view(*args, **kwargs)
    return wrapper
