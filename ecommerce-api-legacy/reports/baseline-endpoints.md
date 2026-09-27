# Baseline — ecommerce-api-legacy (2026-09-27)
Run command: `npm start` (`node src/app.js`) | Port used: 61060 (literal `port: 3000` in `src/utils.js:6` changed **only in the temporary copy**) | Boot: OK | Warnings: none (`node --trace-deprecation --trace-warnings`, Node v25.8.2)

Database: SQLite `:memory:`, seeded at boot. Every restart (including crashes) resets the data.
Order of courses in `GET /api/admin/financial-report` is **non-deterministic** (it changed between requests 1, 6 and P2).

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | GET /api/admin/financial-report | 200 json | `[{course, revenue, students: [{student, paid}]}]` — Docker 0 / Clean Architecture 997 (Leonan) |
| 2 | POST /api/checkout `{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}` | 200 json | `{msg: "Sucesso", enrollment_id: 2}` |
| 3 | POST /api/checkout `{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}` | 400 text/html | `Pagamento recusado` |
| 4 | POST /api/checkout `{"usr":"X","eml":"x@x.com"}` (incompleto) | 400 text/html | `Bad Request` |
| 5 | POST /api/checkout `{... "c_id":999, "card":"4111"}` | 404 text/html | `Curso não encontrado` |
| 6 | GET /api/admin/financial-report | 200 json | same shape; Docker 497 (Guilherme), Clean Architecture 997 (Leonan) |

## Probes

| # | Categoria | Request | Observado | Esperado | Veredito |
|---|---|---|---|---|---|
| P1 | Identidade | POST /api/checkout `{"usr":"Invasor","eml":"leonan@fullcycle.com.br","pwd":"senha-errada","c_id":2,"card":"4111..."}` | 200 `{msg, enrollment_id: 3}`; the enrollment and payment were created **on Leonan's account** (the P2 report shows Leonan under Docker) | 401, nothing created | VULNERÁVEL |
| P2 | Autorização | GET /api/admin/financial-report (no credential) | 200 with the full revenue report and student names | 401/403 | VULNERÁVEL |
| P3 | Injeção | POST /api/checkout `{"usr":"O'Brien","eml":"' OR '1'='1","c_id":"1 OR 1=1",...}` | 404 `Curso não encontrado` (param bound literally, no extra data) | normal / 400 | OK |
| P4 | Tipos | POST /api/checkout `"card": 4111222233334444` (number) | **process crashed** (`TypeError: cc.startsWith is not a function`, AppManager.js:46); curl got no response; the in-memory DB was lost on restart; user `t1@t.com` was inserted before the crash | 400 | VULNERÁVEL |
| P5 | Tipos | POST /api/checkout `"card": {"n":"4"}` (object) | **process crashed** (same TypeError) | 400 | VULNERÁVEL |
| P6 | Tipos | POST /api/checkout `"usr": 123, "eml": ["a"]` | 200, user created with name `123` and email bound from an array | 400 | VULNERÁVEL |
| P7 | Tipos / Exposição | POST /api/checkout body `null` | 400 text/html with **stack trace and absolute server paths** (`/private/var/.../node_modules/body-parser/...`) | 400 with a clean message, no stack | VULNERÁVEL |
| P8 | Consistência | POST checkout denied (`"usr":"Fantasma","eml":"ghost@t.com","card":"5111"`), then a successful checkout with the same email and `"usr":"Real"`, then GET report | Denied → 400, **but the user "Fantasma" was persisted**: the report lists `Fantasma`, not `Real` | failed operation writes nothing | VULNERÁVEL |
| P9 | Inexistentes | DELETE /api/users/999 | 200 `Usuário deletado, mas...` (nothing deleted) | 404 | VULNERÁVEL |
| P10 | Autorização | DELETE /api/users/2 (no credential) | 200, user deleted | 401/403 | VULNERÁVEL |
| P11 | Consistência | DELETE /api/users/1, then GET report | 200; the report now shows `{"student":"Unknown","paid":997}` → orphaned enrollments/payments still counted as revenue | cascade or refusal; no orphans | VULNERÁVEL |
| P12 | Exposição (log) | `grep` for card number / gateway key in server.log | 8 matches: `Processando cartão 4111222233334444 na chave pk_live_1234567890abcdef` on every checkout | absent | VULNERÁVEL |
| P13 | Exposição (resposta) | Password/hash fields in responses | none returned (report only has name and amount) | absent | OK |

Summary: 13 probes, 11 VULNERÁVEL, 2 OK.
