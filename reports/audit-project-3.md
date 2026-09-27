# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.12 + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.1.1)
Files:   14 analyzed | ~1158 lines of code
Date:    2026-09-27
================================
```

## Summary

CRITICAL: 5 | HIGH: 3 | MEDIUM: 7 | LOW: 4
Probes: 15 vulneráveis de 19 executadas — todas cobertas por findings (F-01, F-02, F-03, F-05, F-07, F-08, F-10)

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 5 | F-01, F-02, F-03, F-04, F-05 |
| HIGH | 3 | F-06, F-07, F-08 |
| MEDIUM | 7 | F-09, F-10, F-11, F-12, F-13, F-14, F-15 |
| LOW | 4 | F-16, F-17, F-18, F-19 |

## Findings

### F-01 [CRITICAL] Hash de senha devolvido nas respostas da API
File: models/user.py:16-25 | routes/user_routes.py:33, 85-86, 129, 207-211
Catalog: AP-03
Evidence: probe P1, probe P2, probe P3, probe P16
Description: `User.to_dict()` inclui `'password': self.password` e é usado em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login` (`'user': user.to_dict()`).
Impact: Qualquer cliente lê o hash MD5 de qualquer usuário (`81dc9bdb…` = md5("1234") do admin), que é revertido em segundos com rainbow tables.
Recommendation: Serialização pública sem `password`; hash só é lido dentro do model para verificar login (T-07).

### F-02 [CRITICAL] Nenhuma autenticação/autorização; papel aceito do cliente e token falso
File: routes/user_routes.py:52, 71-72, 92-132, 114-122, 134-151, 207-211 | routes/task_routes.py:156, 225 | routes/report_routes.py:12, 103, 190, 211
Catalog: AP-06
Evidence: probe P2, probe P3, probe P16, probe P17
Description: Todas as rotas são públicas. `POST /users` aceita `role = data.get('role', 'user')` (cria `admin` sem credencial); `PUT /users/<id>` troca `password`, `role` e `active` de qualquer conta; `DELETE /users/<id>` apaga usuário e tasks; o login devolve `'token': 'fake-jwt-token-' + str(user.id)`, previsível e nunca validado.
Impact: Qualquer pessoa assume a conta do admin (P16: senha trocada e login com a nova senha → 200), cria administradores (P3) e apaga usuários (P17). Os relatórios expõem nome/e-mail de todos.
Recommendation: Token assinado emitido no login (itsdangerous com `SECRET_KEY` do ambiente) e decorator de autenticação; exigir papel `admin` para criar usuário com papel, alterar `role`/`active` e remover usuários; alteração de senha só pelo próprio usuário ou admin (T-15).

