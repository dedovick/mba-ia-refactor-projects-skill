# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.12 + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Date:    2026-09-27
================================
```

## Summary

CRITICAL: 8 | HIGH: 8 | MEDIUM: 7 | LOW: 4
Probes: 23 vulneráveis de 27 executadas — todas cobertas por findings (F-01, F-02, F-03, F-04, F-06, F-08, F-09, F-10, F-17, F-18)

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 8 | F-01, F-02, F-03, F-04, F-05, F-06, F-07, F-08 |
| HIGH | 8 | F-09, F-10, F-11, F-12, F-13, F-14, F-15, F-16 |
| MEDIUM | 7 | F-17, F-18, F-19, F-20, F-21, F-22, F-23 |
| LOW | 4 | F-24, F-25, F-26, F-27 |

## Findings

### F-01 [CRITICAL] SQL Injection em todas as queries com parâmetro
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291, 293, 295, 297
Catalog: AP-02
Evidence: probe P1, P2 (login como admin sem senha), P9, P10 (apóstrofo → 500), P11 (filtro `categoria` devolve os 10 produtos)
Description: Toda query com valor variável é montada por concatenação, inclusive a de autenticação: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (models.py:110) e a busca `" AND categoria = '" + categoria + "'"` (models.py:293).
Impact: `{"email": "admin@loja.com' --"}` autentica como administrador com qualquer senha; filtros podem ser burlados para ler o banco inteiro; qualquer nome com apóstrofo (`O'Reilly`, `D'Ávila`) não pode ser cadastrado.
Recommendation: Queries parametrizadas com placeholders `?` em todos os repositórios, sem nenhuma concatenação de valor (T-02).

### F-02 [CRITICAL] Endpoints administrativos sem autenticação executam SQL arbitrário e apagam o banco
File: app.py:47-57, 59-78
Catalog: AP-06, AP-02
Evidence: probe P6 (`SELECT email, senha FROM usuarios` devolveu todas as senhas), probe P25 (reset apagou todas as tabelas; `GET /produtos` → 0 itens)
Description: `POST /admin/query` executa o SQL recebido no corpo (`cursor.execute(query)`, app.py:69) e `POST /admin/reset-db` roda `DELETE FROM` em todas as tabelas (app.py:51-54), sem nenhuma verificação de identidade ou papel.
Impact: Qualquer pessoa com acesso à rede lê, altera ou destrói todos os dados, incluindo credenciais.
Recommendation: Exigir credencial administrativa (token lido do ambiente, comparado com `hmac.compare_digest`) nas rotas `/admin/*`, que respondem 401/403 sem ela; limitar `/admin/query` a leitura (SELECT) (T-15).

### F-03 [CRITICAL] Senhas devolvidas nas respostas de usuários
File: models.py:83, 99 | controllers.py:130-132, 138-140
Catalog: AP-03
Evidence: probe P3 (`GET /usuarios`), probe P4 (`GET /usuarios/1`); baseline #8, #9
Description: O mapeamento row → dict inclui `"senha": row["senha"]` e os handlers devolvem o dict direto em `jsonify({"dados": usuarios, ...})`.
Impact: Qualquer cliente obtém a senha em texto puro de todos os usuários, incluindo o admin (`admin123`).
Recommendation: Serializador público de usuário sem `senha`; o hash só é lido dentro do model para verificar o login (T-07).

### F-04 [CRITICAL] Pedido criado em nome de qualquer `usuario_id`, inclusive inexistente
File: controllers.py:195-203 | models.py:148-151
Catalog: AP-06
Evidence: probe P22 (`usuario_id: 999` → 201, pedido gravado e "email" enviado para usuário 999)
Description: `criar_pedido` usa `usuario_id = dados.get("usuario_id")` vindo do cliente sem verificar se a conta existe nem quem está fazendo o pedido; o `login` (controllers.py:176-180) não emite token/sessão que outra rota valide.
Impact: Qualquer pessoa compra e baixa estoque em nome de outro cliente, e pedidos órfãos entram no faturamento do relatório de vendas.
Recommendation: No mínimo, validar que `usuario_id` existe e recusar com erro 4xx; autenticação por token por pedido é decisão de produto (a registrar se ficar fora do escopo) (T-15, T-11).

### F-05 [CRITICAL] Senhas armazenadas e comparadas em texto puro
File: models.py:110, 127-128 | database.py:31, 75-83
Catalog: AP-04
Evidence: probe P6 (senhas legíveis direto na tabela)
Description: `criar_usuario` grava `senha` como veio (`"... VALUES ('" + nome + "', '" + email + "', '" + senha + "'..."`) e o login compara `AND senha = '...'` no SQL; o seed cria `("Admin", "admin@loja.com", "admin123", "admin")` em texto puro.
Impact: Qualquer leitura do banco (backup, F-02, F-01) expõe todas as senhas, reaproveitáveis em outros serviços.
Recommendation: Hash com salt e algoritmo lento (`werkzeug.security.generate_password_hash` / `check_password_hash`, já disponível via Flask), inclusive no seed, e login que busca por e-mail e verifica o hash (T-06).

### F-06 [CRITICAL] Debug do Werkzeug ativo com bind público
File: app.py:8, 88 | controllers.py:288
Catalog: AP-07
Evidence: boot log (`Debug mode: on`, `Debugger is active!`, `Running on all addresses (0.0.0.0)`); probe P27 (traceback completo em `POST /admin/query` com body `null`)
Description: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` fixos no código.
Impact: Qualquer exceção não tratada abre o debugger interativo do Werkzeug para a rede, o que permite execução remota de código.
Recommendation: `DEBUG` lido do ambiente com padrão `False`; host e porta configuráveis (T-01).

### F-07 [CRITICAL] SECRET_KEY hardcoded e duplicada
File: app.py:7 | controllers.py:289
Catalog: AP-01
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`, repetida como literal na resposta do health check.
Impact: A chave vaza com o repositório (e pela API, ver F-08) e não pode ser trocada por ambiente; qualquer assinatura feita com ela pode ser forjada.
Recommendation: Módulo de config lendo `SECRET_KEY` do ambiente, com `.env.example` sem valor real (T-01).

### F-08 [CRITICAL] Health check expõe configuração interna e segredo
File: controllers.py:276-290
Catalog: AP-03
Evidence: probe P5; baseline #2
Description: `GET /health` devolve `"secret_key": "minha-chave-super-secreta-123"`, `"debug": True`, `"db_path": "loja.db"` e `"ambiente": "producao"`.
Impact: Um endpoint público entrega a chave de assinatura e informações de infraestrutura a qualquer cliente.
Recommendation: Remover `secret_key`, `db_path` e `debug` da resposta; manter `status`, `database`, `counts`, `versao`, `ambiente` (T-07).

### F-09 [HIGH] Tratamento de erro disperso que devolve `str(e)` ao cliente
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292 | app.py:61-62, 77-78
Catalog: AP-16, AP-03
Evidence: probe P9, P10 (`{"erro": "near \"Reilly\": syntax error"}`), P12-P16, P18 (500 com mensagem interna), P17/P27 (exceção fora do `try` → traceback)
Description: Cada um dos 16 handlers repete `except Exception as e: return jsonify({"erro": str(e)}), 500`; em `executar_query`, `dados.get("sql", "")` fica fora do `try` e estoura sem tratamento. O formato do erro varia (`{erro}`, `{erro, sucesso}`, `{status, detalhes}`).
Impact: Mensagens internas do SQLite e do Python chegam ao cliente (revelam estrutura das queries), erros de entrada viram 500 e o contrato de erro é imprevisível.
Recommendation: Handler central (`@app.errorhandler`) com exceções de domínio (`ValidationError` → 400, `NotFoundError` → 404) e 500 genérico sem detalhes, com log no servidor (T-09).

### F-10 [HIGH] Pedido aceita quantidade negativa ou zero: total negativo e estoque aumentado
File: controllers.py:195-201 | models.py:139-146, 163-166
Catalog: AP-17
Evidence: probe P19 (`quantidade: -5` → 201, `total: -1499.5`, estoque do produto 3 de 30 para 35), probe P20 (`quantidade: 0` → 201)
Description: Os itens só são checados com `if not itens or len(itens) == 0`; `produto["estoque"] < item["quantidade"]` passa com negativo e `"UPDATE produtos SET estoque = estoque - " + str(item["quantidade"])` soma estoque.
Impact: Qualquer cliente cria estoque do nada e gera faturamento negativo, distorcendo o relatório de vendas.
Recommendation: Validar cada item (`produto_id` inteiro, `quantidade` inteiro > 0) antes de qualquer acesso ao banco (T-11).

### F-11 [HIGH] Regras de negócio dentro da camada de dados
File: models.py:133-169, 256-262
Catalog: AP-09
Description: `criar_pedido` no model decide disponibilidade (`if produto["estoque"] < item["quantidade"]`), calcula o total e baixa estoque; `relatorio_vendas` aplica faixas de desconto (`if faturamento > 10000: desconto = faturamento * 0.1`).
Impact: A regra de pedido e de desconto só pode ser testada com banco real e muda junto com a persistência.
Recommendation: Mover a orquestração do pedido e o cálculo de desconto para controllers/services; models só leem e gravam (T-04).

### F-12 [HIGH] Handlers HTTP com validação, regra e efeitos colaterais
File: controllers.py:24-62, 64-96, 188-220, 237-255
Catalog: AP-08
Description: `controllers.py` é, na prática, a camada de rotas: cada função lê `request.get_json()`, valida, aplica regra (`categorias_validas`, faixas de status) e dispara "notificações" (`print("ENVIANDO EMAIL: ...")`, linhas 208-210, 247-250) antes de montar o `jsonify`.
Impact: As regras ficam presas ao Flask e não podem ser reutilizadas nem testadas sem um request.
Recommendation: Separar views (parsing + resposta), controllers (orquestração) e um serviço de notificação (T-04).

### F-13 [HIGH] Conexão SQLite global compartilhada entre threads
File: database.py:4-11
Catalog: AP-10
Description: `global db_connection` guarda uma única conexão criada com `sqlite3.connect(db_path, check_same_thread=False)`, reaproveitada por todas as requisições.
Impact: O servidor de desenvolvimento do Flask é multithread: requisições concorrentes compartilham cursor/transação, e o que uma requisição deixou pendente pode ser gravado pelo `commit()` de outra.
Recommendation: Conexão por requisição em `flask.g`, fechada em `teardown_appcontext` (T-05).

### F-14 [HIGH] Criação de pedido em várias etapas sem transação explícita
File: models.py:137-169
Catalog: AP-12
Description: `INSERT INTO pedidos`, os `INSERT INTO itens_pedido` e os `UPDATE produtos SET estoque` rodam em sequência com um único `db.commit()` no fim e nenhum `rollback`; a checagem de estoque (linha 144) e a baixa (linha 164) são separadas (check-then-act).
Impact: Uma exceção no meio deixa escritas pendentes na conexão global (F-13), que o próximo `commit()` de outra requisição persiste: pedido sem itens ou estoque baixado sem pedido. Duas compras simultâneas podem vender o mesmo estoque.
Recommendation: Envolver o fluxo em transação (`with conn:` / commit-rollback) e fazer a baixa condicional (`UPDATE ... SET estoque = estoque - ? WHERE id = ? AND estoque >= ?`) (T-10).

### F-15 [HIGH] `app.py` acumula config, rotas e SQL
File: app.py:6-9, 11-30, 32-45, 47-78
Catalog: AP-05
Description: O entry point configura a aplicação, registra todas as rotas, implementa handlers (`index`, `reset_database`, `executar_query`) e executa SQL direto (`cursor.execute("DELETE FROM itens_pedido")`). Rebaixado para HIGH: models e controllers já existem como arquivos separados.
Impact: O composition root não pode ser importado para testes sem trazer SQL e segredos; o fluxo admin fica fora de qualquer camada.
Recommendation: `app.py` como composition root (`create_app`); admin vai para view/controller/model próprios (T-03, T-16).

### F-16 [HIGH] Handlers acessam o driver do banco diretamente, pulando os models
File: controllers.py:3, 264-274 | app.py:4, 49-55, 66-76
Catalog: AP-11
Description: `health_check` faz `db = get_db(); cursor.execute("SELECT COUNT(*) FROM produtos")` no controller, e os handlers admin usam `get_db()` direto.
Impact: A camada de dados deixa de ser a única dona do SQL; trocar a conexão ou fazer mock exige mexer nos handlers.
Recommendation: Contagens e operações admin em funções de model; controllers só chamam models (T-05).

### F-17 [MEDIUM] Validação de entrada ausente ou inconsistente
File: controllers.py:26-50, 81-90, 113-121, 148-158, 169-171, 239-240 | app.py:61-62
Catalog: AP-17
Evidence: probe P12 (`preco: "abc"` → 500), P13 (`nome: 123` no PUT → 500), P14 (`preco_min=abc` → 500), P15 (`/login` com body `null` → 500), P16 (`/pedidos/1/status` com `null` → 500), P17 (`/admin/query` com `null` → 500), P18 (item sem `produto_id` → 500), P23 (e-mail duplicado aceito → 201)
Description: Não há checagem de tipo (`if preco < 0` com string lança `TypeError`), `float(preco_min)` sem tratar `ValueError`, `dados.get(...)` com `dados` possivelmente `None`; o PUT de produto não valida tamanho do nome nem categoria, que o POST valida (linhas 47-54); `criar_usuario` não confere formato nem unicidade do e-mail.
Impact: Entradas inválidas viram 500 com mensagem interna e dados inconsistentes entram no banco (produtos com categoria inválida via PUT, contas duplicadas).
Recommendation: Validadores por entidade compartilhados entre POST e PUT, retornando 400 com mensagem clara; 409 para e-mail já cadastrado (T-11).

### F-18 [MEDIUM] Atualização de status responde sucesso para pedido inexistente
File: controllers.py:245-252 | models.py:275-283
Catalog: AP-16
Evidence: probe P21 (`PUT /pedidos/999/status` → 200 e log `NOTIFICAÇÃO: Pedido 999 foi aprovado!`)
Description: `atualizar_status_pedido` executa o `UPDATE` e retorna `True` sem conferir `rowcount`; o handler sempre responde `{"sucesso": True, "mensagem": "Status atualizado"}`.
Impact: O cliente acredita que o pedido foi atualizado e a notificação de envio é disparada para um pedido que não existe.
Recommendation: Verificar existência/`rowcount` e responder 404 (T-09).

### F-19 [MEDIUM] Queries N+1 na listagem de pedidos e agregações separadas
File: models.py:186-199, 219-231, 239-254, 155
Catalog: AP-15
Description: Para cada pedido, uma query de itens (`cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ..."`) e, para cada item, outra para o nome do produto (`cursor3`); o relatório faz 5 `COUNT`/`SUM` separados; `criar_pedido` relê o preço já lido no primeiro laço.
Impact: Listar N pedidos com M itens custa 1 + N + N·M queries; a lentidão cresce com o histórico.
Recommendation: `JOIN` de itens com produtos numa única query agrupada em memória e um `SELECT` com `SUM(CASE ...)` para o relatório (T-08).

### F-20 [MEDIUM] Mapeamentos e validações duplicados
File: models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233 | controllers.py:28-46, 72-90
Catalog: AP-18
Description: O mapeamento row → dict de produto aparece três vezes, o de usuário duas; `get_pedidos_usuario` e `get_todos_pedidos` são idênticos exceto pelo `WHERE`; a validação de produto do POST é copiada no PUT (e já divergiu, ver F-17).
Impact: A correção de F-03 (remover `senha`) precisaria ser feita em dois lugares; os blocos já divergem.
Recommendation: Um serializador por entidade e uma função de listagem de pedidos com filtro opcional; validador único de produto (T-04, T-11).

### F-21 [MEDIUM] Logging com `print`, sem níveis, incluindo PII
File: app.py:56, 83-86 | controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Catalog: AP-20
Evidence: baseline — log com `Usuário criado: teste@x.com`, `Login bem-sucedido: admin@loja.com' --`
Description: Eventos, erros e "envio" de e-mail/SMS/push são `print("ENVIANDO EMAIL: Pedido " + ...)`; e-mails de usuários são impressos em cada login e cadastro. O banner de boot anuncia `http://localhost:5000` mesmo quando a porta é outra.
Impact: Sem níveis nem destino configurável; o stdout fica em buffer (no teste da linha de base, nada apareceu no log até ativar `PYTHONUNBUFFERED`); dados pessoais vão para o log sem controle.
Recommendation: `logging` com logger por módulo e níveis; e-mail mascarado ou ausente das mensagens (T-14).

### F-22 [MEDIUM] CORS aberto e porta/host/caminho do banco fixos
File: app.py:9, 88 | database.py:5
Catalog: AP-21
Description: `CORS(app)` libera qualquer origem numa API sem autenticação; `port=5000` e `db_path = "loja.db"` (relativo ao diretório de execução) são literais.
Impact: Qualquer site pode chamar a API a partir do navegador do usuário; a app não sobe onde a porta 5000 está ocupada (AirPlay no macOS) e cria bancos diferentes conforme a pasta de onde é executada.
Recommendation: Origens CORS, `PORT`, `HOST` e `DATABASE_PATH` lidos do ambiente, com o caminho do banco resolvido a partir da raiz do projeto (T-01, T-16).

### F-23 [MEDIUM] Um único módulo por camada misturando todos os domínios
File: models.py:4-314 | controllers.py:5-292
Catalog: AP-26
Description: `models.py` contém produtos, usuários, pedidos e relatório; `controllers.py` contém os mesmos quatro domínios mais o health check; as rotas ficam no `app.py`.
Impact: Mexer em pedidos exige navegar por arquivos que também tratam usuários e produtos; não há onde colocar código novo de um domínio sem aumentar o arquivo de todos.
Recommendation: Um módulo por domínio em cada camada (`models/produto_model.py`, `controllers/pedido_controller.py`, `views/pedido_routes.py`...) (T-18).

### F-24 [LOW] Faixas de desconto codificadas como cadeia de `if/elif`
File: models.py:256-262
Catalog: AP-25
Description: `if faturamento > 10000: ... elif faturamento > 5000: ... elif faturamento > 1000:` compara faixas de um mesmo valor.
Impact: Mudar ou acrescentar uma faixa exige editar o fluxo; a regra não é visível como dado.
Recommendation: Tabela de faixas `[(10000, 0.10), (5000, 0.05), (1000, 0.02)]` percorrida por uma função (T-17a).

### F-25 [LOW] Magic numbers e listas de valores soltas
File: controllers.py:47, 49, 52, 242, 285 | models.py:150, 247, 250, 253 | app.py:36
Catalog: AP-22
Description: Limites `len(nome) < 2` / `> 200`, a lista `categorias_validas`, a lista de status válidos e os status `'pendente'`, `'aprovado'`, `'cancelado'` como literais; a versão `"1.0.0"` repetida em dois arquivos.
Impact: As regras ficam implícitas e cada cópia pode divergir.
Recommendation: Constantes nomeadas por domínio (`CATEGORIAS_VALIDAS`, `STATUS_VALIDOS`, `NOME_MIN/MAX`, `API_VERSION`) (T-13).

### F-26 [LOW] Nomes que sombreiam builtins e cursores numerados
File: controllers.py:14, 56, 64, 98, 136, 160 | models.py:24, 54, 65, 89, 187, 191, 219, 223
Catalog: AP-23
Description: Parâmetros e variáveis `id` (sombreia o builtin) e cursores `cursor2`, `cursor3`.
Impact: Leitura mais lenta e risco de usar o builtin por engano.
Recommendation: `produto_id`, `usuario_id`, `pedido_id`; eliminar cursores extras ao resolver F-19 (T-13).

### F-27 [LOW] Imports não usados
File: database.py:2 | models.py:2
Catalog: AP-24
Description: `import os` em database.py e `import sqlite3` em models.py nunca são usados.
Impact: Ruído que sugere dependências inexistentes.
Recommendation: Remover (T-13).

## Deprecated APIs

Nenhuma API deprecated encontrada para as versões instaladas (Python 3.12.0, Flask 3.1.1, flask-cors 5.0.1, Werkzeug 3.1.8). O boot com `python -W default` não emitiu `DeprecationWarning`; o schema usa `DEFAULT CURRENT_TIMESTAMP` no SQL e não depende dos adapters de datetime do `sqlite3` deprecated no 3.12.

## Architecture Overview

- **Current:** Parcialmente em camadas: existem `models.py` (acesso a dados) e `controllers.py`, mas os "controllers" são handlers HTTP com validação e regra, os models carregam regra de negócio, `app.py` executa SQL direto e todos os domínios se misturam num arquivo por camada.
- **Target:** `app.py` como launcher fino (preserva `python app.py`) + `src/` com `app.py` (`create_app`, composition root), `config/` (settings do ambiente), `database/` (conexão por requisição + seed), `models/` (um `<entidade>_model.py` por entidade, SQL parametrizado), `services/` (notificações), `controllers/` (regras de pedido, desconto, autenticação), `views/` (blueprints por domínio + `presenters.py`) e `middlewares/` (`error_handler.py`, `auth.py`).

```
================================
Total: 27 findings
================================
```
