import logging

from src.controllers import validators as v
from src.database.connection import commit
from src.middlewares.error_handler import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from src.models.constants import DEFAULT_ROLE, MIN_PASSWORD_LENGTH
from src.models.task_model import Task
from src.models.user_model import User

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'
INVALID_CREDENTIALS = 'Credenciais inválidas'
AUTH_REQUIRED = 'Autenticação necessária'
FORBIDDEN = 'Acesso negado'
# Campos de PUT /users/<id> que só o próprio usuário (ou um admin) pode alterar.
SELF_OR_ADMIN_FIELDS = ('email', 'password')
# Campos que só um admin pode alterar.
ADMIN_ONLY_FIELDS = ('role', 'active')


class UserController:
    def __init__(self, token_service):
        self._token_service = token_service

    # ---- leitura -----------------------------------------------------------

    def list_users(self):
        counts = Task.count_by_user()
        return [(user, counts.get(user.id, 0)) for user in User.list_all()]

    def get_user(self, user_id):
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        return user

    def get_user_with_tasks(self, user_id):
        user = self.get_user(user_id)
        return user, Task.list_by_user(user_id)

    # ---- escrita -----------------------------------------------------------

    def create_user(self, data, actor_id):
        v.require_payload(data)
        name, email, password = data.get('name'), data.get('email'), data.get('password')
        role = data.get('role', DEFAULT_ROLE)

        if not name:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not password:
            raise ValidationError('Senha é obrigatória')
        v.validate_name(name)
        v.validate_email(email)
        v.validate_password_type(password, 'Senha é obrigatória')
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
        if User.find_by_email(email):
            raise ConflictError('Email já cadastrado')
        v.validate_role(role)
        if role != DEFAULT_ROLE:
            self._require_admin(actor_id)

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        user.save()
        commit()
        logger.info('Usuário criado: %s', user.id)
        return user

    def update_user(self, user_id, data, actor_id):
        user = self.get_user(user_id)
        v.require_payload(data)
        self._authorize_update(user, data, actor_id)

        if 'name' in data:
            user.name = v.validate_name(data['name'])
        if 'email' in data:
            email = v.validate_email(data['email'])
            existing = User.find_by_email(email)
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = email
        if 'password' in data:
            password = v.validate_password_type(data['password'], 'Senha muito curta')
            if len(password) < MIN_PASSWORD_LENGTH:
                raise ValidationError('Senha muito curta')
            user.set_password(password)
        if 'role' in data:
            user.role = v.validate_role(data['role'])
        if 'active' in data:
            user.active = v.validate_active(data['active'])

        commit()
        return user

    def delete_user(self, user_id, actor_id):
        user = self.get_user(user_id)
        self._require_admin(actor_id)
        user.delete()  # as tasks do usuário saem na mesma transação (cascade)
        commit()
        logger.info('Usuário deletado: %s', user_id)

    def login(self, data):
        v.require_payload(data)
        email, password = data.get('email'), data.get('password')
        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')
        if not isinstance(email, str) or not isinstance(password, str):
            raise UnauthorizedError(INVALID_CREDENTIALS)

        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            raise UnauthorizedError(INVALID_CREDENTIALS)
        if not user.active:
            raise ForbiddenError('Usuário inativo')

        if user.has_legacy_hash():
            user.set_password(password)
            commit()
        return user, self._token_service.issue(user.id)

    # ---- autorização -------------------------------------------------------

    def _require_actor(self, actor_id):
        actor = User.find_by_id(actor_id) if actor_id is not None else None
        if not actor or not actor.active:
            raise UnauthorizedError(AUTH_REQUIRED)
        return actor

    def _require_admin(self, actor_id):
        actor = self._require_actor(actor_id)
        if not actor.is_admin:
            raise ForbiddenError(FORBIDDEN)
        return actor

    def _authorize_update(self, user, data, actor_id):
        if any(field in data for field in ADMIN_ONLY_FIELDS):
            self._require_admin(actor_id)
        elif any(field in data for field in SELF_OR_ADMIN_FIELDS):
            actor = self._require_actor(actor_id)
            if actor.id != user.id and not actor.is_admin:
                raise ForbiddenError(FORBIDDEN)
