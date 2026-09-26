from werkzeug.security import check_password_hash, generate_password_hash

_HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    return bool(stored_hash) and check_password_hash(stored_hash, password)


def is_hashed(value):
    return value.startswith(_HASH_PREFIXES)
