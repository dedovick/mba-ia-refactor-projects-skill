# Validation Results — code-smells-project (2026-09-26)

Run command: `PORT=50780 ADMIN_TOKEN=<token> SEED_ADMIN_PASSWORD=<senha> python -W default app.py` (cópia limpa em diretório temporário, dependências reinstaladas de `requirements.txt`, banco novo)

## Log de boot

```
2026-09-26 15:58:13,701 INFO src.database.seed: Seed aplicado: 10 produtos e 3 usuários
2026-09-26 15:58:13,701 INFO __main__: Servidor iniciando em http://127.0.0.1:50780
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:50780
```

Nenhum erro, traceback ou `DeprecationWarning` (boot com `-W default`). O debugger do Werkzeug não está mais ativo (`Debug mode: off`) e o bind passou a ser `127.0.0.1`. O único aviso é o padrão do Werkzeug ("development server"), que já existia na linha de base.

## Linha de base × depois (mesma sequência de 35 requisições)

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| 1 | GET / | 200 {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} | 200 {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} | ✓ Igual |
| 2 | GET /health | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, status, versao} | ✓ Mudança esperada (segurança: removidos secret_key, db_path, debug) |
| 3 | GET /produtos | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} | ✓ Igual |
| 4 | GET /produtos/busca?q=Mouse | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | ✓ Igual |
| 5 | GET /produtos/busca?categoria=informatica&preco_min=100&preco_max=500 | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | ✓ Igual |
| 6 | GET /produtos/1 | 200 {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} | 200 {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} | ✓ Igual |
| 7 | GET /produtos/999 | 404 {erro, sucesso} | 404 {erro, sucesso} | ✓ Igual |
| 8 | POST /produtos {"nome": "Livro Python", "descricao": "Livro", "preco": 99.9, "estoque": 5, "categoria": "livros"} | 201 {dados: {id}, mensagem, sucesso} | 201 {dados: {id}, mensagem, sucesso} | ✓ Igual |
| 9 | POST /produtos {} | 400 {erro} | 400 {erro} | ✓ Igual |
| 10 | POST /produtos {"nome": "Sem preco", "estoque": 1} | 400 {erro} | 400 {erro} | ✓ Igual |
| 11 | POST /produtos {"nome": "Cat", "preco": 1, "estoque": 1, "categoria": "xyz"} | 400 {erro} | 400 {erro} | ✓ Igual |
| 12 | PUT /produtos/11 {"nome": "Livro Python 2", "descricao": "Livro", "preco": 89.9, "estoque": 4, "categoria": "livros"} | 200 {mensagem, sucesso} | 200 {mensagem, sucesso} | ✓ Igual |
| 13 | PUT /produtos/999 {"nome": "x", "preco": 1, "estoque": 1} | 404 {erro} | 404 {erro} | ✓ Igual |
| 14 | GET /usuarios | 200 {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} | 200 {dados: [{criado_em, email, id, nome, tipo}], sucesso} | ✓ Mudança esperada (segurança: campo senha removido) |
| 15 | GET /usuarios/1 | 200 {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} | 200 {dados: {criado_em, email, id, nome, tipo}, sucesso} | ✓ Mudança esperada (segurança: campo senha removido) |
| 16 | GET /usuarios/999 | 404 {erro} | 404 {erro} | ✓ Igual |
| 17 | POST /usuarios {"nome": "Ana", "email": "ana@email.com", "senha": "abc123"} | 201 {dados: {id}, sucesso} | 201 {dados: {id}, sucesso} | ✓ Igual |
| 18 | POST /usuarios {"nome": "Ana"} | 400 {erro} | 400 {erro} | ✓ Igual |
| 19 | POST /login {"email": "joao@email.com", "senha": "123456"} | 200 {dados: {email, id, nome, tipo}, mensagem, sucesso} | 200 {dados: {email, id, nome, tipo}, mensagem, sucesso} | ✓ Igual |
| 20 | POST /login {"email": "joao@email.com", "senha": "errada"} | 401 {erro, sucesso} | 401 {erro, sucesso} | ✓ Igual |
| 21 | POST /login {"email": ""} | 400 {erro} | 400 {erro} | ✓ Igual |
| 22 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 2}]} | 201 {dados: {pedido_id, total}, mensagem, sucesso} | 201 {dados: {pedido_id, total}, mensagem, sucesso} | ✓ Igual |
| 23 | POST /pedidos {"usuario_id": 2, "itens": []} | 400 {erro} | 400 {erro} | ✓ Igual |
| 24 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]} | 400 {erro, sucesso} | 400 {erro, sucesso} | ✓ Igual |
| 25 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 6, "quantidade": 999}]} | 400 {erro, sucesso} | 400 {erro, sucesso} | ✓ Igual |
| 26 | GET /pedidos | 200 {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} | 200 {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} | ✓ Igual |
| 27 | GET /pedidos/usuario/2 | 200 {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} | 200 {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} | ✓ Igual |
| 28 | PUT /pedidos/1/status {"status": "aprovado"} | 200 {mensagem, sucesso} | 200 {mensagem, sucesso} | ✓ Igual |
| 29 | PUT /pedidos/1/status {"status": "invalido"} | 400 {erro} | 400 {erro} | ✓ Igual |
| 30 | GET /relatorios/vendas | 200 {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} | 200 {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} | ✓ Igual |
| 31 | DELETE /produtos/11 | 200 {mensagem, sucesso} | 200 {mensagem, sucesso} | ✓ Igual |
| 32 | DELETE /produtos/999 | 404 {erro} | 404 {erro} | ✓ Igual |
| 33 | POST /admin/query {"sql": "SELECT COUNT(*) AS n FROM produtos"} | 200 {dados: [{n}], sucesso} | 200 {dados: [{n}], sucesso} | ✓ Igual (enviado com X-Admin-Token; sem token → 401) |
| 34 | POST /admin/query {} | 400 {erro} | 400 {erro} | ✓ Igual (enviado com X-Admin-Token; sem token → 401) |
| 35 | POST /admin/reset-db | 200 {mensagem, sucesso} | 200 {mensagem, sucesso} | ✓ Igual (enviado com X-Admin-Token; sem token → 401) |

