# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`, reorganizada em camadas MVC.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000` (ou na porta de `PORT`). O banco SQLite (`loja.db`, na raiz do projeto, ou o caminho de `DATABASE_PATH`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas gravadas como hash).

### Configuração

Toda configuração vem de variáveis de ambiente; veja `.env.example`:

| Variável | Padrão | Uso |
|---|---|---|
| `PORT` / `HOST` | `5000` / `127.0.0.1` | Endereço do servidor |
| `FLASK_DEBUG` | `false` | Liga o modo debug (nunca em produção) |
| `DATABASE_PATH` | `<raiz>/loja.db` | Arquivo do SQLite |
| `SECRET_KEY` | valor de desenvolvimento | Chave da aplicação |
| `ADMIN_TOKEN` | vazio | Token do header `X-Admin-Token` exigido por `/admin/*`; vazio desativa as rotas admin |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5000` | Origens liberadas no CORS |
| `APP_ENV`, `LOG_LEVEL` | `producao`, `INFO` | Ambiente informado no `/health` e nível de log |

Exemplo: `PORT=8080 ADMIN_TOKEN=troque-me python app.py`

## Estrutura

```
app.py                 # launcher: python app.py
src/app.py             # create_app(): composition root
src/config/            # settings (ambiente) e constantes de domínio
src/database/          # conexão por requisição e schema/seed
src/models/            # acesso a dados por entidade (SQL parametrizado)
src/services/          # notificações
src/controllers/       # casos de uso, regras e validação
src/views/             # blueprints HTTP e presenters
src/middlewares/       # tratamento de erros e autenticação admin
```
