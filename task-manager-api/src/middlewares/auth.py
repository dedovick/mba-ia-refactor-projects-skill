from flask import g, request

BEARER_PREFIX = 'Bearer '


def register_auth(app, token_service):
    """Identifica o autor da requisição pelo header `Authorization: Bearer <token>`.

    Só identifica: quem decide o que cada autor pode fazer são os controllers.
    Token ausente ou inválido deixa `g.actor_id = None`.
    """

    @app.before_request
    def load_actor():
        header = request.headers.get('Authorization', '')
        token = header[len(BEARER_PREFIX):].strip() if header.startswith(BEARER_PREFIX) else ''
        g.actor_id = token_service.verify(token) if token else None


def current_actor_id():
    return g.get('actor_id')
