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

CRITICAL: 6 | HIGH: 6 | MEDIUM: 7 | LOW: 4

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 6 | F-01, F-02, F-03, F-04, F-05, F-06 |
| HIGH | 6 | F-07, F-08, F-09, F-10, F-11, F-12 |
| MEDIUM | 7 | F-13, F-14, F-15, F-16, F-17, F-18, F-19 |
| LOW | 4 | F-20, F-21, F-22, F-23 |

## Findings

### F-01 [CRITICAL] SQL Injection em praticamente todas as queries
File: models.py:28, 48-49, 57-60, 68, 92, 109-110, 126-128, 140, 148-150, 155, 157-160, 163-165, 174, 188, 192, 220, 224, 279-280, 289-297
Catalog: AP-02
Description: Todas as queries com parâmetros são montadas por concatenação, por exemplo no login: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` e na busca: `" AND (nome LIKE '%" + termo + "%' ..."`.
Impact: `POST /login` com `{"email": "admin@loja.com' --", "senha": "x"}` autentica como admin sem senha; `GET /produtos/busca?q=' UNION SELECT ...` lê qualquer tabela (inclusive senhas); qualquer nome com apóstrofo (ex.: `Monitor 27''` do próprio seed, se reenviado) quebra o INSERT com erro 500.
Recommendation: Queries parametrizadas com placeholders `?` em todos os models (T-02).

