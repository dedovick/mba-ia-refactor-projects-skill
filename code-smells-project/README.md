# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`, reorganizada em camadas MVC.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000` (ou na porta de `PORT`). O banco SQLite (`loja.db`, na raiz do projeto) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

Configuração por variáveis de ambiente (veja `.env.example`):

| Variável | Padrão | Para quê |
|---|---|---|
| `PORT` / `HOST` | `5000` / `127.0.0.1` | Endereço do servidor |
| `FLASK_DEBUG` | `false` | Liga o modo debug (só em desenvolvimento) |
| `SECRET_KEY` | `dev-only-change-me` | Chave do Flask; defina em produção |
| `DATABASE_PATH` | `<projeto>/loja.db` | Caminho do SQLite |
| `CORS_ORIGINS` | `http://localhost:3000` | Origens permitidas, separadas por vírgula |
| `ADMIN_TOKEN` | vazio | Token do header `X-Admin-Token` exigido em `/admin/*`; vazio desabilita essas rotas |
| `SEED_ADMIN_PASSWORD` | vazio (senha aleatória) | Senha do usuário `admin@loja.com` criado pelo seed |

Exemplo de rota administrativa:

```bash
ADMIN_TOKEN=troque-me python app.py
curl -X POST localhost:5000/admin/query -H "X-Admin-Token: troque-me" \
     -H "Content-Type: application/json" -d '{"sql": "SELECT COUNT(*) AS n FROM produtos"}'
```

## Estrutura

```
app.py                  # launcher: create_app() + app.run (mesmo comando de antes)
src/
├── app.py              # composition root: config, CORS, banco, error handlers, blueprints
├── config/settings.py  # configuração lida do ambiente
├── database/           # conexão por requisição (connection.py) e schema/seed (seed.py)
├── models/             # acesso a dados parametrizado por entidade + constants.py
├── services/           # hash de senha e notificações
├── controllers/        # validação e regras de cada caso de uso
├── views/              # blueprints por domínio e presenters (formato das respostas)
└── middlewares/        # handler central de erros e autenticação admin
```
