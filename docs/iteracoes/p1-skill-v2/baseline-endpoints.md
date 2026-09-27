# Baseline — code-smells-project (2026-09-26)
Run command: `python app.py` | Port used: 50583 (literal `port=5000` trocado só na cópia temporária) | Boot: OK | Warnings: nenhum warning Python; apenas o aviso padrão do Werkzeug "This is a development server" e "Debug mode: on" / "Debugger is active!"

Sequência executada a partir de banco novo (seed automático de 10 produtos e 3 usuários no primeiro `get_db()`).

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | GET / | 200 | {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} |
| 2 | GET /health | 200 | {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} |
| 3 | GET /produtos | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} |
| 4 | GET /produtos/busca?q=Mouse | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} |
| 5 | GET /produtos/busca?categoria=informatica&preco_min=100&preco_max=500 | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} |
| 6 | GET /produtos/1 | 200 | {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} |
| 7 | GET /produtos/999 | 404 | {erro, sucesso} |
| 8 | POST /produtos {"nome": "Livro Python", "descricao": "Livro", "preco": 99.9, "estoque": 5, "categoria": "livros"} | 201 | {dados: {id}, mensagem, sucesso} |
| 9 | POST /produtos {} | 400 | {erro} |
| 10 | POST /produtos {"nome": "Sem preco", "estoque": 1} | 400 | {erro} |
| 11 | POST /produtos {"nome": "Cat", "preco": 1, "estoque": 1, "categoria": "xyz"} | 400 | {erro} |
| 12 | PUT /produtos/11 {"nome": "Livro Python 2", "descricao": "Livro", "preco": 89.9, "estoque": 4, "categoria": "livros"} | 200 | {mensagem, sucesso} |
| 13 | PUT /produtos/999 {"nome": "x", "preco": 1, "estoque": 1} | 404 | {erro} |
| 14 | GET /usuarios | 200 | {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} |
| 15 | GET /usuarios/1 | 200 | {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} |
| 16 | GET /usuarios/999 | 404 | {erro} |
| 17 | POST /usuarios {"nome": "Ana", "email": "ana@email.com", "senha": "abc123"} | 201 | {dados: {id}, sucesso} |
| 18 | POST /usuarios {"nome": "Ana"} | 400 | {erro} |
| 19 | POST /login {"email": "joao@email.com", "senha": "123456"} | 200 | {dados: {email, id, nome, tipo}, mensagem, sucesso} |
| 20 | POST /login {"email": "joao@email.com", "senha": "errada"} | 401 | {erro, sucesso} |
| 21 | POST /login {"email": ""} | 400 | {erro} |
| 22 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 2}]} | 201 | {dados: {pedido_id, total}, mensagem, sucesso} |
| 23 | POST /pedidos {"usuario_id": 2, "itens": []} | 400 | {erro} |
| 24 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]} | 400 | {erro, sucesso} |
| 25 | POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 6, "quantidade": 999}]} | 400 | {erro, sucesso} |
| 26 | GET /pedidos | 200 | {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} |
| 27 | GET /pedidos/usuario/2 | 200 | {dados: [{criado_em, id, itens, status, total, usuario_id}], sucesso} |
| 28 | PUT /pedidos/1/status {"status": "aprovado"} | 200 | {mensagem, sucesso} |
| 29 | PUT /pedidos/1/status {"status": "invalido"} | 400 | {erro} |
| 30 | GET /relatorios/vendas | 200 | {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} |
| 31 | DELETE /produtos/11 | 200 | {mensagem, sucesso} |
| 32 | DELETE /produtos/999 | 404 | {erro} |
| 33 | POST /admin/query {"sql": "SELECT COUNT(*) AS n FROM produtos"} | 200 | {dados: [{n}], sucesso} |
| 34 | POST /admin/query {} | 400 | {erro} |
| 35 | POST /admin/reset-db | 200 | {mensagem, sucesso} |

Observações:
- `GET /health` expõe `secret_key`, `db_path` e `debug`.
- `GET /usuarios` e `GET /usuarios/<id>` devolvem o campo `senha` em texto puro.
- `POST /admin/query` e `POST /admin/reset-db` respondem sem qualquer autenticação (#33 executou SQL arbitrário; #35 apagou todas as tabelas — por isso é a última requisição).