### F-03 [CRITICAL] Debug do Werkzeug ativo com bind público
File: app.py:34
Catalog: AP-07
Evidence: probe P6, probe P7, probe P8, probe P9, probe P10, probe P11, probe P19
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` fixo. O log de boot mostra `Debugger is active!` e o PIN; cada 500 devolve a página HTML do debugger com traceback e trechos do código-fonte.
Impact: Execução remota de código pelo console interativo do debugger acessível na rede; vazamento de caminhos e código em qualquer erro.
Recommendation: `DEBUG` e `HOST` lidos do ambiente com padrão `False`/`127.0.0.1` via módulo de config (T-01).

### F-04 [CRITICAL] Segredos hardcoded (SECRET_KEY e credenciais SMTP)
File: app.py:13 | services/notification_service.py:7-10
Catalog: AP-01
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e `self.email_user = 'taskmanager@gmail.com'`, `self.email_password = 'senha123'`. `python-dotenv` está declarado em `requirements.txt:6`, mas nenhum arquivo lê variáveis de ambiente.
Impact: Chave de assinatura e senha de e-mail vazam com o repositório e não podem variar por ambiente; quem tem a `SECRET_KEY` forja sessões/tokens.
Recommendation: Módulo `config` lendo variáveis de ambiente (com `.env` via python-dotenv) e `.env.example` sem valores reais (T-01).

### F-05 [CRITICAL] Senhas com MD5 sem salt e política mínima de 4 caracteres
File: models/user.py:3, 27-32 | routes/user_routes.py:64-65, 115-116
Catalog: AP-04
Evidence: probe P1
Description: `hashlib.md5(pwd.encode()).hexdigest()` para gravar e comparar (comparação com `==`, sem tempo constante); senhas de 4 caracteres aceitas.
Impact: Um vazamento do banco (ou das respostas, F-01) revela todas as senhas instantaneamente.
Recommendation: `werkzeug.security.generate_password_hash`/`check_password_hash` (scrypt/pbkdf2 com salt), com rehash transparente de hashes MD5 legados no login (T-06).

### F-06 [HIGH] Regra de negócio, queries e serialização dentro das rotas
File: routes/task_routes.py:11-63, 85-154, 156-223, 273-299 | routes/report_routes.py:12-101, 103-155 | routes/user_routes.py:42-90, 92-132
Catalog: AP-08
Description: Handlers de 40 a 90 linhas validam o body, consultam o ORM, calculam atraso (`if t.due_date < datetime.utcnow(): if t.status != 'done' ...`), taxa de conclusão e montam o JSON campo a campo. `summary_report` tem 90 linhas de agregação dentro da rota.
Impact: Regra presa ao HTTP, impossível testar sem servidor; cada ajuste de regra exige editar vários handlers.
Recommendation: Rotas só mapeiam HTTP → controllers; regras em controllers/services; agregações em métodos de model/repositório (T-04).

### F-07 [HIGH] Camada "oficial" morta: validadores, helpers, service e dependências não usados
File: models/task.py:38-60 | models/user.py:34-38 | utils/helpers.py:9-116 | services/notification_service.py:1-48 | requirements.txt:4-6
Catalog: AP-14
Evidence: probe P12
Description: `Task.validate_status`, `Task.validate_priority`, `Task.is_overdue`, `User.is_admin`, `process_task_data`, `validate_email`, `is_valid_color`, `sanitize_string`, `generate_id`, `log_action`, `VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH` etc. nunca são chamados (busca por nome: zero usos fora da definição); `format_date`/`calculate_percentage` são importados em `routes/report_routes.py:7` e não usados. `NotificationService` não é importado por ninguém e instancia `smtplib.SMTP(...)` internamente (linha 15). `marshmallow`, `requests` e `python-dotenv` não são importados.
Impact: Duas fontes de verdade: as rotas reimplementam (com divergências) o que o model/helper já define — `is_valid_color` existe, mas `POST /categories` grava `"azul"` (P12).
Recommendation: Ativar a lógica útil no model/validators (status, prioridade, atraso, cor, e-mail), remover o resto e as dependências não usadas; o service de notificação morto é removido (T-04).

### F-08 [HIGH] Validação de tipos ausente: input malformado gera 500
File: routes/task_routes.py:92-100, 104, 113, 166-171, 181-184, 260-264 | routes/user_routes.py:61, 102-103, 106, 115, 124-125 | routes/report_routes.py:173-180, 196-202
Catalog: AP-17
Evidence: probe P6, probe P7, probe P8, probe P9, probe P10, probe P11, probe P12, probe P13, probe P15
Description: `if priority < 1` com string (`TypeError`), `len(title)` com número, `int(priority)` em query string sem tratamento, `'name' in data` com body `null`, `re.match(..., email)` com número, `user.active = data['active']` sem checar booleano, `color` sem validação e título só com espaços aceito. `PUT` valida menos que `POST` (nome vazio aceito em `PUT /users` e `PUT /categories`).
Impact: Um request malformado produz 500 (com o debugger exposto, F-03) em vez de 400; dados inválidos gravados no banco.
Recommendation: Validadores por entidade, compartilhados por criação e atualização, que checam presença, tipo e faixa e levantam erro de validação → 400 (T-11). Severidade elevada de MEDIUM para HIGH pela quantidade de endpoints afetados e pela combinação com F-03.

### F-09 [MEDIUM] Queries N+1 e contagens separadas
File: routes/task_routes.py:41-57, 275-287 | routes/user_routes.py:22 | routes/report_routes.py:15-30, 53-56, 161-163
Catalog: AP-15
Description: `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` por task em `GET /tasks`; `len(u.tasks)` lazy por usuário; `Task.query.filter_by(user_id=u.id)` por usuário no summary; `count()` por categoria; 9 `COUNT` separados por status/prioridade além de `Task.query.all()`.
Impact: O número de queries cresce linearmente com os dados (GET /tasks com 10 tasks faz 21 queries).
Recommendation: `joinedload`/`selectinload` nos relacionamentos e agregações com `GROUP BY` (T-08).

### F-10 [MEDIUM] Tratamento de erro disperso, genérico e com formatos diferentes
File: routes/task_routes.py:13, 62-63, 137, 151-154, 204, 221-223, 236-238 | routes/user_routes.py:87-90, 130-132, 149-151 | routes/report_routes.py:186-188, 207-209, 221-223 | utils/helpers.py:46, 49, 88
Catalog: AP-16
Evidence: probe P13, probe P14
Description: `except:` sem tipo em 11 pontos e `try/except` copiado em cada handler; não há `@app.errorhandler`. Erros saem como JSON `{error}`, HTML do debugger (500) ou HTML padrão do Flask (415/404/405).
Impact: `PUT /users/2 {"active":"nao"}` vira 500 "Erro ao atualizar" com a causa engolida (P13); clientes recebem formatos de erro imprevisíveis.
Recommendation: Exceções de domínio (`ValidationError`, `NotFoundError`, `ConflictError`, `AuthError`) e handler central que devolve sempre `{"error": ...}` em JSON (T-09).

### F-11 [MEDIUM] Código duplicado: regra de atraso, listas de valores, serialização e estatísticas
File: routes/task_routes.py:17-39, 71-80, 110, 140-144, 177, 209-213, 274-299 | routes/user_routes.py:61, 71, 106, 120, 162-180 | routes/report_routes.py:19-22, 33-37, 132-135 | models/task.py:23-36, 39, 50-60 | utils/helpers.py:21, 75, 101-106, 110-111
Catalog: AP-18
Description: A regra "vencida e não concluída/cancelada" aparece 7 vezes; `['pending', 'in_progress', 'done', 'cancelled']` 5 vezes; o regex de e-mail 3 vezes; papéis 3 vezes; o mapeamento task → dict é reescrito em `get_tasks` e `get_user_tasks` apesar de `Task.to_dict()`; `/tasks/stats` repete as contagens de `/reports/summary`.
Impact: Correções num lugar não chegam aos outros (ex.: `/tasks` e `/users/<id>/tasks` já divergem nas chaves).
Recommendation: Uma única regra no model (`Task.is_overdue`), constantes de domínio e serializadores reutilizados pelos controllers (T-04, T-11).

### F-12 [MEDIUM] [DEPRECATED] `Query.get()`, `datetime.utcnow()` e `backref`
File: routes/task_routes.py:31, 42, 51, 67, 72, 117, 122, 158, 188, 195, 215, 227, 285 | routes/user_routes.py:29, 94, 136, 155, 172 | routes/report_routes.py:35, 42, 45, 71, 105, 133, 192, 213 | models/task.py:15-16, 20-21, 52 | models/category.py:11 | models/user.py:14 | services/notification_service.py:35 | utils/helpers.py:38 | seed.py:66-74
Catalog: AP-19
Evidence: baseline (log de boot: `LegacyAPIWarning: The Query.get() method is considered legacy` e `DeprecationWarning: datetime.datetime.utcnow() is deprecated`)
Description: `User.query.get(id)` emite `LegacyAPIWarning` com SQLAlchemy 2.1.1; `datetime.utcnow()` é deprecated no Python 3.12; `db.relationship(..., backref='tasks')` é estilo legado.
Impact: Log poluído de warnings e quebra em futuras atualizações.
Recommendation: `db.session.get(Model, id)`, `datetime.now(timezone.utc)` (gravando naive UTC para manter o formato), `back_populates` (T-12).

### F-13 [MEDIUM] Logging com `print`
File: routes/task_routes.py:149, 153, 219, 234 | routes/user_routes.py:83, 89, 147 | utils/helpers.py:39-41 | services/notification_service.py:21, 24
Catalog: AP-20
Description: `print(f"Task criada: {task.id} - {task.title}")`, `print(f"ERRO: {str(e)}")` etc., sem `logging`.
Impact: Sem níveis nem destino configurável; erros reais misturados com ruído.
Recommendation: `logging.getLogger(__name__)` com nível configurável (T-14).

### F-14 [MEDIUM] Configuração HTTP e de runtime fixa no código
File: app.py:11, 15, 30-31, 34
Catalog: AP-21
Description: `CORS(app)` libera qualquer origem; `sqlite:///tasks.db` e `port=5000` fixos; `db.create_all()` roda como efeito colateral do import de `app`.
Impact: Não dá para trocar porta/banco por ambiente (a baseline precisou editar a cópia); qualquer site chama a API pelo navegador.
Recommendation: Config por ambiente (`PORT`, `DATABASE_URL`, `CORS_ORIGINS`) e `create_app()` como composition root (T-01, T-16).

