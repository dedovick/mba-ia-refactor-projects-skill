import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = BASE_DIR / 'instance' / 'tasks.db'
DEFAULT_TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60


def _as_bool(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _as_list(value):
    return [item.strip() for item in value.split(',') if item.strip()]


class Settings:
    """Configuração lida do ambiente; os defaults servem apenas para desenvolvimento local."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-me')
    DEBUG = _as_bool(os.environ.get('FLASK_DEBUG', 'false'))
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', '5000'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DEFAULT_DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = _as_list(os.environ.get('CORS_ORIGINS', 'http://localhost:3000'))
    TOKEN_MAX_AGE_SECONDS = int(os.environ.get('TOKEN_MAX_AGE_SECONDS', str(DEFAULT_TOKEN_MAX_AGE_SECONDS)))
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