### F-02 [CRITICAL] Endpoints administrativos sem autenticação executam SQL arbitrário e apagam o banco
File: app.py:47-57, 59-78
Catalog: AP-06 / AP-02
Description: `POST /admin/query` executa o SQL recebido no corpo (`cursor.execute(query)`, app.py:69) e `POST /admin/reset-db` faz `DELETE FROM` em todas as tabelas (app.py:51-54), ambos sem qualquer verificação de identidade. O `POST /login` (controllers.py:167-186) não emite token nem sessão, então não existe mecanismo de autorização algum na API.
Impact: Qualquer cliente de rede lê a tabela `usuarios` com senhas, altera preços/estoques, faz `DROP TABLE` ou zera o banco com uma única requisição (confirmado na linha de base: #33 e #35 responderam 200 sem credencial).
Recommendation: Proteger `/admin/*` com token administrativo lido do ambiente (comparação com `hmac.compare_digest`), desabilitar as rotas quando o token não estiver configurado e restringir `/admin/query` a leitura (T-15).

### F-03 [CRITICAL] Segredos e credenciais hardcoded
File: app.py:7 | controllers.py:289 | database.py:76-78
Catalog: AP-01
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está fixo no código e repetido literalmente na resposta do health (`"secret_key": "minha-chave-super-secreta-123"`). O seed cria o usuário `("Admin", "admin@loja.com", "admin123", "admin")` com senha fixa versionada.
Impact: A chave de assinatura de sessões fica no repositório e não pode ser trocada por ambiente; qualquer instalação nova tem um administrador com senha conhecida publicamente.
Recommendation: Módulo de config lendo `SECRET_KEY` (e demais valores) de variáveis de ambiente, `.env.example` sem valores reais, senhas do seed configuráveis e gravadas com hash (T-01, T-06).

### F-04 [CRITICAL] Senhas, configuração interna e erros internos expostos nas respostas
File: models.py:83, 99 | controllers.py:286-289 | controllers.py:12, 22, 62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292 | app.py:78
Catalog: AP-03
Description: `get_todos_usuarios` e `get_usuario_por_id` serializam `"senha": row["senha"]`, e `GET /usuarios` é público. O `GET /health` devolve `secret_key`, `db_path`, `debug` e `ambiente`. Todos os handlers devolvem `jsonify({"erro": str(e)})` com a mensagem interna da exceção.
Impact: `GET /usuarios` entrega e-mail e senha em texto puro de todos os usuários (confirmado na linha de base #14/#15); o health entrega a chave secreta; mensagens de erro revelam nomes de tabelas/colunas e ajudam a explorar o F-01.
Recommendation: Remover `senha` da serialização de usuário, remover `secret_key`/`db_path`/`debug` do health e devolver mensagem genérica em erros 500, registrando o detalhe só no log (T-07, T-09).

### F-05 [CRITICAL] Senhas armazenadas e comparadas em texto puro
File: models.py:109-110, 126-128 | database.py:75-83
Catalog: AP-04
Description: `criar_usuario` grava a senha recebida como está (`"... VALUES ('" + nome + "', '" + email + "', '" + senha + "' ..."`), o login compara `AND senha = '" + senha + "'` direto no SQL e o seed insere `"admin123"`, `"123456"`, `"senha123"` sem hash.
Impact: Qualquer vazamento do arquivo `loja.db` (ou uma leitura via F-01/F-02) expõe as senhas reais de todos os usuários, que costumam ser reutilizadas em outros serviços.
Recommendation: Gravar hash com salt (`werkzeug.security.generate_password_hash`) e verificar com `check_password_hash` no model de usuário (T-06).

### F-06 [CRITICAL] Modo debug fixo com bind público
File: app.py:8, 88 | controllers.py:288
Catalog: AP-07
Description: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` fixos; o health ainda anuncia `"debug": True`. O log da linha de base mostra `Debugger is active!`.
Impact: O debugger interativo do Werkzeug fica acessível em todas as interfaces de rede e permite execução remota de código quando uma exceção não tratada chega a ele; o reloader também roda em produção.
Recommendation: `DEBUG` e `HOST` lidos do ambiente com padrão seguro (`False` / `127.0.0.1`) no módulo de config (T-01).

### F-07 [HIGH] Regras de negócio dentro dos models
File: models.py:133-169, 256-262
Catalog: AP-09
Description: `criar_pedido` no model valida existência do produto, checa estoque (`if produto["estoque"] < item["quantidade"]`), calcula o total, cria o pedido, os itens e debita o estoque. `relatorio_vendas` aplica a regra de desconto por faixa de faturamento (`if faturamento > 10000: desconto = faturamento * 0.1 ...`).
Impact: A regra de pedido e de desconto só pode ser testada com banco real e muda junto com o SQL; a camada de dados decide o fluxo de negócio e devolve erros como dicts (`{"erro": ...}`) em vez de exceções.
Recommendation: Mover a orquestração para `PedidoController`/serviço e a regra de desconto para o controller de relatórios; models ficam só com leitura/gravação (T-04).

### F-08 [HIGH] Controllers com validação, notificações e fluxo de status acoplados ao HTTP
File: controllers.py:24-62, 64-96, 188-220, 237-255
Catalog: AP-08
Description: Os handlers leem `request.get_json()`, validam campo a campo, definem a lista de categorias válidas, simulam envio de e-mail/SMS/push (`print("ENVIANDO EMAIL: ...")`, linhas 208-210) e decidem efeitos colaterais por status (`if novo_status == "cancelado": print("... Devolver estoque.")`, linhas 247-250) — tudo na mesma função que monta o `jsonify`.
Impact: Nenhuma dessas regras pode ser reutilizada ou testada sem um request Flask; a notificação de cancelamento promete devolver estoque, mas nada devolve, e essa divergência fica escondida no handler.
Recommendation: Separar rotas (parsing HTTP e resposta) de controllers (validação e orquestração) e de um serviço de notificação (T-04, T-11).

### F-09 [HIGH] `app.py` acumula configuração, registro de rotas e handlers com SQL
File: app.py:6-9, 11-30, 32-45, 47-78, 80-88
Catalog: AP-05 (rebaixado para HIGH: as funções são pequenas e separáveis)
Description: O entry point configura a app com segredos, registra todas as rotas, contém dois handlers administrativos que abrem cursor e executam SQL direto (`cursor.execute("DELETE FROM itens_pedido")`), monta a resposta do índice e inicializa o banco no `__main__`.
Impact: O composition root também é camada de dados e de controle; não há como criar a app para testes (sem `create_app`) nem trocar configuração por ambiente.
Recommendation: Composition root com `create_app()` que só monta config, banco, blueprints e error handlers; handlers admin vão para rota/controller/model próprios (T-16, T-03).

### F-10 [HIGH] Conexão SQLite global única e mutável compartilhada por todas as requisições
File: database.py:4-11
Catalog: AP-10
Description: `global db_connection` guarda uma única conexão criada com `check_same_thread=False` e reutilizada por todas as threads do servidor.
Impact: Requisições concorrentes compartilham o mesmo estado transacional: uma escrita que falha no meio deixa alterações pendentes que o `commit()` da próxima requisição (de outro usuário) persiste; acesso concorrente ao mesmo objeto de conexão sem lock.
Recommendation: Conexão por requisição (`flask.g`) fechada no `teardown_appcontext`, com schema/seed executados uma vez no `create_app` (T-05).

### F-11 [HIGH] Controllers e rotas acessam o driver do banco diretamente
File: controllers.py:3, 264-274 | app.py:4, 49-55, 66-69
Catalog: AP-11
Description: `health_check` chama `get_db()` e executa `SELECT COUNT(*)` direto no controller; os handlers admin de `app.py` fazem o mesmo. Todos os models chamam a função global `get_db()` em vez de receber a conexão.
Impact: Controllers não podem ser testados com um model falso; a mesma contagem de tabelas existe em dois lugares (health e relatório) com SQL diferente.
Recommendation: Contagens e comandos administrativos em models dedicados; controllers dependem só dos models (T-05).

### F-12 [HIGH] Criação de pedido em várias etapas sem transação explícita
File: models.py:137-168
Catalog: AP-12
Description: A checagem de estoque (linhas 139-146) é feita num laço e o `INSERT` do pedido, os `INSERT` dos itens e os `UPDATE` de estoque (linhas 148-166) em outro, com um único `db.commit()` no fim e nenhum `rollback()` em caso de erro.
Impact: Se qualquer instrução do segundo laço falhar, o pedido e parte dos itens ficam pendentes na conexão compartilhada (F-10) e são gravados pelo próximo `commit` de qualquer requisição, gerando pedido sem itens ou estoque debitado pela metade. Entre a checagem e o débito, outra requisição pode consumir o mesmo estoque.
Recommendation: Envolver a criação do pedido em uma transação (`with conn:` / `BEGIN ... COMMIT/ROLLBACK`) e usar a conexão por requisição (T-10, T-05).

### F-13 [MEDIUM] Validação de entrada ausente ou inconsistente (inclusive quantidade negativa)
File: controllers.py:43-50, 81-90, 118-121, 153-158, 169-170, 195-201, 239-240 | app.py:61-62 | models.py:140, 144, 164
Catalog: AP-17
Description: O `PUT /produtos/<id>` não valida tamanho do nome nem categoria, que o `POST` valida (linhas 47-54 × 81-90). Tipos não são checados (`preco < 0` com `"abc"` lança `TypeError`). `dados.get(...)` é chamado com corpo possivelmente nulo em `login`, `atualizar_status_pedido` e `/admin/query`. Os itens do pedido não são validados: `item["produto_id"]` sem chave gera `KeyError`, e `quantidade` negativa passa por `produto["estoque"] < item["quantidade"]` e executa `estoque - -5`.
Impact: Entradas simples viram 500 em vez de 400; um pedido com `quantidade: -5` gera total negativo e **aumenta** o estoque; produtos atualizados podem ficar com categoria inválida.
Recommendation: Validadores por entidade reutilizados em criação e atualização, com checagem de tipo e de corpo nulo, devolvendo 400 (T-11).

### F-14 [MEDIUM] Tratamento de erro repetido, genérico e com status errado
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292 | app.py:77-78 | controllers.py:245 | models.py:279-283
Catalog: AP-16
Description: Cada handler repete `try: ... except Exception as e: return jsonify({"erro": str(e)}), 500`; não há `@app.errorhandler`. Os formatos de erro variam (`{erro}`, `{erro, sucesso}`, `{status, detalhes}`). `PUT /pedidos/<id>/status` devolve 200 mesmo quando o pedido não existe, porque o `UPDATE` não verifica `rowcount`.
Impact: Contrato de erro imprevisível, bugs escondidos atrás de 500 genéricos e sucesso falso para pedidos inexistentes.
Recommendation: Exceções de domínio (`NotFoundError`, `ValidationError`) e handler central de erros; manter as chaves de erro atuais de cada endpoint (T-09).

### F-15 [MEDIUM] Queries N+1 na listagem de pedidos e agregações separadas no relatório
File: models.py:186-199, 219-231, 239-254
Catalog: AP-15
Description: Para cada pedido é feita uma query de itens (`cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " ...)`) e, para cada item, outra query de produto (`cursor3`). O relatório executa cinco consultas separadas (`COUNT`, `SUM` e três `COUNT ... WHERE status = ...`).
Impact: `GET /pedidos` com 100 pedidos de 3 itens dispara ~400 queries; o tempo cresce linearmente com o volume.
Recommendation: `LEFT JOIN` de itens com produtos numa única query agrupada em memória e um único `SELECT` com `SUM(CASE ...)` para o relatório (T-08).

### F-16 [MEDIUM] Código duplicado em serialização, listagens de pedido e validação
File: models.py:12-21, 31-40, 304-313 | models.py:79-86, 95-102 | models.py:171-201, 203-233 | controllers.py:28-45, 72-90
Catalog: AP-18
Description: O mapeamento row → dict de produto aparece três vezes e o de usuário duas; `get_pedidos_usuario` e `get_todos_pedidos` são idênticos exceto pelo `WHERE`; a validação de produto é copiada entre `criar_produto` e `atualizar_produto` (e já divergiu, ver F-13).
Impact: Correções precisam ser feitas em vários lugares; a remoção de `senha` (F-04), por exemplo, teria de ser repetida em duas funções.
Recommendation: Funções únicas de serialização por entidade, uma query de pedidos com filtro opcional e validador compartilhado (T-04, T-11).

### F-17 [MEDIUM] Um único módulo de controllers e de models para todos os domínios; admin no entry point
File: controllers.py:5-292 | models.py:4-314 | app.py:47-78
Catalog: AP-26
Description: `controllers.py` e `models.py` misturam produtos, usuários, pedidos, relatórios e health no mesmo arquivo; os endpoints administrativos ficam dentro de `app.py` em vez de num módulo próprio.
Impact: Para entender ou alterar um domínio é preciso navegar por arquivos de 300 linhas com todos os outros; os handlers admin ficam escondidos no entry point.
Recommendation: Um módulo por domínio em cada camada (`models/produto.py`, `controllers/produto_controller.py`, `routes/produtos.py` etc.) (T-18).

### F-18 [MEDIUM] CORS aberto, porta/host/caminho do banco fixos e schema/seed como efeito colateral
File: app.py:9, 88 | database.py:5, 7-84
Catalog: AP-21
Description: `CORS(app)` libera qualquer origem; a porta 5000 e o host estão fixos em `app.run`; `db_path = "loja.db"` é relativo ao diretório de execução; o `CREATE TABLE` e o seed rodam escondidos dentro do primeiro `get_db()`.
Impact: Qualquer site pode chamar a API a partir do navegador de um usuário; a app não sobe se a porta 5000 estiver ocupada (caso comum no macOS por causa do AirPlay) e cria um banco novo vazio se for executada de outra pasta.
Recommendation: Origens CORS, porta, host e caminho do banco lidos da config; inicialização do schema/seed explícita no `create_app` (T-01, T-16).

### F-19 [MEDIUM] Logging com `print`, sem níveis, incluindo e-mails de usuários
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250 | app.py:56, 83-86
Catalog: AP-20
Description: Eventos e erros são registrados com `print("Login falhou: " + email)`, `print("ERRO: " + str(e))` e notificações simuladas com `print("ENVIANDO EMAIL: ...")`; nenhum uso do módulo `logging`.
Impact: Sem nível nem destino configurável; erros se misturam a mensagens de banner; e-mails (dado pessoal) vão para a saída padrão sem controle.
Recommendation: `logging.getLogger(__name__)` com níveis adequados e configuração central; notificações num serviço dedicado (T-14).

### F-20 [LOW] Magic numbers e strings de negócio espalhados
File: models.py:257-262 | controllers.py:47-50, 52, 242 | models.py:150, 247, 250, 253 | app.py:36, 88 | controllers.py:285-286
Catalog: AP-22
Description: Faixas de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`), limites de nome (`2`, `200`), lista de categorias e lista de status definidas inline; status `'pendente'`, `'aprovado'`, `'cancelado'` repetidos como literais; versão `"1.0.0"` duplicada; porta `5000`.
Impact: A regra fica implícita; adicionar um status ou categoria exige caçar literais em vários arquivos.
Recommendation: Constantes nomeadas por domínio (`CATEGORIAS_VALIDAS`, `STATUS_PEDIDO`, `FAIXAS_DESCONTO`, `API_VERSION`) (T-13).

### F-21 [LOW] Regra de desconto codificada como cadeia de `if/elif` por faixa
File: models.py:256-262
Catalog: AP-25
Description: `if faturamento > 10000: ... elif faturamento > 5000: ... elif faturamento > 1000: ...` compara faixas do mesmo valor.
Impact: Incluir ou alterar uma faixa exige mexer no fluxo em vez de num dado; a regra não pode ser lida nem testada isoladamente.
Recommendation: Tabela de faixas ordenada percorrida por uma função pura de cálculo (T-17a).

### F-22 [LOW] Nomes que sombreiam builtins e cursores numerados
File: controllers.py:14, 56, 64, 98, 136, 160 | models.py:24, 54, 65, 89, 187, 191, 219, 223
Catalog: AP-23
Description: Parâmetros e variáveis chamados `id` (sombreiam o builtin) e cursores `cursor2`, `cursor3`.
Impact: Leitura mais lenta e risco de usar o builtin por engano.
Recommendation: Nomes descritivos (`produto_id`, `usuario_id`, `itens_cursor`) mantendo os nomes de parâmetro de rota exigidos pelo Flask (T-13).

### F-23 [LOW] Imports e instruções sem uso
File: models.py:2 | database.py:2 | controllers.py:268
Catalog: AP-24
Description: `import sqlite3` em `models.py` e `import os` em `database.py` nunca são usados; `cursor.execute("SELECT 1")` no health é executado e o resultado descartado.
Impact: Ruído que sugere dependências que não existem.
Recommendation: Remover os imports e a instrução mortos (T-13).

## Deprecated APIs

Nenhuma API deprecated encontrada para as versões instaladas (Flask 3.1.1, Werkzeug resolvido pelo Flask 3.1.1, flask-cors 5.0.1, Python 3.12.0). A aplicação subiu com `python -W default` sem nenhum `DeprecationWarning`; o código não usa `before_first_request`, `json_encoder`, `FLASK_ENV` nem passa objetos `datetime` ao `sqlite3` (as datas vêm do `DEFAULT CURRENT_TIMESTAMP`).

## Architecture Overview

- **Current:** Monolítica — apesar dos nomes `models.py`/`controllers.py`, `app.py` configura, roteia e executa SQL; controllers validam, notificam e acessam o banco; models concatenam SQL e decidem regras de pedido e desconto; conexão global única.
- **Target:** Pacote `app/` com `config.py`, `database.py` (conexão por requisição), `models/` por entidade (SQL parametrizado), `controllers/` (validação e regras), `routes/` (blueprints finos), `services/notificacoes.py`, `errors.py` (handler central) e `app.py` na raiz como composition root, preservando `python app.py`.

```
================================
Total: 23 findings
================================
```