Idênticos: 32/35; mudanças esperadas: 3; regressões: 0

## Verificações adicionais (correções de segurança e bugs)

| Requisição | Antes (linha de base / código) | Depois |
|---|---|---|
| POST /admin/reset-db sem token | 200, banco apagado | 401 {erro} |
| POST /admin/query sem token / token errado | 200, SQL executado | 401 {erro} |
| POST /admin/query com token, `DELETE FROM produtos` | 200, executado | 400 {erro} "Apenas consultas SELECT são permitidas" |
| POST /admin/query com token, `SELECT 1; DELETE FROM produtos` | — | 400 {erro} (conexão somente leitura) |
| POST /login `{"email": "admin@loja.com' --", "senha": "x"}` | login como admin (SQL injection) | 401 {erro, sucesso} |
| POST /pedidos com `quantidade: -5` | 201, estoque aumentava | 400 {erro} |
| POST /produtos com `preco: "abc"` | 500 com mensagem interna | 400 {erro} |
| POST /login com corpo `null` | 500 (AttributeError) | 400 {erro} |
| PUT /pedidos/999/status | 200 (sucesso falso) | 404 {erro} |
| GET /produtos/busca?preco_min=abc | 500 com mensagem interna | 400 {erro} |
| GET /nao-existe / PATCH /produtos | 404 / 405 do Flask | 404 / 405 do Flask (inalterado) |
| CORS com `Origin: http://evil.example` | `Access-Control-Allow-Origin: *` | sem header CORS (origens vêm de `CORS_ORIGINS`) |
| Boot sobre banco legado com senha em texto puro | — | senha convertida para hash `scrypt:` e login continua 200 |

## Varredura do catálogo nos arquivos novos

- SQL concatenado: nenhum. As únicas f-strings SQL interpolam constantes de módulo (`COLUNAS`, `TABELAS_RESET`); os valores vão sempre por placeholder `?`.
- Segredos hardcoded / `debug=True` / `0.0.0.0`: nenhum.
- `print`: nenhum. `except` genérico: só o handler central em `src/middlewares/error_handler.py`.
- `senha` em presenters/respostas: nenhum.
- `global` / `check_same_thread`: nenhum.
- pyflakes em `src/` e `app.py`: sem avisos.

## Problemas não resolvidos

- `GET /usuarios` e `GET /usuarios/<id>` continuam públicos e devolvem nome/e-mail (sem senha). Restringi-los mudaria o contrato além da correção de segurança pedida e exigiria um mecanismo de sessão que a API não tem.
- `POST /login` continua sem emitir token ou sessão (o contrato de resposta foi mantido).
- A notificação de cancelamento continua só registrando "devolver estoque" em log; o estoque não é devolvido automaticamente (comportamento original preservado).
- `POST /pedidos` não verifica se `usuario_id` existe (comportamento original preservado).
- O servidor continua sendo o de desenvolvimento do Werkzeug, porque o comando `python app.py` foi preservado.
