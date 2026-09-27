# Validation Results — ecommerce-api-legacy (2026-09-27)

Run command: `npm start` (now `node src/server.js`) | Port: 62987 via `PORT` env (no code change needed) | Env: `ADMIN_TOKEN=test-admin-token` | Node v25.8.2 with `NODE_OPTIONS="--trace-deprecation --trace-warnings"`

## Boot log

```
[2026-09-27T15:27:24.932Z] [warn] PAYMENT_GATEWAY_KEY não definida: usando o gateway simulado.
[2026-09-27T15:27:24.936Z] [info] Frankenstein LMS rodando na porta 62987...
```

No errors and no Node runtime/deprecation warnings (`node:sqlite` emits no ExperimentalWarning on v25.8.2). The `[warn]` line is an intentional application log about missing config, not a runtime warning.
Extra check: two boots with `DB_FILENAME=<file>` returned the same seeded report (schema `IF NOT EXISTS` + seed only when empty → idempotent).

## Baseline × after

| # | Request | Baseline | After | Verdict |
|---|---|---|---|---|
| 1 | GET /api/admin/financial-report | 200 `[{course, revenue, students:[{student, paid}]}]` | 200 same shape and content; now sent with `X-Admin-Token` | ✓ Mudança esperada (auth); order now fixed by course id (was non-deterministic) |
| 2 | POST /api/checkout (Guilherme, c_id 2, card 4111…) | 200 `{msg:"Sucesso", enrollment_id:2}` | 200 `{msg:"Sucesso", enrollment_id:2}` | ✓ Igual |
| 3 | POST /api/checkout (João, card 5111…) | 400 `Pagamento recusado` | 400 `Pagamento recusado` | ✓ Igual |
| 4 | POST /api/checkout incompleto | 400 `Bad Request` | 400 `Bad Request` | ✓ Igual |
| 5 | POST /api/checkout c_id 999 | 404 `Curso não encontrado` | 404 `Curso não encontrado` | ✓ Igual |
| 6 | GET /api/admin/financial-report | 200, Docker 497 (Guilherme), CA 997 (Leonan) | 200, same content | ✓ Igual (with token) |

6/6 match the baseline (with the expected auth header).

## Probes before → after

| # | Categoria | Baseline | After | Verdict |
|---|---|---|---|---|
| P1 | Identidade (e-mail existente + senha errada) | 200, matrícula criada na conta de Leonan | 401 `Credenciais inválidas`, nothing charged or written (no payment log line) | VULNERÁVEL → OK |
| P1b | Identidade (e-mail existente sem `pwd`) | — (new) | 400 `Bad Request` | OK |
| P1c | Dono da conta com senha correta | — (new, regression check) | 200 `{msg, enrollment_id}` | OK |
| P2 | Autorização: report sem token | 200 relatório completo | 401 `Não autorizado` | VULNERÁVEL → OK |
| P2b | Autorização: report com token errado | — (new) | 403 `Acesso negado` | OK |
| P3 | Injeção (`c_id: "1 OR 1=1"`, `eml: "' OR '1'='1"`) | 404 | 400 `Bad Request` (type validation) | OK → OK |
| P3b | Injeção: apóstrofos em `usr`/`eml` válidos | — (new) | 200, stored literally | OK |
| P4 | Tipos: `card` número | processo caiu | 400 `Bad Request`, process up | VULNERÁVEL → OK |
| P5 | Tipos: `card` objeto | processo caiu | 400 `Bad Request`, process up | VULNERÁVEL → OK |
| P6 | Tipos: `usr` número, `eml` array | 200, gravado | 400 `Bad Request` | VULNERÁVEL → OK |
| P7 | Body `null` | 400 with stack trace + server paths | 400 `Bad Request` (plain text, no stack) | VULNERÁVEL → OK |
| P8 | Consistência: pagamento recusado grava usuário | "Fantasma" persisted | report shows `Real` (the denied attempt wrote nothing) | VULNERÁVEL → OK |
| P9 | DELETE /api/users/999 | 200 "Usuário deletado…" | 404 `Usuário não encontrado` | VULNERÁVEL → OK |
| P9b | DELETE /api/users/abc | 200 (nothing deleted) | 400 `Bad Request` | OK |
| P10 | DELETE sem token | 200, usuário removido | 401 `Não autorizado` | VULNERÁVEL → OK |
| P11 | DELETE usuário 1 → report | orphans shown as `Unknown` and counted as revenue | Leonan's enrollment/payment removed with him; no `Unknown`, CA revenue 1994 → 997 | VULNERÁVEL → OK |
| P12 | Cartão/chave no log | 8 ocorrências | 0 (cards logged as `**** 4444`, key never logged) | VULNERÁVEL → OK |
| P13 | Senha/hash em respostas | ausente | ausente | OK → OK |

11/11 previously vulnerable probes are now OK.

## Catalog re-scan (new files)

- Hardcoded secrets: none (`grep` matched only the header name `X-Admin-Token`).
- String-built SQL: none; every query uses `prepare(...).run/get/all(params)`.
- `console.*`: only inside `src/config/logger.js`.
- Callbacks with ignored `err` / empty `catch`: none (sync `node:sqlite` + central `errorHandler`).
- `req`/`res` below views: none in models, services or controllers.
- The CRITICAL and HIGH findings F-01…F-12 are resolved (see the final summary).

## Not verified / remaining

- The generic 500 path (`Erro interno`) was not triggered at runtime; it is covered only by code review.
- `engines: node >=22.13`: on Node 22.x `node:sqlite` emits an ExperimentalWarning. Only v25.8.2 was tested.
