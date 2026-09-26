import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def _env_bool(name, default="false"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = _env_bool("FLASK_DEBUG")
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH") or str(BASE_DIR / "loja.db")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
    SEED_ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "")
    APP_ENV = os.environ.get("APP_ENV", "producao")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
