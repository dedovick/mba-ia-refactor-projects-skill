# Validation Results — task-manager-api (2026-09-27)

Run command: `python seed.py && PORT=62406 python app.py` (mesmo comando de antes; porta via ambiente) | Boot: OK

Log de boot:
```
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:62406
```
Warnings novos: nenhum. `LegacyAPIWarning: Query.get()` e `DeprecationWarning: datetime.utcnow()` da linha de base sumiram (`python -W default`). O log não tem nenhuma ocorrência de password/hash/token.

## Requisições da linha de base (antes × depois)

Comparados: status, chaves e **valores** (desconsiderando timestamps e o token).

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| 1 | GET / | 200 {message, version} | 200 {message, version} | ✓ Igual |
| 2 | GET /health | 200 {status, timestamp} | 200 {status, timestamp} | ✓ Igual |
| 3 | GET /tasks | 200 [category_id, category_name, created_at, description, due_date, id, ov | 200 [category_id, category_name, created_at, description, due_date, id, ov | ✓ Igual |
| 4 | GET /tasks/1 | 200 {category_id, created_at, description, due_date, id, overdue, priority | 200 {category_id, created_at, description, due_date, id, overdue, priority | ✓ Igual |
| 5 | GET /tasks/999 | 404 {error} | 404 {error} | ✓ Igual |
| 6 | GET /tasks/search?q=API | 200 [category_id, created_at, description, due_date, id, priority, status, | 200 [category_id, created_at, description, due_date, id, priority, status, | ✓ Igual |
| 7 | GET /tasks/search?status=pending&priority=1 | 200 [category_id, created_at, description, due_date, id, priority, status, | 200 [category_id, created_at, description, due_date, id, priority, status, | ✓ Igual |
| 8 | GET /tasks/stats | 200 {cancelled, completion_rate, done, in_progress, overdue, pending, tota | 200 {cancelled, completion_rate, done, in_progress, overdue, pending, tota | ✓ Igual |
| 9 | GET /users | 200 [active, created_at, email, id, name, role, task_count] (len 3) | 200 [active, created_at, email, id, name, role, task_count] (len 3) | ✓ Igual |
| 10 | GET /users/1 | 200 {active, created_at, email, id, name, password, role, tasks: [category | 200 {active, created_at, email, id, name, role, tasks: [category_id, creat | ✓ Mudança esperada (campo `password` removido) |
| 11 | GET /users/999 | 404 {error} | 404 {error} | ✓ Igual |
| 12 | GET /users/1/tasks | 200 [created_at, description, due_date, id, overdue, priority, status, tit | 200 [created_at, description, due_date, id, overdue, priority, status, tit | ✓ Igual |
| 13 | GET /users/999/tasks | 404 {error} | 404 {error} | ✓ Igual |
| 14 | GET /reports/summary | 200 {generated_at, overdue: {count, tasks}, overview: {total_categories, t | 200 {generated_at, overdue: {count, tasks}, overview: {total_categories, t | ✓ Igual |
| 15 | GET /reports/user/1 | 200 {statistics: {cancelled, completion_rate, done, high_priority, in_prog | 200 {statistics: {cancelled, completion_rate, done, high_priority, in_prog | ✓ Igual |
| 16 | GET /reports/user/999 | 404 {error} | 404 {error} | ✓ Igual |
| 17 | GET /categories | 200 [color, created_at, description, id, name, task_count] (len 4) | 200 [color, created_at, description, id, name, task_count] (len 4) | ✓ Igual |
| 18 | POST /tasks (válido) | 201 {category_id, created_at, description, due_date, id, priority, status, | 201 {category_id, created_at, description, due_date, id, priority, status, | ✓ Igual |
| 19 | POST /tasks {} | 400 {error} | 400 {error} | ✓ Igual |
| 20 | POST /tasks {"title":"ab"} | 400 {error} | 400 {error} | ✓ Igual |
| 21 | POST /tasks status inválido | 400 {error} | 400 {error} | ✓ Igual |
| 22 | POST /tasks user_id=999 | 404 {error} | 404 {error} | ✓ Igual |
| 23 | POST /tasks due_date inválida | 400 {error} | 400 {error} | ✓ Igual |
| 24 | PUT /tasks/11 {"status":"in_progress","priority":4} | 200 {category_id, created_at, description, due_date, id, priority, status, | 200 {category_id, created_at, description, due_date, id, priority, status, | ✓ Igual |
| 25 | PUT /tasks/999 | 404 {error} | 404 {error} | ✓ Igual |
| 26 | POST /users (válido) | 201 {active, created_at, email, id, name, password, role} | 201 {active, created_at, email, id, name, role} | ✓ Mudança esperada (campo `password` removido) |
| 27 | POST /users email duplicado | 409 {error} | 409 {error} | ✓ Igual |
| 28 | POST /users sem senha | 400 {error} | 400 {error} | ✓ Igual |
| 29 | PUT /users/4 {"name":"Ana B"} | 200 {active, created_at, email, id, name, password, role} | 200 {active, created_at, email, id, name, role} | ✓ Mudança esperada (campo `password` removido) |
| 30 | PUT /users/999 | 404 {error} | 404 {error} | ✓ Igual |
| 31 | POST /login (válido joao/1234) | 200 {message, token, user: {active, created_at, email, id, name, password, | 200 {message, token, user: {active, created_at, email, id, name, role}} | ✓ Mudança esperada (campo `password` removido) |
| 32 | POST /login senha errada | 401 {error} | 401 {error} | ✓ Igual |
| 33 | POST /login sem campos | 400 {error} | 400 {error} | ✓ Igual |
| 34 | POST /categories (válido) | 201 {color, created_at, description, id, name} | 201 {color, created_at, description, id, name} | ✓ Igual |
| 35 | POST /categories {} | 400 {error} | 400 {error} | ✓ Igual |
| 36 | PUT /categories/5 {"description":"x"} | 200 {color, created_at, description, id, name} | 200 {color, created_at, description, id, name} | ✓ Igual |
| 37 | PUT /categories/999 | 404 {error} | 404 {error} | ✓ Igual |
| 38 | DELETE /tasks/11 | 200 {message} | 200 {message} | ✓ Igual |
| 39 | DELETE /tasks/999 | 404 {error} | 404 {error} | ✓ Igual |
| 40 | DELETE /categories/5 | 200 {message} | 200 {message} | ✓ Igual |
| 41 | DELETE /categories/999 | 404 {error} | 404 {error} | ✓ Igual |
| 42 | DELETE /users/4 (com token admin) | 200 {message} | 200 {message} | ✓ Igual |
| 43 | DELETE /users/999 | 404 {error} | 404 {error} | ✓ Igual |

**43/43** iguais à linha de base, ou com a mudança esperada. `DELETE /users/4` sem token agora responde 401 (mudança esperada, ver Contract changes) e com token de admin responde 200, como antes.

## Sondas (antes → depois)

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| P1 | Exposição: GET /users/1 (campo password?) | 200 VULNERÁVEL | 200 {active, created_at, email, id, name, role, tasks: sem `password` | OK |
| P2 | Exposição: POST /login válido (password/hash na resposta?) | 200 VULNERÁVEL | 200 {message, token, user: {active, created_at, email, sem `password`; token assinado | OK |
| P3 | Exposição+Autorização: POST /users {"role":"admin"} sem credencial | 201 VULNERÁVEL | 401 {error}  | OK |
| P4 | Autenticação: POST /login email="' OR '1'='1" | 401 OK | 401 {error}  | OK |
| P5 | Injeção: GET /tasks/search?q=' OR '1'='1 | 200 OK | 200 list len 0  | OK |
| P6 | Tipos: POST /tasks {"title":"xyz","priority":"abc"} | 500 VULNERÁVEL | 400 {error}  | OK |
| P7 | Tipos: POST /tasks {"title":123} | 500 VULNERÁVEL | 400 {error}  | OK |
| P8 | Tipos: PUT /tasks/1 {"priority":"5"} | 500 VULNERÁVEL | 400 {error}  | OK |
| P9 | Tipos: GET /tasks/search?priority=abc | 500 VULNERÁVEL | 400 {error}  | OK |
| P10 | Tipos: PUT /categories/1 body null | 500 VULNERÁVEL | 400 {error}  | OK |
| P11 | Tipos: POST /users {"email":123} | 500 VULNERÁVEL | 400 {error}  | OK |
| P12 | Tipos: POST /categories {"color":"azul"} | 201 VULNERÁVEL | 400 {error}  | OK |
| P13 | Tipos: PUT /users/2 {"active":"nao"} | 500 VULNERÁVEL | 401 {error} 401 sem token; com token admin → 400 (X8) | OK |
| P14 | Tipos: POST /tasks sem Content-Type JSON | 415 OK | 415 {error} JSON `{error}` em vez de HTML | OK |
| P15 | Tipos: POST /tasks {"title":"   "} (só espaços) | 201 VULNERÁVEL | 400 {error}  | OK |
| P16 | Identidade: PUT /users/1 {"password":"hacked"} sem credencial | 200 VULNERÁVEL | 401 {error}  | OK |
| P16b | Identidade: POST /login joao/hacked após P16 | 200 VULNERÁVEL | 401 {error} login com "hacked" recusado | OK |
| P17 | Autorização: DELETE /users/3 sem credencial | 200 VULNERÁVEL | 401 {error}  | OK |
| P18 | Consistência: DELETE /categories/1 com tasks vinculadas | 200 OK | 200 {message}  | OK |
| P18b | Consistência: GET /tasks/1 após P18 (category_id) | 200 OK | 200 {category_id, created_at, description, due_date, i `category_id: null` | OK |
| P19 | Traceback/debugger nas respostas 500 e segredos no log | VULNERÁVEL | Debug off; erros saem como JSON `{error}`; log sem segredos | OK |

15/15 sondas que eram VULNERÁVEIS agora estão OK, e as 4 que já estavam OK continuam OK.

## Verificações extras de autorização e robustez

| # | Request | Status | Resposta |
|---|---|---|---|
| DELETE | DELETE /users/4 sem token | 401 | {error} |
| X1 | X1 PUT /users/1 {"password"} com token de outro usuário (maria) | 403 | {error} |
| X2 | X2 PUT /users/2 {"password":"nova"} com o próprio token (maria) | 200 | {active, created_at, email, id, name, role} |
| X3 | X3 POST /users {"role":"admin"} com token admin | 201 | {active, created_at, email, id, name, role} |
| X4 | X4 PUT /users/2 {"active":false} com token de user (maria) | 403 | {error} |
| X5 | X5 DELETE /users/3 com token forjado | 401 | {error} |
| X6 | X6 DELETE /users/3 com token admin | 200 | {message} |
| X8 | X8 PUT /users/2 {"active":"nao"} com token admin | 400 | {error} |
| X9 | X9 PUT /tasks/1 {"tags":[1,2]} | 400 | {error} |
| X10 | X10 POST /tasks corpo JSON malformado | 400 | {error} |
| X7 | X7 GET /rota-inexistente | 404 | {error} |

## Varredura do catálogo nos arquivos novos

- Nenhum `except:` genérico, `print` em código de requisição, `utcnow`, `Query.get`, `debug=True` nem `backref`.
- Segredos: nenhum literal. As senhas em `src/database/seed.py` são fixtures do seed. `TOKEN_SALT` é um namespace, não um segredo.
- `md5` só aparece em `src/models/user_model.py:33`, para verificar e **trocar** hashes legados no login.
- pyflakes: só o import intencional de models em `src/database/connection.py:20` (marcado `noqa`).

## Não resolvido

- Política de senha mínima de 4 caracteres mantida (`MIN_PASSWORD_LENGTH`): as senhas do seed têm 4 caracteres, e aumentar o mínimo é uma decisão de produto.
