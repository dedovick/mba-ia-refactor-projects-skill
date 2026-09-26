# Validation Results — code-smells-project (2026-09-26)

Run command: `python -W default app.py` (mesmo `python app.py` de antes) com `PORT=65229 ADMIN_TOKEN=<aleatório> ADMIN_INITIAL_PASSWORD=<teste>`, numa cópia temporária com venv novo (`pip install -r requirements.txt`: flask 3.1.1, flask-cors 5.0.1, python-dotenv 1.2.3).

## Boot log

```
INFO src.database.seed: Seed aplicado: 10 produtos, 3 usuários
INFO __main__: Servidor iniciado em http://127.0.0.1:65229
 * Serving Flask app 'src.app'
 * Debug mode: off
INFO werkzeug: WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:65229
```

Nenhum erro e nenhum `DeprecationWarning`. O aviso de "development server" do Werkzeug já existia na linha de base. `Debugger is active!` e o bind em `0.0.0.0` sumiram. O único `WARNING` da aplicação durante a sequência é o log intencional do `/admin/reset-db`.

## Antes × depois (mesma sequência da linha de base, banco novo)

As requisições `/admin/*` (35-37) foram enviadas com `Authorization: Bearer <ADMIN_TOKEN>`.

| # | Request | Antes | Depois | Veredito |
|---|---|---|---|---|
| 1 | `GET /` | 200 | 200 (mesmo formato) | ✓ Igual |
| 2 | `GET /health` | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, db_path, debug, secret_key, status, versao} | 200 {ambiente, counts: {pedidos, produtos, usuarios}, database, status, versao} | ✓ Mudança esperada (C-02: sem `secret_key`, `debug`, `db_path`) |
| 3 | `GET /produtos` | 200 | 200 (mesmo formato) | ✓ Igual |
| 4 | `GET /produtos/busca?q=gamer&categoria=informatica&preco_min=100&preco_max=3000` | 200 | 200 (mesmo formato) | ✓ Igual |
| 5 | `GET /produtos/1` | 200 | 200 (mesmo formato) | ✓ Igual |
| 6 | `GET /produtos/999` | 404 | 404 (mesmo formato) | ✓ Igual |
| 7 | `GET /usuarios` | 200 {dados: [{criado_em, email, id, nome, senha, tipo}], sucesso} | 200 {dados: [{criado_em, email, id, nome, tipo}], sucesso} | ✓ Mudança esperada (C-01: sem `senha`) |
| 8 | `GET /usuarios/1` | 200 {dados: {criado_em, email, id, nome, senha, tipo}, sucesso} | 200 {dados: {criado_em, email, id, nome, tipo}, sucesso} | ✓ Mudança esperada (C-01: sem `senha`) |
| 9 | `GET /usuarios/999` | 404 | 404 (mesmo formato) | ✓ Igual |
| 10 | `GET /pedidos` | 200 | 200 (mesmo formato) | ✓ Igual |
| 11 | `GET /pedidos/usuario/2` | 200 | 200 (mesmo formato) | ✓ Igual |
| 12 | `GET /relatorios/vendas` | 200 | 200 (mesmo formato) | ✓ Igual |
| 13 | `POST /produtos {"nome": "Produto Teste", "descricao": "desc", "preco": 10.5, "estoque": 5, "categoria": "geral"}` | 201 | 201 (mesmo formato) | ✓ Igual |
| 14 | `POST /produtos {"nome": "X"}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 15 | `POST /produtos {"nome": "Produto Y", "preco": 10, "estoque": 1, "categoria": "invalida"}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 16 | `POST /usuarios {"nome": "Novo", "email": "novo@email.com", "senha": "abc123"}` | 201 | 201 (mesmo formato) | ✓ Igual |
| 17 | `POST /usuarios {"nome": "Novo"}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 18 | `POST /login {"email": "joao@email.com", "senha": "123456"}` | 200 | 200 (mesmo formato) | ✓ Igual |
| 19 | `POST /login {"email": "joao@email.com", "senha": "errada"}` | 401 | 401 (mesmo formato) | ✓ Igual |
| 20 | `POST /login {"email": ""}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 21 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 2, "quantidade": 2}]}` | 201 | 201 (mesmo formato) | ✓ Igual |
| 22 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 999, "quantidade": 1}]}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 23 | `POST /pedidos {"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 9999}]}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 24 | `POST /pedidos {"usuario_id": 2}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 25 | `GET /pedidos` | 200 | 200 (mesmo formato) | ✓ Igual |
| 26 | `GET /pedidos/usuario/2` | 200 | 200 (mesmo formato) | ✓ Igual |
| 27 | `GET /relatorios/vendas` | 200 | 200 (mesmo formato) | ✓ Igual |
| 28 | `PUT /produtos/11 {"nome": "Produto Teste 2", "preco": 12, "estoque": 3, "categoria": "geral"}` | 200 | 200 (mesmo formato) | ✓ Igual |
| 29 | `PUT /produtos/999 {"nome": "x", "preco": 1, "estoque": 1}` | 404 | 404 (mesmo formato) | ✓ Igual |
| 30 | `PUT /produtos/11 {"nome": "Sem preco"}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 31 | `PUT /pedidos/1/status {"status": "aprovado"}` | 200 | 200 (mesmo formato) | ✓ Igual |
| 32 | `PUT /pedidos/1/status {"status": "invalido"}` | 400 | 400 (mesmo formato) | ✓ Igual |
| 33 | `DELETE /produtos/11` | 200 | 200 (mesmo formato) | ✓ Igual |
| 34 | `DELETE /produtos/999` | 404 | 404 (mesmo formato) | ✓ Igual |
| 35 | `POST /admin/query {"sql": "SELECT COUNT(*) AS n FROM produtos"}` | 200 | 200 (mesmo formato) | ✓ Igual (com token admin, C-03) |
| 36 | `POST /admin/query {}` | 400 | 400 (mesmo formato) | ✓ Igual (com token admin, C-03) |
| 37 | `POST /admin/reset-db` | 200 | 200 (mesmo formato) | ✓ Igual (com token admin, C-03) |

Resultado: 37/37 corretas, sendo 31 iguais, 3 mudanças esperadas de segurança e 3 rotas admin iguais com token. Nenhuma regressão.

## Verificações de segurança e correções de bug

    Verificação                                                 Resposta [status]
    admin/query sem token                                     : {"erro":"N\u00e3o autorizado"}
     [401]
    admin/reset-db token errado                               : {"erro":"N\u00e3o autorizado"}
     [401]
    admin/query DELETE (com token)                            : {"erro":"Apenas consultas SELECT s\u00e3o permitidas"}
     [400]
    admin/query SELECT com função de escrita? (pragma)        : {"erro":"Query inv\u00e1lida ou n\u00e3o permitida"}
     [400]
    admin/query SELECT; DROP (multi-statement)                : {"erro":"Query inv\u00e1lida ou n\u00e3o permitida"}
     [400]
    admin/query SELECT válido                                 : {"dados":[{"n":10}],"sucesso":true}
     [200]
    login SQLi admin@loja.com' --                             : {"erro":"Email ou senha inv\u00e1lidos","sucesso":false}
     [401]
    login admin (senha do env)                                : {"dados":{"email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},"mensagem":"Login OK","sucesso":true}
     [200]
    login admin123 (senha antiga hardcoded)                   : {"erro":"Email ou senha inv\u00e1lidos","sucesso":false}
     [401]
    login sem body                                            : {"erro":"Email e senha s\u00e3o obrigat\u00f3rios"}
     [400]
    busca SQLi q=' UNION SELECT 1--                           : {"dados":[],"sucesso":true,"total":0}
     [200]
    busca preco_min=abc                                       : {"erro":"preco_min deve ser num\u00e9rico"}
     [400]
    POST produto nome com apostrofo                           : {"dados":{"id":11},"mensagem":"Produto criado","sucesso":true}
     [201]
    POST produto preco string                                 : {"erro":"Pre\u00e7o deve ser num\u00e9rico"}
     [400]
    PUT produto categoria invalida                            : {"erro":"Categoria inv\u00e1lida. V\u00e1lidas: ['informatica', 'moveis', 'vestuario', 'geral', 'eletronicos', 'livros']"}
     [400]
    pedido quantidade negativa                                : {"erro":"Cada item precisa de produto_id e quantidade inteira maior que zero"}
     [400]
    pedido item sem produto_id                                : {"erro":"Cada item precisa de produto_id e quantidade inteira maior que zero"}
     [400]
    pedido itens repetidos 5+5 (produto 6 tem 8)              : {"erro":"Estoque insuficiente para Cadeira Gamer","sucesso":false}
     [400]
    estoque produto 6 inalterado                              : {"dados":{"ativo":1,"categoria":"moveis","criado_em":"2026-09-26 18:39:21","descricao":"Cadeira ergon\u00f4mica","estoque":8,"id":6,"nome":"Cadeira Gamer","preco":1299.9},"sucesso":true}
     [200]
    status pedido inexistente                                 : {"erro":"Pedido n\u00e3o encontrado"}
     [404]
    status sem body                                           : {"erro":"Status inv\u00e1lido"}
     [400]
    POST produtos text/plain                                  : {"erro":"Dados inv\u00e1lidos"}
     [400]
    rota inexistente                                          : {"erro":"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}
     [404]
    método não permitido (PATCH /produtos)                    : {"erro":"The method is not allowed for the requested URL."}
     [405]
    GET /usuarios/1 (sem senha)                               : {"dados":{"criado_em":"2026-09-26 18:39:21","email":"admin@loja.com","id":1,"nome":"Admin","tipo":"admin"},"sucesso":true}
     [200]
    CORS origem arbitrária                                    : HTTP/1.1 200 OK
    Content-Type: application/json
    
     [200]

Outras verificações:
- Senhas no banco após o seed: `scrypt:32768:8...` para os 3 usuários.
- Banco legado com senha em texto puro: migrado no boot (`Senhas em texto puro migradas para hash: 1`) e o login com a senha antiga continua funcionando (200).
- CORS: `Origin: http://evil.example` não recebe `Access-Control-Allow-Origin`.

## Varredura do catálogo nos arquivos novos

| Verificação | Resultado |
|---|---|
| AP-01 segredos literais | nenhum |
| AP-02 SQL concatenado | só `src/models/produto_model.py:27`, que junta cláusulas fixas; os valores seguem por parâmetros (padrão T-02) |
| `except:` vazio / `str(e)` devolvido ao cliente | nenhum |
| `senha` em views/presenters | nenhum |
| `print`, `debug=True`, `0.0.0.0`, `global`, `check_same_thread` | nenhum (os matches de `print(` eram `blueprint(`) |
| `flask` importado em models/services/controllers | nenhum |
| SQL fora de `models/` e `database/` | nenhum |
| pyflakes (imports e variáveis sem uso) | sem apontamentos |

## Pendências

- Concorrência real (dois pedidos simultâneos disputando o mesmo estoque) não foi testada sob carga. A proteção é o `UPDATE ... WHERE estoque >= ?` dentro da transação, verificado só por leitura de código.
- O cancelamento de pedido continua sem devolver estoque, como no original (o log antigo prometia a devolução, mas nenhum código a fazia). A mensagem enganosa saiu; a regra não foi implementada para não mudar comportamento sem decisão de negócio.
- `/login` continua sem emitir token de sessão, como no original. As rotas admin usam um token de serviço (`ADMIN_TOKEN`).
