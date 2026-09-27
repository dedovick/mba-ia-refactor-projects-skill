# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Após a refatoração, o código segue MVC em `src/` (config, database, models, services, controllers, views e middlewares).

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional; defina ao menos SECRET_KEY fora do ambiente local
python seed.py
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000` (configure `HOST`/`PORT` no ambiente ou no `.env`). O `seed.py` popula o banco SQLite (`instance/tasks.db`, configurável por `DATABASE_URL`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Autenticação

`POST /login` devolve um `token` assinado. Envie-o como `Authorization: Bearer <token>` nas operações protegidas:

| Operação | Quem pode |
|---|---|
| `POST /users` com `role` diferente de `user` | admin |
| `PUT /users/<id>` alterando `role` ou `active` | admin |
| `PUT /users/<id>` alterando `email` ou `password` | o próprio usuário ou admin |
| `DELETE /users/<id>` | admin |

As demais rotas continuam públicas.

## Estrutura

```
app.py                 # launcher: python app.py
seed.py                # python seed.py
src/
├── app.py             # create_app(): composition root
├── config/            # settings lidos do ambiente
├── database/          # extensão SQLAlchemy, commit e seed
├── models/            # entidades ORM, consultas e constantes de domínio
├── services/          # emissão/verificação de token
├── controllers/       # casos de uso, validação e autorização
├── views/             # blueprints (só HTTP) e presenters
└── middlewares/       # identificação do autor (token) e erros centralizados
```
