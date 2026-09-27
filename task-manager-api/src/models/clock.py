from datetime import datetime, timezone


def utc_now():
    """UTC atual sem tzinfo, no mesmo formato que o banco já armazena."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
