from src.middlewares.error_handler import ValidationError


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_positive_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def require_number(value, mensagem):
    if not is_number(value):
        raise ValidationError(mensagem)
    return value


def require_string(value, mensagem):
    if not isinstance(value, str):
        raise ValidationError(mensagem)
    return value


def parse_optional_float(raw, nome):
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        raise ValidationError(f"{nome} deve ser numérico") from None
