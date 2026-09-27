# Validation Results — ecommerce-api-legacy (2026-09-27)

Run command: `npm start` → `node src/server.js` | Port: 60379 (`PORT` do ambiente), `ADMIN_TOKEN=t0k3n` | Node v25.8.2 | `npm ci` numa cópia temporária

## Log de boot

```
2026-09-27T14:55:13.807Z [INFO] LMS API rodando na porta 60379
2026-09-27T14:55:15.276Z [INFO] Processando pagamento de 497 com cartão **** 4444
```

`node --trace-deprecation`: nenhum warning. O cartão aparece mascarado e a chave do gateway não é mais logada. Sem `ADMIN_TOKEN`, o boot emite `[WARN] ADMIN_TOKEN não configurado...` (intencional, testado com `npm start`).

## Antes × depois (mesma sequência da linha de base; rotas admin com `X-Admin-Token`)

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| 1 | GET /api/admin/financial-report | 200 `[{course, revenue, students}]` | 200, mesmo formato e valores | ✓ Igual (ordem dos cursos agora determinística, por id) |
| 2 | POST /api/checkout (Guilherme, cartão 4…) | 200 `{msg, enrollment_id: 2}` | 200 `{msg, enrollment_id: 2}` | ✓ Igual |
| 3 | POST /api/checkout (cartão 5…) | 400 `Pagamento recusado` | 400 `Pagamento recusado` | ✓ Igual (e nenhum usuário é criado) |
| 4 | POST /api/checkout (campos faltando) | 400 `Bad Request` | 400 `Bad Request` | ✓ Igual |
| 5 | POST /api/checkout c_id 999 | 404 `Curso não encontrado` | 404 `Curso não encontrado` | ✓ Igual |
| 6 | POST /api/checkout (usuário existente) | 200 `{msg, enrollment_id: 3}` | 200 `{msg, enrollment_id: 3}` | ✓ Igual |
| 7 | GET /api/admin/financial-report | 200, CA 997 / Docker 994 | 200, idêntico | ✓ Igual |
| 8 | DELETE /api/users/1 | 200 mensagem | 200 mesma mensagem | ✓ Igual |
| 9 | DELETE /api/users/999 | 200 mensagem | 200 mesma mensagem | ✓ Igual |
| 10 | GET /api/admin/financial-report | 200 com `"Unknown"` | 200, idêntico | ✓ Igual |
| 11 | GET /api/nao-existe | 404 página padrão Express | 404 idêntico | ✓ Igual |

**11/11 iguais à linha de base.**

## Verificações extras

| Request | Antes | Depois | Veredito |
|---|---|---|---|
| GET /api/admin/financial-report sem token | 200 | 401 `Não autorizado` | ✓ Mudança esperada (segurança) |
| DELETE /api/users/2 sem token | 200 | 401 `Não autorizado` | ✓ Mudança esperada (segurança) |
| GET relatório com token errado | 200 | 401 | ✓ Mudança esperada (segurança) |
| POST /api/checkout `"card": 4111` (número) | **processo derrubado** (`TypeError: cc.startsWith`) | 400 `Bad Request`, servidor segue no ar | ✓ Correção de bug |
| POST /api/checkout com JSON inválido | 400 com página de erro do Express (stack) | 400 `Bad Request` | ✓ Correção de bug |
| Checkout recusado com `DB_PATH` em arquivo | usuário criado mesmo assim | tabela `users` só com o seed; senha do seed em `scrypt$…` | ✓ Correção de bug |

## Varredura do catálogo nos arquivos novos

- Segredos hardcoded: nenhum (`SEED_PASSWORD = '123'` é fixture do seed, gravada com hash; `ADMIN_TOKEN_HEADER` é o nome do header).
- SQL concatenado: nenhum; todas as queries usam placeholders.
- `console.log`, `sqlite3`, `globalCache`, `badCrypto`, `pk_live`: nenhuma ocorrência em `src/`.
- Dados sensíveis em log/resposta: cartão mascarado; senha nunca é devolvida.

## Não resolvido

- `DELETE /api/users/:id` continua deixando matrículas e pagamentos órfãos e respondendo 200 para id inexistente: mudar isso alteraria o contrato (a mensagem e o relatório com `"Unknown"`). Fica como pendência de produto.
