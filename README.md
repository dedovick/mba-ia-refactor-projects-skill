# Refatoração Arquitetural Automatizada — Skill `refactor-arch`

Projeto do MBA em Engenharia de Software com IA (Full Cycle). Uma **skill do Claude Code** que analisa, audita e refatora qualquer projeto backend para o padrão **MVC**, validando que a aplicação continua funcionando. A mesma skill, copiada sem alterações, foi executada em três projetos legados de stacks e níveis de organização diferentes.

> O enunciado original do desafio está em [`docs/DESAFIO.md`](docs/DESAFIO.md).

| Projeto | Stack | Findings (C/H/M/L) | Requisições da linha de base | Sondas de segurança | Aplicação após refatorar |
|---|---|---|---|---|---|
| `code-smells-project` | Python + Flask 3.1 | **27** (8/8/7/4) | 32/32 ✓ | 23 vulneráveis → **27/27 OK** | ✅ `python app.py` |
| `ecommerce-api-legacy` | Node.js + Express 4.22 | **22** (7/5/6/4) | 6/6 ✓ | 11 vulneráveis → **13/13 OK** | ✅ `npm start` |
| `task-manager-api` | Python + Flask 3.0 + SQLAlchemy | **19** (5/3/7/4) | 43/43 ✓ | 15 vulneráveis → **19/19 OK** | ✅ `python seed.py && python app.py` |

Resultado final com a versão **`skill-v3`** da skill. Relatórios em [`reports/`](reports/).

## Para o avaliador

