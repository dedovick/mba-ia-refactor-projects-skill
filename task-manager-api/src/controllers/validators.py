import re
from datetime import datetime

from src.middlewares.error_handler import ValidationError
from src.models.constants import (
    COLOR_PATTERN,
    DUE_DATE_FORMAT,
    EMAIL_PATTERN,
    PRIORITY_MAX,
    PRIORITY_MIN,
    TAG_SEPARATOR,
    TASK_STATUSES,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
    USER_ROLES,
)

INVALID_PAYLOAD_MESSAGE = 'Dados inválidos'


def require_payload(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError(INVALID_PAYLOAD_MESSAGE)
    return data


def require_object(data):
    """Como require_payload, mas aceita objeto vazio (atualizações sem campos)."""
    if not isinstance(data, dict):
        raise ValidationError(INVALID_PAYLOAD_MESSAGE)
    return data


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def parse_int(value, message):
    """Converte um parâmetro de query string em inteiro."""
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(message)


# ---- tasks ---------------------------------------------------------------

def validate_title(value, required):
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ValidationError('Título é obrigatório')
        raise ValidationError('Título muito curto')
    if not isinstance(value, str):
        raise ValidationError('Título inválido')
    title = value.strip()
    if len(title) < TITLE_MIN_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > TITLE_MAX_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def validate_optional_text(value, field):
    if value is not None and not isinstance(value, str):
        raise ValidationError(f'Campo {field} deve ser texto')
    return value


def validate_status(value):
    if value not in TASK_STATUSES:
        raise ValidationError('Status inválido')
    return value


def validate_priority(value):
    if not is_integer(value):
        raise ValidationError('Prioridade inválida')
    if value < PRIORITY_MIN or value > PRIORITY_MAX:
        raise ValidationError(f'Prioridade deve ser entre {PRIORITY_MIN} e {PRIORITY_MAX}')
    return value


def validate_optional_id(value, field):
    if value is not None and not is_integer(value):
        raise ValidationError(f'{field} inválido')
    return value


def validate_due_date(value, message):
    if not isinstance(value, str):
        raise ValidationError(message)
    try:
        return datetime.strptime(value, DUE_DATE_FORMAT)
    except ValueError:
        raise ValidationError(message)


def normalize_tags(value):
    if isinstance(value, list):
        if not all(isinstance(tag, str) for tag in value):
            raise ValidationError('Tags inválidas')
        return TAG_SEPARATOR.join(value)
    if isinstance(value, str):
        return value
    raise ValidationError('Tags inválidas')


# ---- usuários --------------------------------------------------------------

def validate_name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError('Nome é obrigatório')
    return value


def validate_email(value):
    if not isinstance(value, str) or not re.match(EMAIL_PATTERN, value):
        raise ValidationError('Email inválido')
    return value


def validate_role(value):
    if value not in USER_ROLES:
        raise ValidationError('Role inválido')
    return value


def validate_active(value):
    if not isinstance(value, bool):
        raise ValidationError('Campo active deve ser booleano')
    return value


def validate_password_type(value, required_message):
    if not isinstance(value, str) or not value:
        raise ValidationError(required_message)
    return value


# ---- categorias ------------------------------------------------------------

def validate_color(value):
    if not isinstance(value, str) or not re.match(COLOR_PATTERN, value):
        raise ValidationError('Cor inválida. Use o formato #RRGGBB')
    return value
