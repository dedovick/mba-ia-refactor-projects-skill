# Baseline — task-manager-api (2026-09-27)
Run command: `python seed.py && python app.py` | Port used: 61193 (literal `port=5000` trocado **só na cópia temporária**) | Boot: OK | Warnings: `DeprecationWarning: datetime.utcnow()` (routes/*, models/*, seed.py), `LegacyAPIWarning: Query.get()` (routes/*), `Debug mode: on` + `Debugger is active!` + bind `0.0.0.0`

Stack instalada: Python 3.12.0, Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.1 (transitiva, não fixada), Werkzeug 3.1.8.

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | GET / | 200 | {message, version} |
| 2 | GET /health | 200 | {status, timestamp} |
| 3 | GET /tasks | 200 | [category_id, category_name, created_at, description, due_date, id, overdue, priority, status, tags, title, updated_at, user_id, user_name] (len 10) |
| 4 | GET /tasks/1 | 200 | {category_id, created_at, description, due_date, id, overdue, priority, status, tags, title, updated_at, user_id} |
| 5 | GET /tasks/999 | 404 | {error} |
| 6 | GET /tasks/search?q=API | 200 | [category_id, created_at, description, due_date, id, priority, status, tags, title, updated_at, user_id] (len 2) |
| 7 | GET /tasks/search?status=pending&priority=1 | 200 | [category_id, created_at, description, due_date, id, priority, status, tags, title, updated_at, user_id] (len 2) |
| 8 | GET /tasks/stats | 200 | {cancelled, completion_rate, done, in_progress, overdue, pending, total} |
| 9 | GET /users | 200 | [active, created_at, email, id, name, role, task_count] (len 3) |
| 10 | GET /users/1 | 200 | {active, created_at, email, id, name, password, role, tasks: [category_id, created_at, description, due_date, id, priority, status, tags, title, updated_at, user_id]} |
| 11 | GET /users/999 | 404 | {error} |
| 12 | GET /users/1/tasks | 200 | [created_at, description, due_date, id, overdue, priority, status, title] (len 4) |
| 13 | GET /users/999/tasks | 404 | {error} |
| 14 | GET /reports/summary | 200 | {generated_at, overdue: {count, tasks}, overview: {total_categories, total_tasks, total_users}, recent_activity: {tasks_completed_last_7_days, tasks_created_last_7_days}, tasks_by_priority: {critical, |
| 15 | GET /reports/user/1 | 200 | {statistics: {cancelled, completion_rate, done, high_priority, in_progress, overdue, pending, total_tasks}, user: {email, id, name}} |
| 16 | GET /reports/user/999 | 404 | {error} |
| 17 | GET /categories | 200 | [color, created_at, description, id, name, task_count] (len 4) |
| 18 | POST /tasks (válido) | 201 | {category_id, created_at, description, due_date, id, priority, status, tags, title, updated_at, user_id} |
| 19 | POST /tasks {} | 400 | {error} |
| 20 | POST /tasks {"title":"ab"} | 400 | {error} |
| 21 | POST /tasks status inválido | 400 | {error} |
| 22 | POST /tasks user_id=999 | 404 | {error} |
| 23 | POST /tasks due_date inválida | 400 | {error} |
| 24 | PUT /tasks/11 {"status":"in_progress","priority":4} | 200 | {category_id, created_at, description, due_date, id, priority, status, tags, title, updated_at, user_id} |
| 25 | PUT /tasks/999 | 404 | {error} |
| 26 | POST /users (válido) | 201 | {active, created_at, email, id, name, password, role} |
| 27 | POST /users email duplicado | 409 | {error} |
| 28 | POST /users sem senha | 400 | {error} |
| 29 | PUT /users/4 {"name":"Ana B"} | 200 | {active, created_at, email, id, name, password, role} |
| 30 | PUT /users/999 | 404 | {error} |
| 31 | POST /login (válido joao/1234) | 200 | {message, token, user: {active, created_at, email, id, name, password, role}} |
| 32 | POST /login senha errada | 401 | {error} |
| 33 | POST /login sem campos | 400 | {error} |
| 34 | POST /categories (válido) | 201 | {color, created_at, description, id, name} |
| 35 | POST /categories {} | 400 | {error} |
| 36 | PUT /categories/5 {"description":"x"} | 200 | {color, created_at, description, id, name} |
| 37 | PUT /categories/999 | 404 | {error} |
| 38 | DELETE /tasks/11 | 200 | {message} |
| 39 | DELETE /tasks/999 | 404 | {error} |
| 40 | DELETE /categories/5 | 200 | {message} |
| 41 | DELETE /categories/999 | 404 | {error} |
| 42 | DELETE /users/4 | 200 | {message} |
| 43 | DELETE /users/999 | 404 | {error} |

## Probes

| # | Categoria | Request | Observado | Esperado | Veredito |
|---|---|---|---|---|---|
| P1 | Exposição | GET /users/1 | 200, resposta inclui `password` (hash MD5 sem salt `81dc9bdb…` = md5("1234")) | campo ausente | VULNERÁVEL |
| P2 | Exposição | POST /login joao/1234 | 200, `user.password` com hash + `token: "fake-jwt-token-1"` previsível | sem hash; token real ou nenhum | VULNERÁVEL |
| P3 | Autorização | POST /users {"role":"admin"} sem credencial | 201, admin criado; resposta devolve o hash | 401/403 (ou role ignorado) | VULNERÁVEL |
| P4 | Autenticação | POST /login {"email":"' OR '1'='1"} | 401 | 401 | OK |
| P5 | Injeção | GET /tasks/search?q=' OR '1'='1 | 200, [] (lido literalmente pelo ORM) | 200 literal | OK |
| P6 | Tipos | POST /tasks {"title":"xyz","priority":"abc"} | 500 HTML do debugger Werkzeug (TypeError + traceback) | 400 | VULNERÁVEL |
| P7 | Tipos | POST /tasks {"title":123} | 500 HTML debugger (TypeError len(int)) | 400 | VULNERÁVEL |
| P8 | Tipos | PUT /tasks/1 {"priority":"5"} | 500 HTML debugger (TypeError) | 400 | VULNERÁVEL |
| P9 | Tipos | GET /tasks/search?priority=abc | 500 HTML debugger (ValueError int()) | 400 | VULNERÁVEL |
| P10 | Tipos | PUT /categories/1 body `null` | 500 HTML debugger (TypeError: argument of type NoneType) | 400 | VULNERÁVEL |
| P11 | Tipos | POST /users {"email":123} | 500 HTML debugger (TypeError re.match) | 400 | VULNERÁVEL |
| P12 | Tipos | POST /categories {"color":"azul"} | 201, cor inválida gravada | 400 | VULNERÁVEL |
| P13 | Tipos | PUT /users/2 {"active":"nao"} | 500 {"error":"Erro ao atualizar"} (exceção engolida por `except:`) | 400 | VULNERÁVEL |
| P14 | Tipos | POST /tasks Content-Type text/plain | 415 HTML padrão do Flask | 400/415 | OK |
| P15 | Tipos | POST /tasks {"title":"   "} | 201, task com título só de espaços | 400 | VULNERÁVEL |
| P16 | Identidade | PUT /users/1 {"password":"hacked"} sem credencial; depois POST /login joao/hacked | 200 senha do admin trocada; login com "hacked" → 200 | 401/403; nada alterado | VULNERÁVEL |
| P17 | Autorização | DELETE /users/3 sem credencial | 200, usuário e suas tasks apagados | 401/403 | VULNERÁVEL |
| P18 | Consistência | DELETE /categories/1 com tasks vinculadas; GET /tasks/1 | 200; task 1 ficou com `category_id: null` (ORM desvincula) | sem órfãos | OK |
| P19 | Exposição | server.log (grep password/senha/md5) e respostas 500 | log sem segredos; porém respostas 500 expõem traceback + código-fonte via debugger interativo (PIN impresso no log) | sem traceback ao cliente | VULNERÁVEL |

**Resumo:** 43/43 requisições responderam; 19 sondas, 15 VULNERÁVEIS.
