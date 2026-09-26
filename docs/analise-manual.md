# Análise Manual dos Projetos

Análise feita **antes** de criar a skill, lendo todo o código dos 3 projetos e subindo cada aplicação para confirmar os problemas na prática. Serve de insumo para o catálogo de anti-patterns e de gabarito para verificar se a skill encontra os mesmos problemas.

Escala de severidade (definida no enunciado):
- **CRITICAL:** segurança grave ou violação total de separação de responsabilidades.
- **HIGH:** fortes violações de MVC/SOLID.
- **MEDIUM:** padronização, duplicação e performance moderada.
- **LOW:** legibilidade, nomes e magic numbers.

---

## Projeto 1 — code-smells-project (Python/Flask)

**Stack:** Python 3 · Flask 3.1.1 · flask-cors 5.0.1 · SQLite via `sqlite3` puro (sem ORM)
**Domínio:** API de e-commerce (produtos, usuários/login, pedidos, relatório de vendas)
**Tamanho:** 4 arquivos `.py`, 780 linhas · **Tabelas:** `produtos`, `usuarios`, `pedidos`, `itens_pedido`
**Endpoints:** 19

| # | Severidade | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection por concatenação de strings em praticamente todas as queries | `models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-165, 174, 188, 192, 220, 224, 280, 291, 293` | Confirmado: login com `admin@loja.com' --` entrou como Admin sem senha. Um apóstrofo no nome do produto derruba a query (500) |
| 2 | CRITICAL | Endpoint que executa SQL arbitrário, sem autenticação | `app.py:59-78` (`cursor.execute(query)` na linha 69) | Qualquer cliente lê, altera ou apaga o banco inteiro |
| 3 | CRITICAL | Reset destrutivo do banco sem autenticação | `app.py:47-57` | Um POST anônimo apaga todos os dados |
| 4 | CRITICAL | `SECRET_KEY` e senhas do seed hardcoded | `app.py:7`; `database.py:76-78` | Segredos versionados; o admin tem senha conhecida (`admin123`) |
| 5 | CRITICAL | `/health` expõe a `secret_key`, o modo debug e o caminho do banco | `controllers.py:286-289` | Vaza segredos para qualquer cliente |
| 6 | CRITICAL | Senhas em texto puro, gravadas e **devolvidas** nas respostas | `models.py:127-128` (grava), `110` (compara), `83` e `99` (devolve) | Confirmado: `GET /usuarios/1` retorna `"senha": "admin123"` |
| 7 | CRITICAL | Debug ativo com bind público | `app.py:8, 88` | O debugger do Werkzeug permite execução remota de código |
| 8 | CRITICAL | `app.py` como God module: rotas, config, SQL direto e lógica admin juntos | `app.py:1-88` | Nenhuma separação de camadas |
| 9 | HIGH | Regras de negócio e validação dentro dos controllers | `controllers.py:28-54, 242, 247-250` | Regra presa ao HTTP, não reutilizável nem testável |
| 10 | HIGH | Criação de pedido (total, estoque, baixa) no model e sem transação | `models.py:133-169` | Lógica de serviço na camada de dados, com risco de vender acima do estoque |
| 11 | HIGH | Regra de desconto com magic numbers dentro do model de relatório | `models.py:256-262` | Regra de negócio escondida na camada de dados |
| 12 | HIGH | Estado global mutável: uma conexão única compartilhada entre threads | `database.py:4, 8, 10` (`check_same_thread=False`) | Não é thread-safe e impede injeção de dependência |
| 13 | HIGH | Acoplamento forte; o controller consulta o banco direto | `controllers.py:2-3, 266-274` | Não dá para trocar o repositório nem testar com mocks |
| 14 | HIGH | Nenhuma rota tem autenticação ou autorização; o login não emite token | `app.py:11-30`; `controllers.py:176-180` | O tipo `admin` nunca é verificado |
| 15 | MEDIUM | Queries N+1 na listagem de pedidos | `models.py:187-193, 219-225` | Uma query por pedido e mais uma por item |
| 16 | MEDIUM | Código duplicado (listagens de pedidos, mapeamento row→dict, validação de produto) | `models.py:171-233, 12-40, 79-102`; `controllers.py:28-46 × 72-90` | Um bug corrigido num lugar continua nos outros |
| 17 | MEDIUM | Validação ausente ou inconsistente | `controllers.py:43, 81-90, 119-121, 153-158, 169`; `models.py:144-146` | Quantidade negativa **aumenta** o estoque; tipos errados viram 500 |
| 18 | MEDIUM | `except Exception` genérico devolvendo `str(e)` ao cliente | `controllers.py:10-12, 21-22, 60-62…`; `app.py:77-78` | Vaza mensagens internas do SQLite; não há error handler central |
| 19 | MEDIUM | Notificações simuladas e logs com `print`, incluindo e-mails | `controllers.py:161, 179-182, 208-210, 248-250` | Sem `logging`; dados pessoais no stdout |
| 20 | MEDIUM | CORS aberto para qualquer origem | `app.py:9` | Somado à falta de autenticação, amplia a superfície de ataque |
| 21 | LOW | Imports não usados | `database.py:2`; `models.py:2` | Ruído |
| 22 | LOW | Magic numbers e strings (limites, faixas de desconto, listas de categorias/status, versão) | `controllers.py:47, 49, 52, 242, 285-286`; `models.py:257-262` | Deveriam ser constantes ou config |
| 23 | LOW | Nomes ruins: `id` sombreando o builtin, `cursor2`/`cursor3`, `buscar_produto` × `buscar_produtos` | `controllers.py:14, 56…`; `models.py:187, 191, 219, 223` | Legibilidade |
| 24 | LOW | Query descartada no health check | `controllers.py:268` | Cosmético |

