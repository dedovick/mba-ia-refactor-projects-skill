# Execução 1 — code-smells-project (interrompida na Fase 3)

Arquivos alterados em relação ao original:
```
 M code-smells-project/README.md
 M code-smells-project/app.py
D  code-smells-project/controllers.py
D  code-smells-project/database.py
D  code-smells-project/models.py
 M code-smells-project/requirements.txt
?? code-smells-project/.env.example
?? code-smells-project/reports/
?? code-smells-project/src/
```

Estrutura criada em src/:
```
src/__init__.py
src/app.py
src/config/__init__.py
src/config/constants.py
src/config/logger.py
src/config/settings.py
src/controllers/__init__.py
src/controllers/admin_controller.py
src/controllers/health_controller.py
src/controllers/pedido_controller.py
src/controllers/produto_controller.py
src/controllers/relatorio_controller.py
src/controllers/usuario_controller.py
src/controllers/validators.py
src/database/__init__.py
src/database/connection.py
src/database/seed.py
src/errors.py
src/middlewares/__init__.py
src/middlewares/auth.py
src/middlewares/error_handler.py
src/models/__init__.py
src/models/admin_model.py
src/models/pedido_model.py
src/models/produto_model.py
src/models/usuario_model.py
src/services/__init__.py
src/services/notification_service.py
src/services/password_service.py
src/services/pedido_service.py
src/views/__init__.py
src/views/admin_routes.py
src/views/pedido_routes.py
src/views/presenters.py
src/views/produto_routes.py
src/views/relatorio_routes.py
src/views/sistema_routes.py
src/views/usuario_routes.py
```
