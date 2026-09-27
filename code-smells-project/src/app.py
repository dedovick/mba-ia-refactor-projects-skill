import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.database import connection, seed
from src.middlewares.error_handler import register_error_handlers
from src.views import pedido_routes, produto_routes, relatorio_routes, sistema_routes, usuario_routes


def create_app(settings=Settings):
    logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config.from_object(settings)

    CORS(app, origins=settings.CORS_ORIGINS)
    connection.init_app(app)
    register_error_handlers(app)

    for blueprint in (produto_routes.bp, usuario_routes.bp, pedido_routes.bp, relatorio_routes.bp, sistema_routes.bp):
        app.register_blueprint(blueprint)

    conn = connection.connect(settings.DATABASE_PATH)
    try:
        seed.init_db(conn)
    finally:
        conn.close()
    return app
