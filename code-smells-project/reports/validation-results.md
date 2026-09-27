# Validation Results — code-smells-project (2026-09-27)

Run command: `PORT=61885 ADMIN_TOKEN=<token de teste> python -W default app.py` (mesmo `python app.py` de antes; porta via ambiente) | Boot: OK

Boot log:
```
 * Serving Flask app 'src.app'
 * Debug mode: off
INFO werkzeug: WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:61885
```
Sem erros, tracebacks ou DeprecationWarning. Antes: `Debug mode: on`, `Debugger is active!`, bind em 0.0.0.0; agora debug desligado e bind local por padrão.

Dependências reinstaladas numa cópia limpa (`pip install -r requirements.txt`: flask 3.1.1, flask-cors 5.0.1 — manifesto inalterado).

## Baseline × depois

Além de status e formato, os **valores** das 32 respostas foram comparados subindo o código original (`git HEAD`) e o novo lado a lado com bancos limpos: idênticos em todas, ignorando `criado_em` e os campos sensíveis removidos.

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| 1 | `GET /` | 200 {endpoints: {health, login, pedidos, produtos, relatorios, usuarios}, mensagem, versao} | 200 (igual) | ✓ Igual |
| 2 | `GET /health` | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, status, versao} | ✓ Mudança esperada (secret_key, db_path, debug removidos — Contract changes) |
| 3 | `GET /produtos` | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso} | 200 (igual) | ✓ Igual |
| 4 | `GET /produtos/1` | 200 {dados: {ativo, categoria, criado_em, descricao, estoque, id, nome, preco}, sucesso} | 200 (igual) | ✓ Igual |
| 5 | `GET /produtos/999` | 404 {erro, sucesso} | 404 (igual) | ✓ Igual |
| 6 | `GET /produtos/busca?q=Mouse` | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | 200 (igual) | ✓ Igual |
| 7 | `GET /produtos/busca?categoria=informatica&preco_min=100&preco_max=500` | 200 {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, total} | 200 (igual) | ✓ Igual |
| 8 | `GET /usuarios` | 200 {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} | 200 {dados: [{criado_em, email, id, nome, tipo}], sucesso} | ✓ Mudança esperada (campo senha removido — Contract changes) |
| 9 | `GET /usuarios/1` | 200 {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} | 200 {dados: {criado_em, email, id, nome, tipo}, sucesso} | ✓ Mudança esperada (campo senha removido — Contract changes) |
| 10 | `GET /usuarios/999` | 404 {erro} | 404 (igual) | ✓ Igual |
| 11 | `POST /produtos {"nome": "Produto Teste", "descricao": "desc", "preco": 10.5, "estoque": 5, "categoria": "geral"}` | 201 {dados: {id}, mensagem, sucesso} | 201 (igual) | ✓ Igual |
| 12 | `POST /produtos {}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 13 | `POST /produtos {"nome": "X Produto"}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 14 | `POST /produtos {"nome": "Produto", "preco": 1, "estoque": 1, "categoria": "invalida"}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 15 | `PUT /produtos/11 {"nome": "Produto Teste 2", "descricao": "d2", "preco": 12, "estoque": 6, "categoria": "geral"}` | 200 {mensagem, sucesso} | 200 (igual) | ✓ Igual |
| 16 | `PUT /produtos/999 {"nome": "Nada", "preco": 1, "estoque": 1}` | 404 {erro} | 404 (igual) | ✓ Igual |
| 17 | `POST /usuarios {"nome": "Teste", "email": "teste@x.com", "senha": "abc123"}` | 201 {dados: {id}, sucesso} | 201 (igual) | ✓ Igual |
| 18 | `POST /usuarios {"nome": "Sem email"}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 19 | `POST /login {"email": "joao@email.com", "senha": "123456"}` | 200 {dados: {email, id, nome, tipo}, mensagem, sucesso} | 200 (igual) | ✓ Igual |
| 20 | `POST /login {"email": "joao@email.com", "senha": "errada"}` | 401 {erro, sucesso} | 401 (igual) | ✓ Igual |
| 21 | `POST /login {"email": "joao@email.com"}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 22 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 1}]}` | 201 {dados: {pedido_id, total}, mensagem, sucesso} | 201 (igual) | ✓ Igual |
| 23 | `POST /pedidos {"usuario_id": 2, "itens": []}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 24 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]}` | 400 {erro, sucesso} | 400 (igual) | ✓ Igual |
| 25 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 6, "quantidade": 1000}]}` | 400 {erro, sucesso} | 400 (igual) | ✓ Igual |
| 26 | `GET /pedidos` | 200 {dados: [{criado_em, id, itens: [{preco_unitario, produto_id, produto_nome, quantidade}], status, total, usuario_id}], sucesso} | 200 (igual) | ✓ Igual |
| 27 | `GET /pedidos/usuario/2` | 200 {dados: [{criado_em, id, itens: [{preco_unitario, produto_id, produto_nome, quantidade}], status, total, usuario_id}], sucesso} | 200 (igual) | ✓ Igual |
| 28 | `PUT /pedidos/1/status {"status": "aprovado"}` | 200 {mensagem, sucesso} | 200 (igual) | ✓ Igual |
| 29 | `PUT /pedidos/1/status {"status": "xyz"}` | 400 {erro} | 400 (igual) | ✓ Igual |
| 30 | `GET /relatorios/vendas` | 200 {dados: {desconto_aplicavel, faturamento_bruto, faturamento_liquido, pedidos_aprovados, pedidos_cancelados, pedidos_pendentes, ticket_medio, total_pedidos}, sucesso} | 200 (igual) | ✓ Igual |
| 31 | `DELETE /produtos/11` | 200 {mensagem, sucesso} | 200 (igual) | ✓ Igual |
| 32 | `DELETE /produtos/999` | 404 {erro} | 404 (igual) | ✓ Igual |

**Resultado:** 29/32 iguais, 3 mudanças esperadas (segurança), 0 regressões.

## Sondas antes → depois

| # | Categoria | Request | Antes | Depois | Veredito |
|---|---|---|---|---|---|
| P1 | Autenticação | `POST /login {"email": "admin@loja.com' --", "senha": "qualquer"}` | VULNERÁVEL: 200, autenticou como admin@loja.com | 401, {erro, sucesso} | OK |
| P2 | Autenticação | `POST /login {"email": "x' OR '1'='1", "senha": "x' OR '1'='1"}` | VULNERÁVEL: 200, autenticou como admin@loja.com | 401, {erro, sucesso} | OK |
| P3 | Exposição | `GET /usuarios` | VULNERÁVEL: 200, campo senha presente | 200, sem senha | OK |
| P4 | Exposição | `GET /usuarios/1` | VULNERÁVEL: 200, campo senha presente | 200, sem senha | OK |
| P5 | Exposição | `GET /health` | VULNERÁVEL: 200, secret_key/db_path expostos | 200, sem segredos | OK |
| P6 | Autorização | `POST /admin/query {"sql": "SELECT email, senha FROM usuarios"}` | VULNERÁVEL: 200, SQL arbitrário executado, senhas devolvidas | 401, {erro} | OK |
| P7 | Injeção | `GET /produtos/busca?q=%27` | OK: 200, {dados: [], sucesso, total} | 200, {dados: [{ativo, categoria, criado_em, descricao, estoque, id, nome, preco}], sucesso, tot | OK |
| P8 | Injeção | `GET /produtos/busca?q=zzz%27%20OR%20%271%27%3D%271` | OK: 200, total=0 | 200, total=0 | OK |
| P9 | Injeção | `POST /produtos {"nome": "Livro O'Reilly", "preco": 50, "estoque": 1, "categoria": "livros"}` | VULNERÁVEL: 500, {erro} | 201, {dados: {id}, mensagem, sucesso} | OK |
| P10 | Injeção | `POST /usuarios {"nome": "Ana D'Ávila", "email": "ana@x.com", "senha": "s3nha"}` | VULNERÁVEL: 500, {erro} | 201, {dados: {id}, sucesso} | OK |
| P11 | Injeção | `GET /produtos/busca?categoria=x%27%20OR%20%271%27%3D%271` | VULNERÁVEL: 200, total=10 | 200, total=0 | OK |
| P12 | Tipos | `POST /produtos {"nome": "Teste", "preco": "abc", "estoque": 1}` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P13 | Tipos | `PUT /produtos/1 {"nome": 123, "preco": 10, "estoque": 1}` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P14 | Tipos | `GET /produtos/busca?preco_min=abc` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P15 | Tipos | `POST /login (body raw: 'null')` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P16 | Tipos | `PUT /pedidos/1/status (body raw: 'null')` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P17 | Tipos | `POST /admin/query (body raw: 'null')` | VULNERÁVEL: 500, traceback exposto | 401, {erro} | OK |
| P18 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"quantidade": 1}]}` | VULNERÁVEL: 500, {erro} | 400, {erro} | OK |
| P19 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 3, "quantidade": -5}]}` | VULNERÁVEL: 201, total=-1499.5, estoque produto 3: 30→35 | 400, total=None, estoque produto 3: 30→30 | OK |
| P20 | Tipos | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 3, "quantidade": 0}]}` | VULNERÁVEL: 201, {dados: {pedido_id, total}, mensagem, sucesso} | 400, {erro} | OK |
| P21 | Inexistentes | `PUT /pedidos/999/status {"status": "aprovado"}` | VULNERÁVEL: 200, {mensagem, sucesso} | 404, {erro} | OK |
| P22 | Identidade | `POST /pedidos {"usuario_id": 999, "itens": [{"produto_id": 2, "quantidade": 1}]}` | VULNERÁVEL: 201, {dados: {pedido_id, total}, mensagem, sucesso} | 400, {erro, sucesso} | OK |
| P23 | Identidade | `POST /usuarios {"nome": "Clone", "email": "joao@email.com", "senha": "outra"}` | VULNERÁVEL: 201, {dados: {id}, sucesso} | 409, {erro} | OK |
| P24 | Consistência | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 4, "quantidade": 1}, {"produto_id": 999, "quantidade": 1}]}` | OK: 400, {erro, sucesso}, estoque produto 4: 15→15 | 400, {erro, sucesso}, estoque produto 4: 15→15 | OK |
| P25 | Autorização | `POST /admin/reset-db` | VULNERÁVEL: 200, banco apagado sem credencial; GET /produtos depois: 0 itens | 401, {erro}; GET /produtos depois: 11 itens | OK |
| P26 | Exposição | grep no `server.log` por senhas, token admin e e-mails | OK: sem senhas; e-mails e payloads impressos | 0 ocorrências de senhas, token ou e-mails; logs com `logging`, nível e ids | OK |
| P27 | Exposição | `POST /admin/query` body `null` | VULNERÁVEL: traceback + debugger | sem token: 401; com token: 400 `{erro: "Query não informada"}`; debug off | OK |

**Resultado:** 23/23 sondas que eram VULNERÁVEIS agora estão OK; as 4 que já eram OK continuam OK.

## Verificações adicionais

| Verificação | Resultado |
|---|---|
| `POST /admin/query {"sql": "SELECT COUNT(*) AS n FROM produtos"} [X-Admin-Token válido]` | 200 {dados: [{n}], sucesso} |
| `POST /admin/query {"sql": "DELETE FROM produtos"} [X-Admin-Token válido]` | 400 {erro} |
| `POST /admin/query {"sql": "SELECT * FROM tabela_inexistente"} [X-Admin-Token válido]` | 400 {erro} |
| `POST /admin/query {"sql": "SELECT 1"} [X-Admin-Token errado]` | 401 {erro} |
| `POST /admin/reset-db [X-Admin-Token válido]` | 200 {mensagem, sucesso}; GET /produtos depois: 0 itens |
| `POST /produtos` com `Content-Type: text/plain` | 400 `{erro: "Dados inválidos"}` (antes: 415) |
| `PATCH /produtos/1` / rota inexistente | 405 / 404 em JSON `{erro}` pelo handler central |
| Banco `loja.db` legado (senhas em texto puro, criado pelo código original) | No boot, as 3 senhas foram convertidas para `scrypt:`; login com as senhas originais → 200; senha errada → 401 |

## Varredura estática (catálogo) nos arquivos novos

| Anti-pattern | Resultado |
|---|---|
| AP-01 segredos | nenhum literal; único hit é o nome do header `X-Admin-Token` (não é segredo) |
| AP-02 SQL concatenado | nenhum valor concatenado; os f-strings/joins restantes montam só estrutura fixa (`?` placeholders, nome de tabela de tupla constante) — falso positivo pelo catálogo |
| AP-03 senha em resposta | presenters sem `senha`; `/health` sem segredos |
| AP-07 debug | nenhum `debug=True`/`0.0.0.0` |
| AP-10 estado global | sem `global` nem `check_same_thread`; conexão por requisição em `g` |
| AP-16 except genérico | nenhum `except Exception`/`str(e)` nos handlers; só `sqlite3.Error` específico no health e no admin/query |
| AP-20 print | nenhum `print` |
| Camadas | nenhum import de `request`/`jsonify` em controllers, models, services ou database |
| AP-15 N+1 | nenhuma query dentro de laço sobre resultado de outra query |

## Não resolvido

- F-04 (parcial): `POST /pedidos` agora recusa `usuario_id` inexistente (P22 OK), mas continua sem autenticação por pedido; qualquer cliente pode pedir em nome de um usuário **existente**. Exige token/sessão emitido no login e mudança de contrato para todos os clientes — decisão de produto.
- Porta padrão 5000 não testada nesta máquina (ocupada pelo AirPlay/ControlCenter); a validação usou `PORT` do ambiente, que é o caminho documentado.
