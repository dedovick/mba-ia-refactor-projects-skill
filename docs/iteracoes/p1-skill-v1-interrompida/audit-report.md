# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.12 + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Date:    2026-09-26
================================
```

## Summary

CRITICAL: 6 | HIGH: 5 | MEDIUM: 6 | LOW: 3

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 6 | F-01, F-02, F-03, F-04, F-05, F-06 |
| HIGH | 5 | F-07, F-08, F-09, F-10, F-11 |
| MEDIUM | 6 | F-12, F-13, F-14, F-15, F-16, F-17 |
| LOW | 3 | F-18, F-19, F-20 |

## Findings

### F-01 [CRITICAL] Endpoints administrativos sem autenticação executam SQL arbitrário e apagam o banco
File: app.py:47-57, 59-78
Catalog: AP-06 (+ AP-02)
Description: `POST /admin/query` executa o SQL recebido no body, sem nenhuma verificação: `query = dados.get("sql", "")` … `cursor.execute(query)`. `POST /admin/reset-db` executa `DELETE FROM` nas quatro tabelas. Nenhuma das duas rotas verifica identidade ou papel, e `/login` não emite token nem sessão que alguma rota pudesse validar.
Impact: Qualquer cliente da rede lê a tabela `usuarios` com as senhas (`SELECT * FROM usuarios`), altera preços e status, executa `DROP TABLE` ou zera o banco com uma única requisição. Na linha de base, `POST /admin/query` com `SELECT` respondeu 200 com dados.
Recommendation: Exigir autorização administrativa (token lido de variável de ambiente, comparado com `hmac.compare_digest`) nas rotas `/admin/*`, que respondem 401/403 sem ele. Mover o reset para um model e restringir `/admin/query` a leitura (T-15, T-01).

### F-02 [CRITICAL] SQL Injection em praticamente todas as queries
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291, 293, 295, 297
Catalog: AP-02
Description: As queries são montadas por concatenação, incluindo a de login: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (models.py:110). A busca concatena o parâmetro de query string `q`: `" AND (nome LIKE '%" + termo + "%' ..."` (models.py:291).
Impact: Um e-mail `admin@loja.com' --` autentica como administrador sem senha. `GET /produtos/busca?q=' UNION SELECT ...` lê qualquer tabela. Um nome de produto com apóstrofo (`Monitor 27''`) quebra o INSERT com erro 500.
Recommendation: Usar queries parametrizadas com placeholders `?` em todos os repositórios (T-02).

### F-03 [CRITICAL] Senhas, segredo e detalhes internos expostos nas respostas
File: models.py:83, 99 | controllers.py:285-289, 12, 22, 62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292 | app.py:78
Catalog: AP-03
Description: `GET /usuarios` e `GET /usuarios/<id>` serializam `"senha": row["senha"]`. `GET /health` devolve `"secret_key": "minha-chave-super-secreta-123"`, `"debug": True` e `"db_path": "loja.db"`. Todos os handlers devolvem `{"erro": str(e)}` com a mensagem interna da exceção, que inclui fragmentos de SQL.
Impact: Qualquer pessoa obtém as senhas de todos os usuários (confirmado na linha de base: a chave `senha` aparece em `/usuarios`) e a `SECRET_KEY` usada para assinar sessões do Flask. Os erros revelam a estrutura do banco, o que facilita a exploração de F-02.
Recommendation: Serializar usuários sem `senha`, tirar a configuração do `/health` e devolver mensagens de erro genéricas, registrando o detalhe só no log (T-07, T-09).

### F-04 [CRITICAL] Senhas armazenadas e comparadas em texto puro
File: models.py:109-111, 126-129 | database.py:75-83
Catalog: AP-04
Description: `criar_usuario` grava a senha recebida como está (`"', '" + senha + "', '"`), o login compara `AND senha = '" + senha + "'` e o seed insere `("Admin", "admin@loja.com", "admin123", "admin")`.
Impact: Qualquer leitura do banco, seja pelo arquivo `loja.db`, por F-01, F-02 ou F-03, entrega todas as senhas utilizáveis, que costumam ser reaproveitadas em outros serviços.
Recommendation: Gravar hash com salt e custo (`werkzeug.security.generate_password_hash`, padrão scrypt/pbkdf2), verificar com `check_password_hash` e migrar o seed para gerar hashes (T-06).

### F-05 [CRITICAL] SECRET_KEY hardcoded e credenciais padrão no código
File: app.py:7 | controllers.py:289 | database.py:76
Catalog: AP-01
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está versionado e repetido literalmente no `/health`. O seed cria o administrador com a senha fixa `"admin123"`.
Impact: A chave vaza com o repositório e não pode ser trocada por ambiente. Com ela é possível forjar cookies de sessão assinados. A conta admin tem senha conhecida em toda instalação nova.
Recommendation: Criar um módulo de config que leia `SECRET_KEY`, `ADMIN_TOKEN` e os demais segredos do ambiente, publicar um `.env.example` sem valores reais e fazer o seed ler a senha inicial do admin do ambiente (T-01).

### F-06 [CRITICAL] Debug do Werkzeug ativo com bind público
File: app.py:8, 88 | controllers.py:286-288
Catalog: AP-07
Description: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` estão fixos no código. O log da linha de base mostra `Debugger is active!` e `Running on all addresses (0.0.0.0)`. O `/health` ainda afirma `"ambiente": "producao"`.
Impact: O debugger interativo do Werkzeug fica exposto a toda a rede e permite execução remota de código a partir de qualquer exceção não tratada. O reloader também duplica o processo.
Recommendation: Ler `DEBUG`, `HOST` e `PORT` do ambiente, com padrão `DEBUG=false` e `HOST=127.0.0.1` (T-01).

### F-07 [HIGH] Regra de negócio e orquestração dentro dos models
File: models.py:137-169, 256-262
Catalog: AP-09
Description: `criar_pedido` valida existência e estoque, calcula o total (`total = total + (produto["preco"] * item["quantidade"])`), grava pedido e itens e debita o estoque, tudo na camada de dados. `relatorio_vendas` aplica faixas de desconto (`if faturamento > 10000: desconto = faturamento * 0.1`).
Impact: A regra de pedido e a política de desconto só podem ser testadas com banco, e qualquer mudança de regra exige mexer na persistência. O model devolve `{"erro": ...}` como valor, misturando fluxo de erro com dados.
Recommendation: Mover a validação de estoque, o cálculo de total e o desconto para um service ou controller de pedidos e relatórios, deixando no repositório só leitura e escrita (T-04).

### F-08 [HIGH] Criação de pedido sem transação e com checagem de estoque não atômica
File: models.py:139-168
Catalog: AP-12
Description: O fluxo faz `SELECT` de estoque, depois `INSERT INTO pedidos`, depois, para cada item, `INSERT INTO itens_pedido` e `UPDATE produtos SET estoque = estoque - ...`, com um único `db.commit()` no fim e sem `rollback`. Como a conexão é compartilhada (F-09), uma exceção no meio deixa as escritas pendentes, e o `commit()` da próxima requisição as grava.
Impact: Pedidos sem itens, estoque debitado pela metade e venda acima do estoque quando dois pedidos concorrentes passam pela checagem antes do débito.
Recommendation: Executar o pedido inteiro numa transação (`with conn:`, que faz commit ou rollback) numa conexão por requisição, e debitar com `UPDATE ... WHERE id = ? AND estoque >= ?` (T-10).

### F-09 [HIGH] Conexão global única e controllers acessando o driver direto
File: database.py:4-11 | controllers.py:3, 264-274 | app.py:4, 49-55, 66-76
Catalog: AP-10, AP-11
Description: `db_connection` é global (`global db_connection`), criada uma vez com `check_same_thread=False` e compartilhada por todas as requisições e threads. `health_check` e as rotas admin chamam `get_db()` e executam SQL direto, pulando a camada de model.
Impact: Condições de corrida entre requisições concorrentes (o servidor do Flask usa threads), transações que se misturam (F-08) e nenhuma forma de substituir o banco em testes.
Recommendation: Usar uma conexão por requisição guardada em `flask.g` e fechada em `teardown_appcontext`, com caminho do banco vindo da config, e fazer todo acesso a dados passar por repositórios (T-05).

### F-10 [HIGH] `app.py` acumula configuração, rotas, SQL administrativo e boot
File: app.py:6-9, 11-30, 32-45, 47-78, 80-88
Catalog: AP-05 (rebaixado para HIGH: já existem `controllers.py` e `models.py` separados)
Description: O mesmo arquivo configura a aplicação (segredo, debug, CORS), registra todas as rotas, implementa handlers com SQL (`cursor.execute("DELETE FROM itens_pedido")`) e sobe o servidor.
Impact: Não é possível criar a app para testes sem carregar configuração fixa nem separar a administração do resto, e cada novo domínio aumenta o arquivo.
Recommendation: Criar um composition root (`create_app()`) que monte config, banco, blueprints e error handlers, com rotas por domínio em `routes/` (T-03, T-16).

### F-11 [HIGH] Controllers com validação, regras e efeitos colaterais misturados ao HTTP
File: controllers.py:24-62, 64-96, 188-220, 237-255
Catalog: AP-08
Description: Os handlers leem o request, validam campo a campo, aplicam regras de domínio (lista de categorias válidas, transições de status) e simulam notificações (`print("ENVIANDO EMAIL: Pedido " ...)`, `print("NOTIFICAÇÃO: ... Devolver estoque.")`) na mesma função. Não existe camada de rotas: `controllers.py` faz o papel de view e de controller.
Impact: As regras ficam presas ao contexto HTTP (`request.get_json()` dentro da regra). O cancelamento promete "Devolver estoque", mas nenhum código faz isso.
Recommendation: Rotas fazem só parsing e resposta; controllers e services recebem dados já validados e disparam notificações por um serviço dedicado (T-04).

### F-12 [MEDIUM] Validação de entrada ausente ou inconsistente
File: controllers.py:43-54, 72-90, 118-121, 169-170, 239-240 | models.py:140, 144, 164
Catalog: AP-17
Description: O PUT de produto não valida tamanho do nome nem categoria, validação que o POST faz (43-54 × 72-90). `preco`/`estoque` não têm checagem de tipo (`"abc" < 0` gera `TypeError` → 500). `login` e `atualizar_status_pedido` chamam `dados.get(...)` com body possivelmente `None` (→ 500). `float(preco_min)` com texto gera 500. Nos itens do pedido, a falta de `produto_id` gera `KeyError` → 500, e `quantidade` negativa passa na checagem de estoque, gera total negativo e **aumenta** o estoque (`estoque = estoque - -5`).
Impact: Dados inválidos no banco, manipulação de estoque e faturamento, e erros 500 onde deveria haver 400.
Recommendation: Centralizar validadores por entidade usados pelo POST e pelo PUT, com checagem de tipo, body nulo e `quantidade > 0` inteira (T-11).

### F-13 [MEDIUM] Tratamento de erro disperso, genérico e com formatos diferentes
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292 | app.py:77-78 | controllers.py:245-252 | models.py:279-283
Catalog: AP-16
Description: Cada handler repete `try/except Exception as e: return jsonify({"erro": str(e)}), 500`. Os formatos de erro variam: `{erro, sucesso}` (404 de produto), `{erro}` (404 de usuário) e `{status, detalhes}` (health). `PUT /pedidos/<id>/status` responde 200 "Status atualizado" mesmo para pedido inexistente, porque o UPDATE não confere `rowcount`.
Impact: O contrato de erro é imprevisível para o cliente, bugs ficam escondidos em 500 genéricos e a API informa sucesso sem ter alterado nada.
Recommendation: Registrar um error handler central (`@app.errorhandler`) com exceções de domínio (`NotFound`, `ValidationError`), mantendo as chaves de resposta atuais (T-09).

### F-14 [MEDIUM] Queries N+1 na listagem de pedidos e agregações separadas no relatório
File: models.py:186-199, 219-231, 239-254
Catalog: AP-15
Description: Para cada pedido é feita uma query de itens (`cursor2`) e, para cada item, uma query do nome do produto (`cursor3`). O relatório faz cinco queries (`COUNT`, `SUM` e três `COUNT ... WHERE status = ...`).
Impact: Com P pedidos e I itens, a listagem executa 1 + P + P·I queries, e o tempo de resposta cresce com o histórico.
Recommendation: Buscar itens com `JOIN produtos` numa única query agrupada por pedido e usar `GROUP BY status` com `SUM(CASE ...)` no relatório (T-08).

### F-15 [MEDIUM] Código duplicado em mapeamentos, listagens e validações
File: models.py:12-21, 31-40, 304-313 | models.py:79-86, 95-102 | models.py:171-201, 203-233 | controllers.py:28-46, 72-90
Catalog: AP-18
Description: O mapeamento row → dict de produto aparece três vezes e o de usuário duas. `get_pedidos_usuario` e `get_todos_pedidos` são idênticas, exceto pelo `WHERE`. A validação de produto está copiada entre POST e PUT, e a cópia já divergiu (F-12).
Impact: Correções aplicadas num lugar não chegam aos outros. A remoção de `senha` (F-03), por exemplo, teria que ser feita em dois lugares.
Recommendation: Criar uma função de serialização por entidade, uma listagem de pedidos parametrizada e um validador compartilhado (T-04, T-11).

### F-16 [MEDIUM] Logging com `print`, sem níveis e com dados pessoais
File: app.py:56, 83-86 | controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Catalog: AP-20
Description: Eventos, erros e "envios" de e-mail/SMS/push são registrados com `print`, incluindo o e-mail de cada tentativa de login (`print("Login falhou: " + email)`).
Impact: Não há níveis nem destino configurável, e dados pessoais vão para a saída padrão sem controle.
Recommendation: Usar o módulo `logging` com logger por módulo e níveis adequados, sem registrar credenciais (T-14).

### F-17 [MEDIUM] CORS aberto, host/porta/banco fixos e schema criado como efeito colateral
File: app.py:9, 88 | database.py:5, 7-86
Catalog: AP-21
Description: `CORS(app)` libera qualquer origem numa API sem autenticação. `db_path = "loja.db"` é relativo ao diretório de execução, e a porta 5000 é fixa (no macOS costuma estar ocupada pelo AirPlay). O schema e o seed rodam escondidos na primeira chamada de `get_db()`.
Impact: Qualquer site pode chamar a API a partir do navegador de um usuário, o banco muda de lugar conforme o diretório de onde a app é iniciada e não dá para subir duas instâncias ou trocar a porta sem editar código.
Recommendation: Ler origens de CORS, porta, host e caminho do banco da config e inicializar schema e seed explicitamente no `create_app` (T-01, T-16).

### F-18 [LOW] Magic numbers e strings de negócio
File: models.py:150, 247, 250, 253, 257-262 | controllers.py:47-50, 52, 242 | app.py:36, 88 | controllers.py:285
Catalog: AP-22
Description: Faixas de desconto (`10000`, `0.1`, `5000`, `0.05`, `1000`, `0.02`), limites de nome (`2`, `200`), a lista de categorias, a lista de status, os status `'pendente'`/`'aprovado'`/`'cancelado'` como literais repetidos, a versão `"1.0.0"` duplicada e a porta `5000`.
Impact: As regras ficam implícitas e espalhadas, e mudar uma faixa ou um status exige caçar literais.
Recommendation: Definir constantes nomeadas num módulo de domínio (`DISCOUNT_TIERS`, `VALID_CATEGORIES`, `ORDER_STATUSES`, `API_VERSION`) (T-13).

### F-19 [LOW] Nomes que sombreiam builtins e cursores numerados
File: controllers.py:14, 56, 64, 98, 136, 160 | models.py:24, 54, 65, 89, 187, 191, 219, 223
Catalog: AP-23
Description: Parâmetros e variáveis chamados `id` sombreiam o builtin, e há cursores numerados (`cursor2`, `cursor3`).
Impact: A leitura fica mais lenta e há risco de usar o builtin errado.
Recommendation: Renomear para `produto_id`, `usuario_id`, `novo_id` e similares, eliminando os cursores extras junto com F-14 (T-13). O nome do parâmetro de rota `<int:id>` não faz parte do contrato HTTP.

### F-20 [LOW] Imports e comandos sem uso
File: models.py:2 | database.py:2 | controllers.py:268
Catalog: AP-24
Description: `import sqlite3` em models.py e `import os` em database.py nunca são usados, e `cursor.execute("SELECT 1")` no health tem o resultado descartado.
Impact: É ruído que sugere dependências inexistentes.
Recommendation: Remover (T-13).

## Deprecated APIs

Nenhuma API deprecated encontrada para as versões instaladas (Python 3.12.0, Flask 3.1.1, Werkzeug 3.1.8, flask-cors 5.0.1). O boot com `python -W default` não emitiu `DeprecationWarning`, e o `sqlite3` é usado sem `detect_types`, então os adapters de datetime deprecated no 3.12 não entram em ação.

## Architecture Overview

- **Current:** Parcialmente em camadas. Existem `controllers.py`, `models.py` e `database.py`, mas `app.py` mistura config, rotas, SQL e boot; os controllers acumulam validação e regras; os models concentram regra de negócio e SQL concatenado; e a conexão é global.
- **Target:** Pacote `src/` com `config.py`, `database.py` (conexão por requisição), `models/` (repositórios por entidade com SQL parametrizado), `controllers/` (regras de produto, usuário, pedido e relatório), `routes/` (blueprints só com HTTP), `middlewares/` (error handler e autenticação admin), mantendo `app.py` como entry point que chama `create_app()`.

```
================================
Total: 20 findings
================================
```
