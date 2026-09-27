from pathlib import Path

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

SQLITE_PREFIX = 'sqlite:///'


def _ensure_sqlite_directory(uri):
    if uri.startswith(SQLITE_PREFIX) and ':memory:' not in uri:
        Path(uri[len(SQLITE_PREFIX):]).parent.mkdir(parents=True, exist_ok=True)


def init_app(app):
    _ensure_sqlite_directory(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    with app.app_context():
        # Importa os models para registrar as tabelas antes do create_all.
        from src.models import category_model, task_model, user_model  # noqa: F401
        db.create_all()


def commit():
    """Confirma a unidade de trabalho da requisição; desfaz tudo se falhar."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