- 🔍 Problemas encontrados à mão → [Análise Manual](#análise-manual)
- 🛠️ Como a skill foi construída e por quê → [Construção da Skill](#construção-da-skill)
- 📊 Relatórios, antes/depois, checklists e logs → [Resultados](#resultados)
- ▶️ Como rodar a skill e validar → [Como Executar](#como-executar)

Material complementar:
- [`docs/analise-manual.md`](docs/analise-manual.md): os 66 problemas da análise manual, com arquivo e linha;
- [`PLANO.md`](PLANO.md): plano, checklist de requisitos e log de todas as execuções;
- [`docs/iteracoes/`](docs/iteracoes/): relatórios das versões anteriores da skill.

---

## Análise Manual

Antes de escrever a skill, li todo o código dos três projetos e subi cada aplicação para **confirmar os problemas em execução**, e não só pela leitura. A análise completa, com 24 + 22 + 20 problemas e todos os arquivos e linhas, está em [`docs/analise-manual.md`](docs/analise-manual.md). Abaixo estão os mais relevantes de cada projeto.

### Projeto 1 — code-smells-project (Python/Flask, e-commerce)

Quatro arquivos que fazem tudo: rotas, SQL, regras e configuração misturados.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | SQL Injection por concatenação de strings em quase todas as queries | `models.py:28, 48-49, 110, …` | Confirmado: o login com `admin@loja.com' --` entra como admin **sem senha** |
| CRITICAL | Endpoint que executa SQL arbitrário e outro que apaga o banco, ambos sem autenticação | `app.py:47-78` | Qualquer cliente lê, altera ou destrói o banco com um POST |
| CRITICAL | Senhas em texto puro, **devolvidas** nas respostas | `models.py:83, 99, 110, 127` | `GET /usuarios/1` retornava `"senha": "admin123"` |
| CRITICAL | `SECRET_KEY` hardcoded e exposta no `/health`; debug ativo com bind `0.0.0.0` | `app.py:7-8, 88`; `controllers.py:286-289` | Vaza o segredo de sessão; o debugger do Werkzeug permite execução remota |
| HIGH | Regra de negócio na camada de dados (estoque, total, desconto), sem transação | `models.py:133-169, 256-262` | Pedidos inconsistentes e venda acima do estoque |
| HIGH | Conexão SQLite global compartilhada entre threads | `database.py:4-10` | Condições de corrida; impossível injetar/mocar |
| MEDIUM | Queries N+1 na listagem de pedidos | `models.py:187-193, 219-225` | 1 + P + P·I queries por listagem |
| MEDIUM | Validação ausente: quantidade negativa **aumenta** o estoque | `models.py:144-146`; `controllers.py:43, 81-90` | Manipulação de estoque e faturamento |
| LOW | Magic numbers (faixas de desconto, limites, listas de status) | `models.py:257-262`; `controllers.py:47-52` | Regras implícitas e espalhadas |
| LOW | Nomes ruins (`id` sombreando o builtin, `cursor2`, `cursor3`) | `models.py:187-223` | Legibilidade |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS com checkout)

Três arquivos, com quase tudo dentro de uma única classe.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | Senha do banco e chave **live** do gateway hardcoded | `src/utils.js:1-7` | Segredos de produção no repositório |
| CRITICAL | Número completo do cartão e chave do gateway impressos no log | `src/AppManager.js:45` | Violação de PCI-DSS (confirmado no log) |
| CRITICAL | God Class `AppManager`: conexão, schema, seed, rotas e regras | `src/AppManager.js:4-139` | Nada é testável isoladamente |
| CRITICAL | "Hash" de senha reversível (base64 truncado) e senha padrão `123456` | `src/utils.js:17-23`; `AppManager.js:68` | Senhas efetivamente expostas |
| HIGH | Um request com o cartão como número **derruba o servidor** | `src/AppManager.js:46` | DoS com um único request (confirmado) |
| HIGH | Checkout com e-mail existente **ignora a senha** | `src/AppManager.js:40, 73-74` | Compra cobrada na conta de outra pessoa (confirmado) |
| HIGH | Callback hell sem transação; usuário gravado antes do pagamento recusado | `src/AppManager.js:37-77` | Banco inconsistente |
| MEDIUM | N+1 no relatório financeiro | `src/AppManager.js:83-127` | Queries crescem com as matrículas |
| MEDIUM | DELETE responde sucesso mesmo sem apagar nada e deixa órfãos | `src/AppManager.js:133-135` | Status que mente; relatório mostra `"Unknown"` |
| LOW | Nomes ruins (`u`, `e`, `cc`, `badCrypto`) e magic strings (`"4"` = aprovado) | `src/AppManager.js:29-33, 46` | Legibilidade e regras implícitas |

### Projeto 3 — task-manager-api (Python/Flask, parcialmente em camadas)

Parece organizado, com `models/`, `routes/`, `services/` e `utils/`. É o teste de que **ter as pastas certas não é ter a arquitetura certa**.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | Senha com MD5 sem salt, e o hash **devolvido** no login | `models/user.py:21, 27-32` | Quebrável por rainbow table e exposto na API |
| CRITICAL | Token fake (`"fake-jwt-token-" + id`) e nenhuma autorização | `routes/user_routes.py:210` | Qualquer pessoa cria admins e apaga dados |
| CRITICAL | `SECRET_KEY` e credenciais SMTP hardcoded | `app.py:11-13`; `services/notification_service.py:7-10` | Segredos no repositório |
| HIGH | Rotas "gordas": não existe camada de controllers | `routes/task_routes.py:85-223`; `routes/report_routes.py:12-101` | MVC só no nome |
| HIGH | Camada morta: `NotificationService`, `helpers.py` e validadores do model nunca usados | `services/…:4-48`; `utils/helpers.py:57-116` | Duas fontes de verdade para as mesmas regras |
| HIGH | Regra de "tarefa atrasada" copiada em **6 lugares**; o método do model nunca é usado | `task_routes.py:30-39, 71-80, …`; `models/task.py:50-60` | Mudar a regra exige editar 6 arquivos |
| MEDIUM | **[DEPRECATED]** `Query.get()` (16×) e `datetime.utcnow()` (22×) | rotas, models e seed | Emitem warnings no boot; `db.session.get` e `datetime.now(timezone.utc)` |
| MEDIUM | CRUD de categorias dentro do blueprint de **relatórios** | `routes/report_routes.py:157-223` | Baixa coesão |
| LOW | Imports não usados | `app.py:7`; `task_routes.py:7`; `helpers.py:2-7` | Ruído |
| LOW | `if` aninhado retornando True/False; nomes `p1..p5` | `models/task.py:38-60`; `report_routes.py:84-88` | Legibilidade |

### O que os três têm em comum

| Problema | P1 | P2 | P3 |
|---|:-:|:-:|:-:|
| Segredos no código | ✓ | ✓ | ✓ |
| Senha mal protegida ou exposta | ✓ | ✓ | ✓ |
| Nenhuma autenticação/autorização real | ✓ | ✓ | ✓ |
| Regra de negócio fora do lugar | ✓ | ✓ | ✓ |
| N+1 | ✓ | ✓ | ✓ |
| Erros genéricos ou ignorados | ✓ | ✓ | ✓ |
| Nomes ruins e magic numbers | ✓ | ✓ | ✓ |

Essa interseção virou a espinha do catálogo de anti-patterns: são problemas que aparecem **independentemente da stack**, e é por isso que a skill consegue ser agnóstica.

---

## Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                         # o "prompt": 3 fases, regras invioláveis com exemplos ✅/❌
└── references/
    ├── project-analysis.md          # Análise de projeto: linguagem, framework, banco, arquitetura, endpoints
    ├── anti-patterns-catalog.md     # Catálogo: 26 anti-patterns + APIs deprecated + falsos positivos
    ├── report-template.md           # Template do relatório da Fase 2
    ├── mvc-guidelines.md            # Guidelines: camadas, responsabilidades, estrutura alvo por stack
    ├── refactoring-playbook.md      # Playbook: 18 transformações com código antes/depois
    └── validation.md                # (extra) linha de base, sondas de segurança e validação pós-refatoração
```

| Área obrigatória | Arquivo | Destaques |
|---|---|---|
| Análise de projeto | `project-analysis.md` | Heurísticas por manifesto e por uso real no código; descoberta de endpoints para 6 frameworks; classificação "monolítica / parcialmente em camadas / em camadas" pela **responsabilidade** dos arquivos, não pelos nomes das pastas |
| Catálogo de anti-patterns | `anti-patterns-catalog.md` | 26 itens (7 CRITICAL, 7 HIGH, 8 MEDIUM, 4 LOW), cada um com sinais de detecção, regra de ajuste de severidade e transformação correspondente; tabela de APIs deprecated para Python, SQLAlchemy, Flask, Node e Express |
| Template de relatório | `report-template.md` | Formato fixo, com `File:` conferido, `Catalog:`, `Evidence:` (a sonda que prova o problema) e exemplos de finding bem e mal escrito |
| Guidelines de arquitetura | `mvc-guidelines.md` | O que cada camada **pode** e **não pode** fazer, regra de dependência, estrutura alvo para Flask e Express, tabela "onde cada coisa vai" e roteiro para projetos que já têm camadas |
| Playbook de refatoração | `refactoring-playbook.md` | 18 transformações com código antes/depois em Python e JavaScript |

### Decisões de design

**1. O `SKILL.md` é o processo; as referências são o conhecimento.** O `SKILL.md` define as 3 fases, os gates e as regras, e diz **quando** ler cada referência: análise e validação na Fase 1, catálogo e template na Fase 2, guidelines e playbook na Fase 3. Assim o modelo carrega o conhecimento no momento em que ele é útil.

**2. Seis regras invioláveis, cada uma com exemplos ✅/❌:**
1. nada muda antes do "sim";
2. todo finding tem arquivo e linha **conferidos**;
3. o contrato da API é sagrado, com exceção só para segurança e para status que mentem;
4. o comando de execução é preservado;
5. nunca afirmar que algo funciona sem ter executado;
6. detectar a stack por evidência, nunca pelo nome.

**3. Linha de base antes de mexer.** Na Fase 1, a skill sobe a aplicação **numa cópia temporária** (o repositório nunca é tocado antes da confirmação) e registra status e formato de resposta de cada endpoint. Na Fase 3, a mesma sequência roda de novo e é comparada linha a linha. É assim que ela prova que "os endpoints continuam respondendo", sem depender de ninguém dizer que funcionou.

**4. Sondas de segurança e robustez (v3).** Além das requisições normais, a skill monta **sondas** a partir do que leu no código:
- identidade: agir em nome de outra conta;
- injeção;
- autorização;
- tipos trocados;
- recursos inexistentes;
- consistência depois de falha;
- exposição de dados.

Cada sonda vulnerável precisa ter um finding na Fase 2 e precisa estar bloqueada no fim da Fase 3. Uma sonda que continua vulnerável **bloqueia a conclusão**.

**5. A transformação se adapta ao ponto de partida.** Num monolito, a skill cria as camadas do zero. Num projeto parcialmente organizado, ela preserva o que está certo, cria a camada que falta (controllers), consolida duplicações e resolve o código morto.

### Anti-patterns do catálogo e por quê

| Severidade | Anti-patterns | Por que entraram |
|---|---|---|
| CRITICAL | AP-01 segredos hardcoded · AP-02 SQL Injection · AP-03 dados sensíveis expostos · AP-04 senha insegura · AP-05 God Class · AP-06 endpoint perigoso sem auth / identidade não verificada · AP-07 debug em produção | Presentes nos 3 projetos, cada um com um "sabor" diferente (concatenação em Python × template literal em JS, MD5 × base64 × texto puro) |
| HIGH | AP-08 fat controller · AP-09 regra no model · AP-10 estado global · AP-11 acoplamento sem DI · AP-12 sem transação · AP-13 callback hell · AP-14 camada morta | O núcleo das violações de MVC/SOLID. O AP-14 existe por causa do P3: a camada existe e é ignorada |
| MEDIUM | AP-15 N+1 · AP-16 erro genérico · AP-17 validação ausente · AP-18 duplicação · AP-19 **APIs deprecated** · AP-20 print/console · AP-21 CORS e config HTTP · AP-26 baixa coesão | Padronização e performance. O AP-19 traz a tabela de deprecated com o equivalente moderno |
| LOW | AP-22 magic numbers · AP-23 nomes ruins · AP-24 código não usado · AP-25 condicionais em cadeia | Legibilidade. O AP-25 **distingue** faixas → tabela de dados, valor → ação → despacho/`match`, `if` aninhado → expressão, e guard clauses (que **não** são problema) |

O catálogo também tem uma tabela de **falsos positivos** (✅ é finding × ❌ não é finding) para cada item. Por exemplo: `db = SQLAlchemy()` não é estado global; `print` num script de seed não é finding; o entry point que registra todas as camadas não é God Class.

### Como garanti que a skill é agnóstica

1. **Detecção por evidência:** a stack sai do manifesto **e** do uso no código (`require('express')` + `app.get(...)`), nunca do nome da pasta.
2. **Heurísticas para várias stacks**, e não só as três do desafio: Flask, FastAPI, Django, Express, NestJS, Spring e Go na descoberta de endpoints; tabela de deprecated para 5 ecossistemas.
3. **Estrutura alvo por stack** nas guidelines (Flask e Express, com orientação para outras), preservando o comando de execução de cada uma.
4. **Exemplos 100% fictícios.** Todos os exemplos das referências usam domínios neutros: faturas, chamados, labels, assinaturas. Fiz uma varredura para remover qualquer nome, rota ou mensagem dos projetos reais. Assim, acertar os problemas dos 3 projetos mostra que a skill entendeu o **padrão**, e não que copiou um exemplo.
5. **A prova:** a mesma pasta, copiada byte a byte (conferido com `diff -r`), rodou em Flask monolítico, Express e Flask em camadas.

### Desafios encontrados e como resolvi

| Desafio | Como resolvi |
|---|---|
| **Porta 5000 ocupada no macOS** (AirPlay Receiver): os projetos Flask não subiam | A validação sempre escolhe uma porta livre; na linha de base, o literal da porta é trocado **só na cópia temporária**; na refatoração, a porta passa a vir de `PORT` |
| Como provar que "os endpoints continuam funcionando"? | Linha de base na Fase 1 + mesma sequência na Fase 3, com comparação por status e formato |
| **A v2 não detectou o checkout em nome de outra conta** (P2), então a Fase 3 também não corrigiu | v3: sondas de segurança executadas antes e depois, com a Fase 2 obrigada a cobrir toda sonda vulnerável com um finding; mais um sinal genérico no AP-06 ("identidade não verificada no fluxo"). Resultado: detectado como CRITICAL e corrigido (→ 401). O mesmo sinal encontrou um caso análogo no P1 que ninguém tinha visto (pedido em nome de qualquer `usuario_id`) |
| Sequências de `if` e organização de módulos não tinham item próprio | v2: AP-25 (com a tabela de quando **não** é problema) e AP-26, mais as transformações T-17 e T-18 |
| Exemplos das referências parecidos demais com os projetos | Troca por domínios fictícios e varredura por termos dos projetos antes de cada versão |
| Relatório propunha `routes/` e o código criava `views/` | v3: o template exige os nomes de pastas das guidelines |
| Ordem não determinística no relatório financeiro (P2) geraria "regressão" falsa | v3: listas comparadas por conteúdo, não por posição; ordem que ficou estável conta como correção |
| Contrato × correção de bug: DELETE inexistente respondendo 200 | v3: "status que mentem" viram exceção permitida ao contrato, sempre documentada |

### Evolução da skill

Cada versão é um commit com tag (`git diff skill-v1 skill-v3`):

| Versão | Mudanças | Motivada por |
|---|---|---|
| [`skill-v1`](https://github.com/dedovick/mba-ia-refactor-projects-skill/tree/skill-v1) | 3 fases, 24 anti-patterns, 16 transformações, linha de base | análise manual |
| [`skill-v2`](https://github.com/dedovick/mba-ia-refactor-projects-skill/tree/skill-v2) | +AP-25 condicionais, +AP-26 coesão, +T-17/T-18, falsos positivos, exemplos ✅/❌ nas regras, exemplos fictícios | revisão da 1ª execução no P1 |
| [`skill-v3`](https://github.com/dedovick/mba-ia-refactor-projects-skill/tree/skill-v3) | sondas de segurança antes/depois, `Evidence:` nos findings, identidade no AP-06, comparação sem ordem, status que mentem, nomes consistentes | o finding que faltou no P2 |

| Execução | Versão | Findings | Observação |
|---|---|---|---|
| P1 | v1 | 20 | interrompida na Fase 3 para incluir melhorias ([`docs/iteracoes/p1-skill-v1-interrompida`](docs/iteracoes/p1-skill-v1-interrompida)) |
| P1 | v2 | 23 | AP-25 e AP-26 passam a aparecer |
| P2 | v2 | 20 | **não** detectou o checkout em nome de outra conta |
| P1 | **v3** | **27** | sem regressão; +pedido em nome de outro usuário, +status que mente |
| P2 | **v3** | **22** | detecta **e corrige** o checkout em nome de outra conta |
| P3 | **v3** | **19** | detecta camada morta, duplicação, coesão e deprecated num projeto já em camadas |

---

## Resultados

### Resumo das auditorias (skill-v3)

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | APIs deprecated | Relatório |
|---|:-:|:-:|:-:|:-:|:-:|---|---|
| code-smells-project | 8 | 8 | 7 | 4 | **27** | nenhuma (verificado com `python -W default`) | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | 7 | 5 | 6 | 4 | **22** | driver `sqlite3` de callbacks, `self = this` → `node:sqlite` + async/await | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | 5 | 3 | 7 | 4 | **19** | `Query.get()`, `datetime.utcnow()`, `backref` | [audit-project-3.md](reports/audit-project-3.md) |

Cada projeto também tem, na própria pasta `reports/`, a linha de base (`baseline-endpoints.md`) e o resultado da validação (`validation-results.md`).

### Antes × depois

**code-smells-project** (780 → 1032 linhas)
```
ANTES                         DEPOIS
app.py                        app.py                 # launcher: python app.py
controllers.py                .env.example
models.py                     src/
database.py                   ├── app.py             # create_app() — composition root
requirements.txt              ├── config/            # settings.py, constants.py
                              ├── database/          # conexão por requisição, seed
                              ├── models/            # produto, usuario, pedido, admin
                              ├── services/          # notificações
                              ├── controllers/       # produto, usuario, pedido, relatorio, sistema + validators
                              ├── views/             # blueprints por domínio + presenters
                              └── middlewares/       # error_handler, auth (X-Admin-Token)
```

**ecommerce-api-legacy** (180 → 479 linhas)
```
ANTES                         DEPOIS
src/app.js                    src/
src/AppManager.js             ├── server.js          # listen — npm start
src/utils.js                  ├── app.js             # createApp() — composition root
package.json                  ├── config/            # index.js (env), logger.js
                              ├── database/          # node:sqlite, schema + seed
                              ├── models/            # user, course, enrollment, payment, auditLog
                              ├── services/          # checkout, report, user, paymentGateway, passwordHasher
                              ├── controllers/       # checkout, report, user + validators
                              ├── views/             # routes.js + presenters.js
                              └── middlewares/       # errorHandler, requireAdmin
```

**task-manager-api** (1158 → 1321 linhas)
```
ANTES                         DEPOIS
app.py                        app.py, seed.py        # mesmos comandos
database.py                   .env.example
models/  (task, user,         src/
          category)           ├── app.py             # create_app()
routes/  (task, user,         ├── config/            # settings.py (env)
          report)             ├── database/          # extensão ORM + seed
services/notification_…       ├── models/            # task, user, category + constants, clock
utils/helpers.py              ├── services/          # token_service (token assinado)
seed.py                       ├── controllers/       # task, user, category, report + validators  ← camada que faltava
                              ├── views/             # task, user, category, report, system + presenters
                              └── middlewares/       # error_handler, auth (Bearer)
```

### Checklist de validação

| Item | P1 | P2 | P3 |
|---|:-:|:-:|:-:|
| **Fase 1 — Análise** | | | |
| Linguagem detectada corretamente | ✅ Python 3.12 | ✅ JavaScript (CommonJS) | ✅ Python 3.12 |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.22.1 | ✅ Flask 3.0 + SQLAlchemy |
| Domínio descrito corretamente | ✅ e-commerce | ✅ LMS com checkout | ✅ Task Manager |
| Número de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 14 (16 `.py` menos os `__init__.py` vazios) |
| **Fase 2 — Auditoria** | | | |
| Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 27 | ✅ 22 | ✅ 19 |
| Detecção de APIs deprecated | ✅ nenhuma (justificado) | ✅ | ✅ |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3 — Refatoração** | | | |
| Estrutura de diretórios segue MVC | ✅ | ✅ | ✅ |
| Configuração extraída (sem hardcoded) + `.env.example` | ✅ | ✅ | ✅ |
| Models abstraem os dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ `create_app()` | ✅ `server.js` + `createApp()` | ✅ `create_app()` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ (os warnings de deprecated sumiram) |
| Endpoints originais respondem corretamente | ✅ 32/32 | ✅ 6/6 | ✅ 43/43 |

### Aplicações rodando após a refatoração

Os três projetos foram validados **duas vezes**: pela própria skill (Fase 3) e por mim, de forma independente, numa cópia limpa com dependências reinstaladas e repetindo os ataques da análise manual.

**Logs de boot** (dos `validation-results.md`):
```
# code-smells-project — python -W default app.py
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:61885

# ecommerce-api-legacy — npm start (node --trace-deprecation: nenhum warning)
[info] Frankenstein LMS rodando na porta 62987...
[info] Processando pagamento de 497 com cartão **** 4444

# task-manager-api — python -W default app.py (sem LegacyAPIWarning / DeprecationWarning)
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:62406
```

**Ataques repetidos depois da refatoração (validação independente):**

| Ataque | Antes | Depois |
|---|---|---|
| P1: login com `admin@loja.com' --` | 200, admin sem senha | **401** |
| P1: `GET /usuarios/1` | devolvia `senha` | sem o campo |
| P1: `POST /admin/query` sem token | executava qualquer SQL | **401**; com token, só `SELECT` |
| P1: pedido com quantidade `-5` | aumentava o estoque | **400** |
| P2: checkout com o e-mail de outra pessoa e senha errada | 200, cobrado na conta dela | **401** |
| P2: `"card": 4111` (número) | derrubava o servidor | **400** |
| P2: cartão e chave no log | completos | `**** 4444`, sem a chave |
| P2: checkout recusado | gravava o usuário | não grava nada |
| P3: `POST /login` | devolvia o hash MD5 | token assinado, sem hash |
| P3: criar admin / apagar usuário sem credencial | 201 / 200 | **401** |
| P3: `"priority": "abc"` | 500 com traceback | **400** |

Mudanças intencionais de contrato, todas por segurança ou por status que mentiam, estão listadas em cada `validation-results.md`.

### Como a skill se comportou em cada stack

- **Flask monolítico (P1):** a transformação mais profunda. Quatro arquivos viraram 7 camadas. A skill manteve as chaves em português do contrato (`dados`, `sucesso`, `erro`) e o `python app.py`, e corrigiu os problemas de segurança **sem** mudar formatos, exceto os campos sensíveis removidos.
- **Express (P2):** além da separação em camadas, aplicou a recomendação de deprecated que ela mesma fez: trocou o driver `sqlite3` de callbacks pelo `node:sqlite` nativo, eliminou o callback hell e adicionou transações. Manteve **exatamente** as mensagens em texto (`Bad Request`, `Pagamento recusado`) do contrato original.
- **Flask em camadas (P3):** o teste mais sutil. A skill não se deixou enganar pelas pastas existentes: criou a camada de controllers que faltava, ativou ou removeu o código morto, unificou a regra de atraso num único lugar, tirou as categorias do módulo de relatórios e migrou as APIs deprecated. Os warnings do boot sumiram.
- **Em comum:** o comando de execução foi preservado nos três; nenhum finding sem linha conferida; nenhuma sonda vulnerável sem finding.

---

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`)
- Python 3.10+ (para os projetos 1 e 3) e Node.js 22.13+ (para o projeto 2, que passa a usar `node:sqlite`)
- `curl` e `rsync`, usados pela validação da skill (já vêm no macOS e na maioria das distribuições Linux)

### Rodar a skill

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto. Rode o Claude Code **a partir da pasta do projeto**:

```bash
git clone https://github.com/dedovick/mba-ia-refactor-projects-skill.git
cd mba-ia-refactor-projects-skill

# Projeto 1 — Python/Flask
cd code-smells-project && claude "/refactor-arch"

# Projeto 2 — Node.js/Express
cd ../ecommerce-api-legacy && claude "/refactor-arch"

# Projeto 3 — Python/Flask em camadas
cd ../task-manager-api && claude "/refactor-arch"
```

> Este repositório já contém o resultado da refatoração. Para rodar a skill sobre o **código legado original**, use o commit `eb7dc8b`, que tem os 3 projetos no estado original com a skill v3 em `.claude/`:
>
> ```bash
> git worktree add ../refactor-original eb7dc8b
> cd ../refactor-original/code-smells-project && claude "/refactor-arch"
> ```

O que acontece em cada execução:
1. **Fase 1:** imprime o resumo do projeto e grava `reports/baseline-endpoints.md`, com as requisições e as sondas.
2. **Fase 2:** imprime e salva `reports/audit-report.md` e **pergunta** `Proceed with refactoring (Phase 3)? [y/n]`. Nada é alterado antes da resposta.
3. **Fase 3:** refatora, valida e salva `reports/validation-results.md`.

Para reutilizar a skill em outro projeto, copie a pasta: `cp -R code-smells-project/.claude <outro-projeto>/`.

### Validar que a refatoração funcionou

1. Leia `reports/validation-results.md` do projeto: log de boot, tabela antes × depois e tabela de sondas.
2. Suba a aplicação você mesmo, com o **mesmo comando de antes**, numa porta livre:

```bash
# Projeto 1
cd code-smells-project
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
PORT=5055 ADMIN_TOKEN=troque-me python app.py
curl -s localhost:5055/produtos/1
curl -s -X POST localhost:5055/login -H 'Content-Type: application/json' -d "{\"email\":\"admin@loja.com' --\",\"senha\":\"x\"}"   # → 401

# Projeto 2
cd ecommerce-api-legacy
npm install
PORT=3055 ADMIN_TOKEN=troque-me npm start
# use os exemplos de api.http; rotas admin exigem o header X-Admin-Token

# Projeto 3
cd task-manager-api
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
SECRET_KEY=troque-me python seed.py
SECRET_KEY=troque-me PORT=5056 python app.py
curl -s localhost:5056/tasks
```

As variáveis de ambiente de cada projeto estão documentadas no respectivo `.env.example`. No macOS, evite a porta 5000, que é usada pelo AirPlay Receiver.