### F-15 [MEDIUM] Baixa coesão: CRUD de categorias em `report_routes.py` e `utils` genérico
File: routes/report_routes.py:157-223 | utils/helpers.py:9-116
Catalog: AP-26
Description: `GET/POST/PUT/DELETE /categories` estão no módulo de relatórios; `helpers.py` mistura formatação de data, validação de e-mail, geração de UUID, log, regras de task e constantes de domínio.
Impact: Quem procura o domínio "categorias" não o encontra; mudanças num domínio mexem em arquivo de outro.
Recommendation: Um módulo por domínio (views/controllers/validators de categoria) e remoção do `utils` genérico (T-18).

### F-16 [LOW] Magic numbers e strings
File: routes/task_routes.py:96, 99, 104, 113, 167, 169, 182 | routes/user_routes.py:64, 115, 210 | routes/report_routes.py:24-28, 45, 84-88, 129, 180
Catalog: AP-22
Description: Limites `3`/`200` de título, prioridade `1..5` e `<= 2` como "alta", senha `4`, `timedelta(days=7)`, `'#000000'`, prefixo `'fake-jwt-token-'`.
Impact: Regras implícitas espalhadas.
Recommendation: Constantes de domínio nomeadas (T-13).

### F-17 [LOW] Imports não usados
File: app.py:7 | routes/task_routes.py:7 | routes/user_routes.py:6 | routes/report_routes.py:7-8 | models/task.py:3 | utils/helpers.py:3-7
Catalog: AP-24
Description: `import os, sys, json` (app), `import json, os, sys, time` (tasks), `hashlib, json` (users), `format_date, calculate_percentage, json` (reports), `json` (model task), `os, json, sys, math, hashlib` (helpers).
Impact: Ruído que sugere dependências inexistentes.
Recommendation: Remover (T-13).