**APIs deprecated:** nenhuma encontrada (Flask 3.1.1 sobe sem `DeprecationWarning`).

---

## Projeto 2 — ecommerce-api-legacy (Node.js/Express)

**Stack:** JavaScript (CommonJS) · Express 4.22 · sqlite3 5.1 (banco **em memória**, seed no boot)
**Domínio:** LMS com checkout de cursos (usuário → matrícula → pagamento), relatório financeiro admin e remoção de usuário
**Tamanho:** 3 arquivos, 180 linhas · **Tabelas:** `users`, `courses`, `enrollments`, `payments`, `audit_logs`
**Endpoints:** 3 (`POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`)

| # | Severidade | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | Senha do banco, chave live do gateway e usuário SMTP hardcoded | `src/utils.js:1-7` | Segredos de produção versionados |
| 2 | CRITICAL | Número completo do cartão e chave do gateway impressos no log | `src/AppManager.js:45` | Violação de PCI-DSS (confirmado no log do boot) |
| 3 | CRITICAL | "Hash" de senha reversível (base64 truncado) e senha padrão `123456` | `src/utils.js:17-23`; `src/AppManager.js:68, 18` | Senhas efetivamente expostas; hashes colidem |
| 4 | CRITICAL | God Class `AppManager`: conexão, schema, seed, rotas e regras juntos | `src/AppManager.js:4-139` | Viola SRP; nada é testável nem reutilizável |
| 5 | CRITICAL | Relatório financeiro e exclusão de usuário sem autenticação | `src/AppManager.js:80, 131` | Qualquer pessoa lê dados financeiros ou apaga usuários |
| 6 | HIGH | Fluxo inteiro de checkout dentro do route handler | `src/AppManager.js:28-78` | Não existe camada de controller/service/model |
| 7 | HIGH | Callback hell (5 níveis) e fluxo sem transação | `src/AppManager.js:37-77` | Se o pagamento falha, a matrícula fica órfã |
| 8 | HIGH | Um request com o cartão como número derruba o servidor | `src/AppManager.js:46` (`cc.startsWith`), `92-93` | Confirmado: `"card": 4111` mata o processo (DoS) |
| 9 | HIGH | Estado global mutável (`globalCache`) e `totalRevenue` exportado por valor, nunca atualizado | `src/utils.js:9-15, 25`; `src/AppManager.js:2` | Estado escondido e código morto enganoso |
| 10 | HIGH | Acoplamento sem injeção de dependência (banco criado no constructor) | `src/AppManager.js:1, 7`; `src/app.js:8` | Impossível mockar o banco em testes |
| 11 | HIGH | Checkout com e-mail já existente ignora a senha | `src/AppManager.js:40, 73-74` | Confirmado: com senha errada, matriculou e cobrou na conta de outra pessoa |
| 12 | HIGH | Gateway de pagamento fake embutido no handler; usuário criado antes da recusa | `src/AppManager.js:46, 69` | Regra de integração acoplada; checkout recusado deixa lixo no banco |
| 13 | MEDIUM | N+1 no relatório financeiro (query por curso, por matrícula, por usuário e pagamento) | `src/AppManager.js:83-127` | Lento; um `JOIN` com `GROUP BY` resolve |
| 14 | MEDIUM | Erros de callback ignorados; DELETE responde sucesso mesmo sem apagar nada | `src/AppManager.js:57, 92, 104, 106, 133` | Confirmado: `DELETE /api/users/999` → 200 |
| 15 | MEDIUM | DELETE sem cascata deixa matrículas e pagamentos órfãos | `src/AppManager.js:133-135` | O relatório passa a mostrar `"student": "Unknown"` |
| 16 | MEDIUM | Validação de entrada fraca (sem tipo, formato de e-mail, UNIQUE) | `src/AppManager.js:35, 132` | Dados inválidos e duplicados no banco |
| 17 | MEDIUM | Respostas inconsistentes (texto puro × JSON) e sem error handler central | `src/AppManager.js:35, 38, 41, 48, 51, 55, 60, 70, 87` | Contrato da API imprevisível |
| 18 | MEDIUM | Schema e seed misturados ao runtime; `initDb` não é aguardado antes do `listen` | `src/AppManager.js:10-23`; `src/app.js:9` | Funciona por acaso (fila do sqlite3) |
| 19 | LOW | Nomes ruins: `u, e, p, cid, cc`, `badCrypto`, `AppManager`, `utils` | `src/AppManager.js:29-33`; `src/utils.js:17` | Legibilidade |
| 20 | LOW | Magic numbers e strings: porta 3000, `10000`, `"4"`, `'PAID'`/`'DENIED'` | `src/utils.js:6, 19, 22`; `src/AppManager.js:46, 68, 108` | Deveriam ser constantes |
| 21 | LOW | `let` onde deveria ser `const` | `src/AppManager.js:29-33, 43, 46…`; `src/utils.js:9-10` | Legibilidade |
| 22 | LOW | Padrão `self = this` com `function()` | `src/AppManager.js:26, 50-54` | Estilo pré-arrow functions |

