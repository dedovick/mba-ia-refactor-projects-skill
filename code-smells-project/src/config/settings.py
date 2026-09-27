import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def _bool(name, default="false"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes")


def _list(name, default):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = _bool("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "loja.db"))
    CORS_ORIGINS = _list("CORS_ORIGINS", "http://localhost:3000,http://localhost:5000")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
    APP_ENV = os.environ.get("APP_ENV", "producao")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
