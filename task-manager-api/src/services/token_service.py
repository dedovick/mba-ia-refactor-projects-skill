from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_SALT = 'auth-token'


class TokenService:
    """Emite e verifica tokens assinados com a SECRET_KEY da aplicação."""

    def __init__(self, secret_key, max_age_seconds):
        self._serializer = URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT)
        self._max_age = max_age_seconds

    def issue(self, user_id):
        return self._serializer.dumps({'user_id': user_id})

    def verify(self, token):
        """Devolve o id do usuário do token, ou None se o token for inválido ou expirado."""
        try:
            payload = self._serializer.loads(token, max_age=self._max_age)
        except (BadSignature, SignatureExpired):
            return None
        user_id = payload.get('user_id') if isinstance(payload, dict) else None
        return user_id if isinstance(user_id, int) else None
