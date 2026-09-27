# Análise de Projeto — Heurísticas de Detecção

Use este guia na **Fase 1**. O objetivo é descrever o projeto com fatos verificáveis: cada item do resumo precisa ter vindo de um arquivo que você leu.

## 1. Inventário

Liste os arquivos-fonte e conte linhas, ignorando o que não é código do projeto:

```bash
# Ignorar: .git .claude node_modules venv .venv __pycache__ dist build target vendor reports
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.mjs" -o -name "*.cjs" \
  -o -name "*.java" -o -name "*.kt" -o -name "*.go" -o -name "*.rb" -o -name "*.php" -o -name "*.cs" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.claude/*" \
  -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/__pycache__/*" \
  -not -path "*/dist/*" -not -path "*/build/*" | sort | xargs wc -l
```

Conte como "source files" apenas os arquivos de código. Manifestos, lockfiles, READMEs e arquivos `.http` entram na análise, mas não na contagem.

## 2. Linguagem

| Sinal | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, arquivos `.py` | Python |
| `package.json` com arquivos `.js`/`.mjs`/`.cjs` | JavaScript (Node.js); veja `"type": "module"` para ESM × CommonJS |
| `package.json` + `tsconfig.json` ou arquivos `.ts` | TypeScript |
| `pom.xml`, `build.gradle(.kts)` | Java / Kotlin |
| `go.mod` | Go |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj` | C# / .NET |

Versão da linguagem: `engines` no `package.json`, `python_requires`/`requires-python`, `.python-version`, `.nvmrc`, `go.mod`. Se não houver, escreva "versão não fixada" e informe a versão instalada no ambiente (`python3 --version`, `node --version`).

## 3. Framework e dependências

Leia o manifesto e confirme o uso no código (uma dependência declarada e nunca importada é um finding, não um framework).

| Dependência | Framework | Como confirmar no código |
|---|---|---|
| `flask` | Flask | `Flask(__name__)`, `@app.route`, `add_url_rule`, `Blueprint` |
| `fastapi` | FastAPI | `FastAPI()`, `@app.get`, `APIRouter` |
| `django` | Django | `urls.py`, `views.py`, `settings.py` |
| `express` | Express | `express()`, `app.get/post`, `express.Router()` |
| `fastify`, `koa`, `@nestjs/core`, `hapi` | Fastify / Koa / NestJS / Hapi | instância do framework e registro de rotas |
| `spring-boot-starter-web` | Spring Boot | `@RestController`, `@GetMapping` |
| `gin`, `echo`, `chi` | Go web | `r.GET`, `e.GET`, `r.Get` |

Versão: use a versão fixada no manifesto; se houver range (`^4.18.2`), informe também a versão resolvida no lockfile (`package-lock.json`, `poetry.lock`) quando existir.

## 4. Banco de dados

| Sinal no código | Banco / acesso |
|---|---|
| `import sqlite3`, `sqlite3.connect(...)` | SQLite via driver puro |
| `flask_sqlalchemy`, `SQLAlchemy(...)`, `db.Model` | ORM SQLAlchemy |
| `require('sqlite3')`, `new sqlite3.Database(...)` | SQLite (Node); `':memory:'` = em memória, recriado a cada boot |
| `node:sqlite`, `better-sqlite3` | SQLite (Node, API síncrona moderna) |
| `pg`, `psycopg`, `mysql2`, `pymysql`, `mongoose`, `pymongo`, `prisma`, `sequelize`, `typeorm` | Postgres / MySQL / MongoDB / ORMs |

Tabelas: procure `CREATE TABLE`, classes de model (`db.Model`, `class X(Base)`), schemas (`mongoose.Schema`, `schema.prisma`) e migrations. Registre também onde e quando o schema é criado (no import, no boot, por script de seed) e se há seed de dados.

## 5. Classificação da arquitetura

| Classificação | Sinais |
|---|---|
| **Monolítica** | Poucos arquivos concentram rotas, SQL e regra de negócio; há uma classe ou módulo "faz tudo"; não existem camadas nomeadas |
| **Parcialmente em camadas** | Existem pastas como `models/`, `routes/`, `services/`, `utils/`, mas as responsabilidades vazam: rotas com regra de negócio e queries, services não usados, validação duplicada, sem controllers |
| **Em camadas (MVC ou similar)** | Rotas só roteiam, controllers orquestram, models encapsulam dados, config separada, erro centralizado |

Justifique a classificação em uma linha, citando o arquivo que mais pesa (ex.: "`app.py` registra rotas e executa SQL direto").

> Ter as pastas certas **não** é ter a arquitetura certa. Classifique pela responsabilidade real de cada arquivo.

## 6. Domínio

Deduza o domínio pelas entidades (tabelas, models), pelos paths das rotas e pelos textos do código. Descreva em uma linha, citando as entidades principais. Exemplos de formato:
- "Sistema de reservas (hotéis, quartos, reservas, hóspedes)"
- "Plataforma de assinaturas (planos, clientes, faturas)"
- "Help desk (chamados, agentes, filas, SLAs)"

## 7. Descoberta de endpoints

Liste **todos** os endpoints, com método, path e handler (arquivo:linha). Eles são a base da validação.

| Framework | O que procurar |
|---|---|
| Flask | `@app.route(path, methods=[...])`, `@bp.route`, `app.add_url_rule(path, endpoint, view, methods=[...])`, `app.register_blueprint(bp, url_prefix=...)` (some o prefixo ao path) |
| FastAPI | `@app.get/post/put/delete`, `@router.*`, `include_router(prefix=...)` |
| Django | `path()`/`re_path()` em `urls.py`, `include()` |
| Express | `app.get/post/put/patch/delete(path, ...)`, `router.*`, `app.use(prefix, router)` |
| NestJS | `@Controller(prefix)` + `@Get/@Post(...)` |
| Spring | `@RequestMapping` na classe + `@GetMapping/@PostMapping` no método |

Sem método explícito no Flask, o padrão é `GET`. Rotas registradas dentro de funções ou classes (ex.: um método `setupRoutes(app)`) também contam.

Para cada endpoint, anote o corpo esperado (campos lidos de `request.get_json()`, `req.body`, etc.), os parâmetros de query e os exemplos existentes no projeto (`*.http`, README, testes, seeds). Você vai precisar deles para montar as requisições da linha de base.

## 8. Como a aplicação sobe

Registre: comando de execução (README, `scripts.start`, `if __name__ == "__main__"`), porta e host (e se estão fixos no código), passos prévios obrigatórios (ex.: rodar um seed) e variáveis de ambiente lidas.
