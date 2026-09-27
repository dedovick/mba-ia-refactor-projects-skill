# Baseline — ecommerce-api-legacy (2026-09-26)
Run command: `npm start` (`node src/app.js`) | Port used: 53902 (porta 3000 fixa em `src/utils.js:6`, trocada só na cópia temporária) | Boot: OK | Warnings: nenhum (`node --trace-deprecation`, Node v25.8.2)

Banco SQLite em memória, recriado e semeado a cada boot (1 usuário, 2 cursos, 1 matrícula, 1 pagamento).

| # | Request | Status | Content-Type | Response shape |
|---|---|---|---|---|
| 1 | GET /api/admin/financial-report | 200 | application/json | `[{course, revenue, students: [{student, paid}]}]` (2 itens) |
| 2 | POST /api/checkout `{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}` | 200 | application/json | `{msg: "Sucesso", enrollment_id: 2}` |
| 3 | POST /api/checkout `{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}` | 400 | text/html | `Pagamento recusado` |
| 4 | POST /api/checkout `{"usr":"X","eml":"x@x.com"}` | 400 | text/html | `Bad Request` |
| 5 | POST /api/checkout `{..., "c_id":999, "card":"4111"}` | 404 | text/html | `Curso não encontrado` |
| 6 | POST /api/checkout `{"usr":"Leonan","eml":"leonan@fullcycle.com.br","c_id":2,"card":"4000"}` (usuário existente) | 200 | application/json | `{msg: "Sucesso", enrollment_id: 3}` |
| 7 | GET /api/admin/financial-report | 200 | application/json | `[{course, revenue, students: [{student, paid}]}]` — Clean Architecture 997 (Leonan), Docker 994 (Guilherme 497, Leonan 497) |
| 8 | DELETE /api/users/1 | 200 | text/html | `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.` |
| 9 | DELETE /api/users/999 (inexistente) | 200 | text/html | mesma mensagem do #8 |
| 10 | GET /api/admin/financial-report | 200 | application/json | mesmo formato; alunos do usuário 1 aparecem como `"Unknown"` (matrículas órfãs) |
| 11 | GET /api/nao-existe | 404 | text/html | página padrão do Express `Cannot GET /api/nao-existe` |

Observações:
- A ordem dos cursos no relatório **não é determinística** (#1 veio Docker primeiro, #7 Clean Architecture primeiro): o array é montado na ordem em que os callbacks terminam.
- O log do servidor imprime o número completo do cartão e a chave do gateway de pagamento a cada checkout.
