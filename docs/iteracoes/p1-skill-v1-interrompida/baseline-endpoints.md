# Baseline — code-smells-project (2026-09-26)
Run command: `python app.py` | Port used: 64669 (literal 5000 alterado só na cópia temporária) | Boot: OK | Python 3.12.0, Flask 3.1.1, Werkzeug 3.1.8, flask-cors 5.0.1
Warnings: nenhum `DeprecationWarning` com `-W default`. Avisos do Werkzeug: "This is a development server", "Debug mode: on", "Debugger is active!" e bind em `0.0.0.0`.

Banco: `loja.db` novo (seed automático no boot: 10 produtos, 3 usuários). As requisições rodam na ordem abaixo; o reset destrutivo fica por último.

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | `GET /` | 200 | {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} |
| 2 | `GET /health` | 200 | {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} |
| 3 | `GET /produtos` | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} |
| 4 | `GET /produtos/busca?q=gamer&categoria=informatica&preco_min=100&preco_max=3000` | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} |
| 5 | `GET /produtos/1` | 200 | {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} |
| 6 | `GET /produtos/999` | 404 | {erro, sucesso} |
| 7 | `GET /usuarios` | 200 | {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} |
| 8 | `GET /usuarios/1` | 200 | {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} |
| 9 | `GET /usuarios/999` | 404 | {erro} |
| 10 | `GET /pedidos` | 200 | {dados: [], sucesso} |
| 11 | `GET /pedidos/usuario/2` | 200 | {dados: [], sucesso} |
| 12 | `GET /relatorios/vendas` | 200 | {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} |
| 13 | `POST /produtos {"nome": "Produto Teste", "descricao": "desc", "preco": 10.5, "estoque": 5, "categoria": "geral"}` | 201 | {dados: {id}, mensagem, sucesso} |
| 14 | `POST /produtos {"nome": "X"}` | 400 | {erro} |
| 15 | `POST /produtos {"nome": "Produto Y", "preco": 10, "estoque": 1, "categoria": "invalida"}` | 400 | {erro} |
| 16 | `POST /usuarios {"nome": "Novo", "email": "novo@email.com", "senha": "abc123"}` | 201 | {dados: {id}, sucesso} |
| 17 | `POST /usuarios {"nome": "Novo"}` | 400 | {erro} |
| 18 | `POST /login {"email": "joao@email.com", "senha": "123456"}` | 200 | {dados: {email, id, nome, tipo}, mensagem, sucesso} |
| 19 | `POST /login {"email": "joao@email.com", "senha": "errada"}` | 401 | {erro, sucesso} |
| 20 | `POST /login {"email": ""}` | 400 | {erro} |
| 21 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 2}]}` | 201 | {dados: {pedido_id, total}, mensagem, sucesso} |
| 22 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]}` | 400 | {erro, sucesso} |
| 23 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 9999}]}` | 400 | {erro, sucesso} |
| 24 | `POST /pedidos {"usuario_id": 2}` | 400 | {erro} |
| 25 | `GET /pedidos` | 200 | {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} |
| 26 | `GET /pedidos/usuario/2` | 200 | {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} |
| 27 | `GET /relatorios/vendas` | 200 | {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} |
| 28 | `PUT /produtos/11 {"nome": "Produto Teste 2", "preco": 12, "estoque": 3, "categoria": "geral"}` | 200 | {mensagem, sucesso} |
| 29 | `PUT /produtos/999 {"nome": "x", "preco": 1, "estoque": 1}` | 404 | {erro} |
| 30 | `PUT /produtos/11 {"nome": "Sem preco"}` | 400 | {erro} |
| 31 | `PUT /pedidos/1/status {"status": "aprovado"}` | 200 | {mensagem, sucesso} |
| 32 | `PUT /pedidos/1/status {"status": "invalido"}` | 400 | {erro} |
| 33 | `DELETE /produtos/11` | 200 | {mensagem, sucesso} |
| 34 | `DELETE /produtos/999` | 404 | {erro} |
| 35 | `POST /admin/query {"sql": "SELECT COUNT(*) AS n FROM produtos"}` | 200 | {dados: [{n}], sucesso} |
| 36 | `POST /admin/query {}` | 400 | {erro} |
| 37 | `POST /admin/reset-db` | 200 | {mensagem, sucesso} |
