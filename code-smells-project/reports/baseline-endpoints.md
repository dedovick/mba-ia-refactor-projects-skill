# Baseline — code-smells-project (2026-09-27)
Run command: `python app.py` | Port used: 61114 (literal `port=5000` trocado só na cópia temporária) | Boot: OK | Warnings: nenhum DeprecationWarning; Werkzeug avisa "development server" e o app sobe com `Debug mode: on` + "Debugger is active!"

Ambiente: Python 3.12.0, Flask 3.1.1, flask-cors 5.0.1, Werkzeug 3.1.8. Banco SQLite novo (`loja.db` criado e populado no boot). A sequência rodou duas vezes em bancos novos, com resultado idêntico.

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | `GET /` | 200 | {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} |
| 2 | `GET /health` | 200 | {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} |
| 3 | `GET /produtos` | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} |
| 4 | `GET /produtos/1` | 200 | {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} |
| 5 | `GET /produtos/999` | 404 | {erro, sucesso} |
| 6 | `GET /produtos/busca?q=Mouse` | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} |
| 7 | `GET /produtos/busca?categoria=informatica&preco_min=100&preco_max=500` | 200 | {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} |
| 8 | `GET /usuarios` | 200 | {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} |
| 9 | `GET /usuarios/1` | 200 | {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} |
| 10 | `GET /usuarios/999` | 404 | {erro} |
| 11 | `POST /produtos {"nome": "Produto Teste", "descricao": "desc", "preco": 10.5, "estoque": 5, "categoria": "geral"}` | 201 | {dados: {id}, mensagem, sucesso} |
| 12 | `POST /produtos {}` | 400 | {erro} |
| 13 | `POST /produtos {"nome": "X Produto"}` | 400 | {erro} |
| 14 | `POST /produtos {"nome": "Produto", "preco": 1, "estoque": 1, "categoria": "invalida"}` | 400 | {erro} |
| 15 | `PUT /produtos/11 {"nome": "Produto Teste 2", "descricao": "d2", "preco": 12, "estoque": 6, "categoria": "geral"}` | 200 | {mensagem, sucesso} |
| 16 | `PUT /produtos/999 {"nome": "Nada", "preco": 1, "estoque": 1}` | 404 | {erro} |
| 17 | `POST /usuarios {"nome": "Teste", "email": "teste@x.com", "senha": "abc123"}` | 201 | {dados: {id}, sucesso} |
| 18 | `POST /usuarios {"nome": "Sem email"}` | 400 | {erro} |
| 19 | `POST /login {"email": "joao@email.com", "senha": "123456"}` | 200 | {dados: {email, id, nome, tipo}, mensagem, sucesso} |
| 20 | `POST /login {"email": "joao@email.com", "senha": "errada"}` | 401 | {erro, sucesso} |
| 21 | `POST /login {"email": "joao@email.com"}` | 400 | {erro} |
| 22 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 1}]}` | 201 | {dados: {pedido_id, total}, mensagem, sucesso} |
| 23 | `POST /pedidos {"usuario_id": 2, "itens": []}` | 400 | {erro} |
| 24 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]}` | 400 | {erro, sucesso} |
| 25 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 6, "quantidade": 1000}]}` | 400 | {erro, sucesso} |
| 26 | `GET /pedidos` | 200 | {dados: [{criado_em, id, itens: [{preco_unitario, produto_id, produto_nome, quantidade}], status, total, usuario_id}], sucesso} |
| 27 | `GET /pedidos/usuario/2` | 200 | {dados: [{criado_em, id, itens: [{preco_unitario, produto_id, produto_nome, quantidade}], status, total, usuario_id}], sucesso} |
| 28 | `PUT /pedidos/1/status {"status": "aprovado"}` | 200 | {mensagem, sucesso} |
| 29 | `PUT /pedidos/1/status {"status": "xyz"}` | 400 | {erro} |
| 30 | `GET /relatorios/vendas` | 200 | {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} |
| 31 | `DELETE /produtos/11` | 200 | {mensagem, sucesso} |
| 32 | `DELETE /produtos/999` | 404 | {erro} |

## Probes

| # | Categoria | Request | Observado | Esperado | Veredito |
|---|---|---|---|---|---|
| P1 | Autenticação | `POST /login {"email": "admin@loja.com' --", "senha": "qualquer"}` | 200, autenticou como admin@loja.com | 401 | VULNERÁVEL |
| P2 | Autenticação | `POST /login {"email": "x' OR '1'='1", "senha": "x' OR '1'='1"}` | 200, autenticou como admin@loja.com | 401 | VULNERÁVEL |
| P3 | Exposição | `GET /usuarios` | 200, campo senha presente | sem campo senha | VULNERÁVEL |
| P4 | Exposição | `GET /usuarios/1` | 200, campo senha presente | sem campo senha | VULNERÁVEL |
| P5 | Exposição | `GET /health` | 200, secret_key/db_path expostos | sem secret_key/db_path/debug | VULNERÁVEL |
| P6 | Autorização | `POST /admin/query {"sql": "SELECT email, senha FROM usuarios"}` | 200, SQL arbitrário executado, senhas devolvidas | 401/403 sem credencial | VULNERÁVEL |
| P7 | Injeção | `GET /produtos/busca?q=%27` | 200, {dados: [], sucesso, total} | 200 lista vazia | OK |
| P8 | Injeção | `GET /produtos/busca?q=zzz%27%20OR%20%271%27%3D%271` | 200, total=0 | 200, total 0 | OK |
| P9 | Injeção | `POST /produtos {"nome": "Livro O'Reilly", "preco": 50, "estoque": 1, "categoria": "livros"}` | 500, {erro} | 201 (gravado literalmente) | VULNERÁVEL |
| P10 | Injeção | `POST /usuarios {"nome": "Ana D'Ávila", "email": "ana@x.com", "senha": "s3nha"}` | 500, {erro} | 201 (gravado literalmente) | VULNERÁVEL |
| P11 | Injeção | `GET /produtos/busca?categoria=x%27%20OR%20%271%27%3D%271` | 200, total=10 | 200, total 0 | VULNERÁVEL |
| P12 | Tipos | `POST /produtos {"nome": "Teste", "preco": "abc", "estoque": 1}` | 500, {erro} | 400 | VULNERÁVEL |
| P13 | Tipos | `PUT /produtos/1 {"nome": 123, "preco": 10, "estoque": 1}` | 500, {erro} | 400 | VULNERÁVEL |
| P14 | Tipos | `GET /produtos/busca?preco_min=abc` | 500, {erro} | 400 | VULNERÁVEL |
| P15 | Tipos | `POST /login (body raw: 'null')` | 500, {erro} | 400 | VULNERÁVEL |
| P16 | Tipos | `PUT /pedidos/1/status (body raw: 'null')` | 500, {erro} | 400 | VULNERÁVEL |
| P17 | Tipos | `POST /admin/query (body raw: 'null')` | 500, traceback exposto | 4xx, sem traceback | VULNERÁVEL |
| P18 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"quantidade": 1}]}` | 500, {erro} | 400 | VULNERÁVEL |
| P19 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 3, "quantidade": -5}]}` | 201, total=-1499.5, estoque produto 3: 30→35 | 400 | VULNERÁVEL |
| P20 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 3, "quantidade": 0}]}` | 201, {dados: {pedido_id, total}, mensagem, sucesso} | 400 | VULNERÁVEL |
| P21 | Inexistentes | `PUT /pedidos/999/status {"status": "aprovado"}` | 200, {mensagem, sucesso} | 404 | VULNERÁVEL |
| P22 | Identidade | `POST /pedidos {"usuario_id": 999, "itens": [{"produto_id": 2, "quantidade": 1}]}` | 201, {dados: {pedido_id, total}, mensagem, sucesso} | 400/404 (usuário inexistente) | VULNERÁVEL |
| P23 | Identidade | `POST /usuarios {"nome": "Clone", "email": "joao@email.com", "senha": "outra"}` | 201, {dados: {id}, sucesso} | 409/400 (e-mail já cadastrado) | VULNERÁVEL |
| P24 | Consistência | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 4, "quantidade": 1}, {"produto_id": 999, "quantidade": 1}]}` | 400, {erro, sucesso}, estoque produto 4: 15→15 | 400, nada gravado | OK |
| P25 | Autorização | `POST /admin/reset-db` | 200, banco apagado sem credencial; GET /produtos depois: 0 itens | 401/403 sem credencial | VULNERÁVEL |
| P26 | Exposição | `grep` no `server.log` por senhas e pela SECRET_KEY | nenhuma senha nem segredo no log; e-mails de usuários (PII) e payloads de injeção são impressos em texto puro (`Login bem-sucedido: admin@loja.com' --`) | sem segredos | OK |
| P27 | Exposição | `POST /admin/query` com body `null` (debug=True) | exceção sem tratamento: traceback completo no log e página do Werkzeug debugger (`Debugger is active!`) | 400 sem traceback | VULNERÁVEL |

**Resumo:** 32/32 requisições da linha de base responderam. 27 sondas executadas, 23 vulneráveis.

Notas:
- P7/P8 (`q=` com apóstrofo) deram 200 por coincidência sintática, mas a busca concatena SQL do mesmo jeito: a injeção pelo parâmetro `categoria` (P11) devolveu os 10 produtos.
- P21: o log registrou `NOTIFICAÇÃO: Pedido 999 foi aprovado!` para um pedido que não existe.
- P25 (destrutiva) rodou por último: apagou todas as tabelas sem credencial.
- P17 e P27 são a mesma requisição: P17 mede a resposta (500), P27 mede a exposição do traceback.