### F-18 [LOW] Condicionais aninhadas e `if cond: return True else: return False`
File: routes/task_routes.py:30-39, 71-80, 284-287 | routes/user_routes.py:171-180 | routes/report_routes.py:34-36, 119-127, 132-135 | models/task.py:39-43, 46-48, 51-60 | models/user.py:35-38
Catalog: AP-25
Description: Três níveis de `if` para decidir `overdue`; cadeia `if t.status == 'done': ... elif 'pending' ... elif ...` para contar status; `if self.role == 'admin': return True else: return False`.
Impact: Regra escondida no fluxo e cópias divergentes.
Recommendation: Expressão booleana direta e contagem por dicionário/`GROUP BY` (T-17b, T-17c).

### F-19 [LOW] Nomes ruins
File: routes/report_routes.py:24-28 | models/category.py:14 | utils/helpers.py:83 | routes/task_routes.py:141, 210
Catalog: AP-23
Description: `p1`…`p5` para contagens por prioridade, `d` para o dict da categoria, `p` para prioridade; `type(tags) == list` em vez de `isinstance`.
Impact: Leitura lenta.
Recommendation: Nomes descritivos e `isinstance` (T-13).

## Deprecated APIs

| API | Onde | Equivalente moderno |
|---|---|---|
| `Model.query.get(id)` (LegacyAPIWarning, SQLAlchemy 2.1.1) | routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227; routes/user_routes.py:29, 94, 136, 155; routes/report_routes.py:105, 192, 213 | `db.session.get(Model, id)` |
| `datetime.utcnow()` (DeprecationWarning, Python 3.12) | models/task.py:15-16, 52; models/category.py:11; models/user.py:14; routes/*; utils/helpers.py:38; services/notification_service.py:35; seed.py:66-74 | `datetime.now(timezone.utc)` |
| `relationship(..., backref=...)` (legado) | models/task.py:20-21 | `back_populates` em ambos os lados |
| `Model.query.filter_by(...)` (estilo 1.x, sem warning) | routes/* | `db.select(Model).where(...)` — recomendação, sem severidade própria |

## Architecture Overview

- **Current:** Parcialmente em camadas — há `models/`, `routes/`, `services/`, `utils/`, mas as rotas concentram validação, queries, regra e serialização; service e helpers estão mortos; não existem controllers nem config.
- **Target:** `app.py` (launcher fino, mantém `python app.py`) + `src/` com `app.py` (`create_app`, composition root), `config/settings.py`, `database/` (extensão ORM + seed), `models/<entidade>_model.py`, `controllers/<entidade>_controller.py`, `views/<entidade>_routes.py` + `views/presenters.py`, `middlewares/` (`error_handler.py`, `auth.py`).

```
================================
Total: 19 findings
================================
```