**APIs deprecated / legadas:**
- API de callbacks do `sqlite3` (`src/AppManager.js:37, 40, 50, 54, 57, 69, 83…`). O equivalente moderno é `node:sqlite` (nativo desde o Node 22.5), `better-sqlite3` ou um wrapper com promises e `async/await`. O `npm audit` ainda aponta 12 vulnerabilidades transitivas do `sqlite3`.
- `self = this` com `function()` para ler `this.lastID`: substituir por `async/await`.

---

## Projeto 3 — task-manager-api (Python/Flask, parcialmente organizado)

**Stack:** Python 3 · Flask 3.0.0 · Flask-SQLAlchemy 3.1.1 (SQLAlchemy 2.1) · Flask-CORS 4.0 · SQLite
**Domínio:** gerenciador de tarefas (tasks, users, categories, relatórios, login)
**Tamanho:** 16 arquivos `.py`, 1158 linhas, já divididos em `models/`, `routes/`, `services/` e `utils/` · **Tabelas:** `users`, `categories`, `tasks`
**Endpoints:** 22

| # | Severidade | Problema | Local | Por que importa |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais SMTP hardcoded | `services/notification_service.py:7-10` | Segredo versionado |
| 2 | CRITICAL | `SECRET_KEY` e URI do banco fixas no código (o python-dotenv está instalado e não é usado) | `app.py:11-13` | Permite forjar sessões; não há config por ambiente |
| 3 | CRITICAL | Hash de senha MD5 sem salt | `models/user.py:27-32` | Quebrável por rainbow table |
| 4 | CRITICAL | Hash da senha devolvido pela API | `models/user.py:21`; rotas `user_routes.py:33, 85, 129, 209` | Confirmado: `POST /login` devolve o hash MD5 |
| 5 | CRITICAL | Token fake e nenhuma autorização | `routes/user_routes.py:210` | Qualquer pessoa cria um usuário `admin` e apaga qualquer recurso |
| 6 | HIGH | Rotas "gordas": validação, regra, query e serialização juntas (não há controllers) | `routes/task_routes.py:85-154, 156-223`; `routes/report_routes.py:12-101` | Viola MVC/SRP mesmo com pastas separadas |
| 7 | HIGH | `NotificationService` nunca é usado, instancia SMTP direto e guarda estado em memória | `services/notification_service.py:4-48` | A camada de serviço existe só no nome |
| 8 | HIGH | CRUD de categorias dentro do blueprint de relatórios | `routes/report_routes.py:157-223` | Baixa coesão |
| 9 | HIGH | Regra de "overdue" copiada 6 vezes; o método do model nunca é usado | `task_routes.py:30-39, 71-80, 283-287`; `user_routes.py:171-180`; `report_routes.py:34-37, 132-135`; `models/task.py:50-60` | Mudar a regra exige editar 6 lugares |
| 10 | HIGH | `except:` pelado e nenhum error handler central | `task_routes.py:62, 137, 204, 236`; `user_routes.py:130, 149`; `report_routes.py:186, 207, 221`; `utils/helpers.py:46, 49, 88` | Confirmado: `priority` como string gera 500 com traceback |
| 11 | MEDIUM | N+1 e dezenas de COUNTs separados | `task_routes.py:42, 51, 275-281`; `user_routes.py:22`; `report_routes.py:15-28, 55-56, 163` | Degrada com o volume |
| 12 | MEDIUM | Validação duplicada; `helpers.py` e suas constantes nunca são usados | `utils/helpers.py:57-116`; `task_routes.py:110, 177`; `user_routes.py:61, 71, 106, 120` | Várias fontes de verdade para a mesma regra |
| 13 | MEDIUM | Validação ausente ou fraca (cor, body nulo, nome vazio, senha de 4 caracteres) | `report_routes.py:180, 196-197`; `user_routes.py:64, 102-103, 124-125` | Dados inválidos no banco |
| 14 | MEDIUM | Serialização refeita à mão fora do model | `task_routes.py:17-28`; `user_routes.py:15-23, 162-169` | Formatos de resposta divergentes |
| 15 | MEDIUM | Cascata manual em loop e CORS aberto | `user_routes.py:140-142`; `app.py:15` | Deveria ser `cascade` no relacionamento |
| 16 | MEDIUM | `print` como log, debug em produção e `create_all()` no import | `app.py:30-31, 34`; vários `print` nas rotas | Sem logging; risco do debugger exposto |
| 17 | MEDIUM | **[DEPRECATED]** `Query.get()` (16 usos; emite `LegacyAPIWarning` no boot) | `task_routes.py:42, 51, 67, 117…`; `user_routes.py:29, 94, 136, 155`; `report_routes.py:105, 192, 213` | Substituir por `db.session.get(Model, id)` |
| 18 | MEDIUM | **[DEPRECATED]** `datetime.utcnow()` (22 usos; `DeprecationWarning` no Python 3.12) | `models/task.py:15, 16, 52`; `models/user.py:14`; `models/category.py:11`; rotas e seed | Substituir por `datetime.now(timezone.utc)` |
| 19 | LOW | Imports e funções utilitárias não usados | `app.py:7`; `task_routes.py:7`; `user_routes.py:5-6`; `report_routes.py:7-8`; `helpers.py:2-7` | Ruído |
| 20 | LOW | Magic numbers, nomes curtos (`t`, `u`, `p1..p5`) e `type(x) == list` | `task_routes.py:104, 113, 141, 210`; `report_routes.py:45, 84-88, 129` | Legibilidade |

---

## Observações que viram regras da skill

- **Porta 5000 no macOS:** a porta 5000 é ocupada pelo AirPlay Receiver, então os projetos Flask não sobem nela. A skill precisa tornar a porta configurável (`PORT`) e validar numa porta livre.
- **Contrato da API:** a refatoração precisa manter paths, métodos, nomes de campos e status codes. Mudanças de contrato só por segurança (tirar senhas e segredos das respostas) e sempre documentadas.
- **Linha de base antes de mexer:** registrar as respostas dos endpoints **antes** da refatoração, para comparar depois.
- **Projeto parcialmente organizado:** ter pastas `models/` e `routes/` não significa ter MVC. A skill precisa julgar responsabilidades, e não só a estrutura de pastas.
