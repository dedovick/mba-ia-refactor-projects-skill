import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.controllers.category_controller import CategoryController
from src.controllers.report_controller import ReportController
from src.controllers.task_controller import TaskController
from src.controllers.user_controller import UserController
from src.database import connection
from src.middlewares.auth import register_auth
from src.middlewares.error_handler import register_error_handlers
from src.services.token_service import TokenService
from src.views.category_routes import create_category_blueprint
from src.views.report_routes import create_report_blueprint
from src.views.system_routes import create_system_blueprint
from src.views.task_routes import create_task_blueprint
from src.views.user_routes import create_user_blueprint


def create_app(settings=Settings):
    """Composition root: config, banco, middlewares, controllers e rotas."""
    logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app, origins=settings.CORS_ORIGINS)
    connection.init_app(app)

    token_service = TokenService(settings.SECRET_KEY, settings.TOKEN_MAX_AGE_SECONDS)
    register_auth(app, token_service)
    register_error_handlers(app)

    app.register_blueprint(create_system_blueprint())
    app.register_blueprint(create_task_blueprint(TaskController()))
    app.register_blueprint(create_user_blueprint(UserController(token_service)))
    app.register_blueprint(create_category_blueprint(CategoryController()))
    app.register_blueprint(create_report_blueprint(ReportController()))
    return app
