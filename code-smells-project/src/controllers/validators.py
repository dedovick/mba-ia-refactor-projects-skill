import re

from src.middlewares.error_handler import ValidationError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def require_body(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    return dados


def optional_string(dados, campo, default):
    valor = dados.get(campo, default)
    if not isinstance(valor, str):
        raise ValidationError(f"{campo} deve ser texto")
    return valor


def parse_float_param(valor, campo):
    if valor in (None, ""):
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"{campo} deve ser numérico")


def validate_email(email):
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Email inválido")
