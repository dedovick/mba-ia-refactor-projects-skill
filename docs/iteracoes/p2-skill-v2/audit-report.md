# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js, CommonJS) + Express 4.22.1 (^4.18.2)
Files:   3 analyzed | ~180 lines of code
Date:    2026-09-26
================================
```

## Summary

CRITICAL: 6 | HIGH: 4 | MEDIUM: 7 | LOW: 3

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 6 | F-01, F-02, F-03, F-04, F-05, F-06 |
| HIGH | 4 | F-07, F-08, F-09, F-10 |
| MEDIUM | 7 | F-11, F-12, F-13, F-14, F-15, F-16, F-17 |
| LOW | 3 | F-18, F-19, F-20 |

## Findings

### F-01 [CRITICAL] Credenciais e chave de pagamento hardcoded
File: src/utils.js:1-7
Catalog: AP-01
Description: O objeto `config` guarda segredos literais: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `dbUser: "admin_master"`, `smtpUser: "no-reply@fullcycle.com.br"`. Nenhuma variável de ambiente é lida em todo o projeto.
Impact: Os segredos de produção vazam com o repositório e não podem ser trocados por ambiente sem editar código.
Recommendation: Módulo `config` lendo `process.env`, `.env.example` sem valores reais (T-01).

### F-02 [CRITICAL] Número do cartão e chave do gateway impressos no log
File: src/AppManager.js:45
Catalog: AP-03
Description: A cada checkout: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`. Confirmado no log da linha de base (`Processando cartão 4111222233334444 na chave pk_live_...`).
Impact: PAN completo e chave do gateway vão para o stdout/agregador de logs — violação direta de PCI-DSS e vazamento de credencial.
Recommendation: Remover dados sensíveis dos logs; logar no máximo os 4 últimos dígitos mascarados, via logger com níveis (T-07, T-14).

### F-03 [CRITICAL] Armazenamento inseguro de senhas
File: src/utils.js:17-23 | src/AppManager.js:18, 68
Catalog: AP-04
Description: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e corta em 10 (`Buffer.from(pwd).toString('base64').substring(0, 2)`) — é reversível e colide para qualquer senha com o mesmo prefixo; o seed grava a senha em texto puro (`'123'`); sem senha, o usuário é criado com a senha padrão `p || "123456"`.
Impact: Um vazamento do banco expõe as senhas; senhas diferentes com o mesmo início geram o mesmo "hash"; contas criadas sem senha têm senha conhecida.
Recommendation: `crypto.scrypt` com salt aleatório por usuário, sem senha padrão (T-06).

### F-04 [CRITICAL] God Class `AppManager`
File: src/AppManager.js:4-139
Catalog: AP-05
Description: Uma única classe abre a conexão (`new sqlite3.Database(':memory:')`, l. 7), cria o schema e o seed (l. 10-23), registra todas as rotas (l. 25-137), executa SQL, aplica a regra de pagamento (l. 46) e formata as respostas.
Impact: Nada pode ser testado isoladamente; qualquer mudança em checkout, relatório ou usuários mexe no mesmo arquivo.
Recommendation: Separar em config, database, models por entidade, controllers/services e rotas (T-03, T-16).

### F-05 [CRITICAL] Endpoints administrativos e destrutivos sem autenticação
File: src/AppManager.js:80, 131-137
Catalog: AP-06
Description: `GET /api/admin/financial-report` devolve receita por curso e nomes de alunos com o valor pago, e `DELETE /api/users/:id` apaga usuários — nenhum dos dois verifica identidade ou papel.
Impact: Qualquer pessoa lê dados financeiros e pessoais e apaga usuários arbitrários.
Recommendation: Middleware de autorização por token administrativo (lido do ambiente) nas rotas admin e de remoção (T-15).

### F-06 [CRITICAL] Callback hell sem controle de erro — um request derruba o servidor
File: src/AppManager.js:37-78, 46, 57, 92-93, 104, 106, 133
Catalog: AP-13
Description: O checkout aninha 6 níveis de callbacks. `cc.startsWith("4")` (l. 46) roda sobre input não validado: `"card": 4111` (número) lança `TypeError: cc.startsWith is not a function` dentro do callback do sqlite3 e **mata o processo** (reproduzido na análise). Vários callbacks ignoram `err` (l. 57, 104, 106, 133) e l. 92-93 faz `enrollments.length` sem checar `err`.
Impact: Um único request malformado derruba a API para todos; erros de banco passam silenciosos ou quebram o processo.
Recommendation: Driver com Promises + `async/await`, `try/catch` via `asyncHandler` e repasse ao error handler central (T-10, T-09).

### F-07 [HIGH] Regra de negócio e SQL dentro dos handlers de rota
File: src/AppManager.js:28-78, 80-129
Catalog: AP-08
Description: O handler de checkout valida o body, busca curso e usuário, cria usuário, decide o pagamento (`cc.startsWith("4") ? "PAID" : "DENIED"`), grava matrícula, pagamento e auditoria e monta o JSON. O handler do relatório faz a agregação de receita inteira.
Impact: A regra de checkout fica presa ao HTTP; não dá para reusar nem testar sem subir o servidor.
Recommendation: Mover para `CheckoutService` / `ReportService` chamados por controllers finos (T-04).

### F-08 [HIGH] Checkout e remoção multi-etapa sem transação
File: src/AppManager.js:48, 50-61, 69-71, 133-135
Catalog: AP-12
Description: O usuário é inserido (l. 69) **antes** da decisão de pagamento; se o cartão é recusado (l. 48) o usuário fica criado. Matrícula (l. 50), pagamento (l. 54) e auditoria (l. 57) são INSERTs independentes. `DELETE /api/users/:id` apaga o usuário e deixa matrículas e pagamentos órfãos — a própria resposta admite: `"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."` (na linha de base, o relatório passa a mostrar `"Unknown"`).
Impact: Falha no meio deixa matrícula sem pagamento, usuários fantasmas de pagamentos recusados e registros órfãos.
Recommendation: Envolver cada fluxo em `BEGIN/COMMIT/ROLLBACK` (T-10). A remoção em cascata mudaria o relatório (contrato); manter o comportamento de dados e registrar como pendência.

### F-09 [HIGH] Estado global mutável e conexão única compartilhada
File: src/utils.js:9-15, 25 | src/AppManager.js:2, 7
Catalog: AP-10
Description: `let globalCache = {}` e `let totalRevenue = 0` são exportados; `logAndCache` muta `globalCache` a cada checkout (l. 14) e nada lê o cache. A conexão é criada no construtor e compartilhada por todas as requisições.
Impact: Cache cresce sem limite (vazamento de memória) e sem dono; estado vaza entre requisições e testes.
Recommendation: Remover o cache sem leitor; conexão gerenciada por um módulo de database injetado (T-05).

### F-10 [HIGH] Acoplamento forte sem injeção de dependência
File: src/AppManager.js:1-2, 7, 45-46
Catalog: AP-11
Description: A classe instancia o próprio banco (`new sqlite3.Database(':memory:')`), importa `config` global e embute o "gateway de pagamento" inline no handler.
Impact: Impossível trocar o banco ou mockar o gateway em testes.
Recommendation: Composition root em `app.js` cria db e gateway e os injeta em models/services (T-05).

### F-11 [MEDIUM] Relatório financeiro com N+1 e ordem não determinística
File: src/AppManager.js:83, 92, 104, 106
Catalog: AP-15
Description: 1 query de cursos + 1 de matrículas por curso + 2 queries (usuário e pagamento) por matrícula. O array é montado na ordem em que os callbacks terminam (na linha de base, #1 veio `Docker` primeiro e #7 `Clean Architecture` primeiro).
Impact: O número de queries cresce linearmente com matrículas; resposta com ordem imprevisível.
Recommendation: Uma query com `JOIN`s ordenada por id e agregação em memória (T-08).

### F-12 [MEDIUM] Tratamento de erro disperso, formatos e status inconsistentes
File: src/AppManager.js:35, 38, 41, 51, 55, 70, 84, 133-135 | src/app.js:1-14
Catalog: AP-16
Description: Erros em texto puro (`res.status(500).send("Erro DB")`) enquanto os sucessos são JSON; `err || !course` responde 404 até para erro de banco (l. 38); `DELETE` responde 200 mesmo quando o id não existe (linha de base #9); não há middleware de erro no `app.js`.
Impact: Cliente não consegue distinguir erros; falhas reais aparecem como "não encontrado".
Recommendation: Middleware de erro central e classes de erro de domínio; preservar as mensagens atuais de cada caso (T-09).

### F-13 [MEDIUM] Validação de entrada só de presença
File: src/AppManager.js:29-35, 132
Catalog: AP-17
Description: `if (!u || !e || !cid || !cc)` só testa presença: `card` não é checado como string (causa o crash de F-06), `eml` não tem formato, `c_id` não tem tipo; `:id` do DELETE não é validado.
Impact: Dados inválidos no banco e erros 500/crash no lugar de 400.
Recommendation: Validador do checkout na camada de rota/controller, devolvendo o mesmo `400 Bad Request` atual (T-11).

### F-14 [MEDIUM] [DEPRECATED] Driver `sqlite3` baseado em callbacks e estilo `self = this`
File: src/AppManager.js:1, 26, 50, 54, 69
Catalog: AP-19
Description: `require('sqlite3').verbose()` (API de callbacks, modo verbose em produção), `const self = this` e `function(err)` só para acessar `this.lastID`.
Impact: Impede `async/await`, alimenta o callback hell de F-06; o pacote nativo precisa compilar a cada versão de Node.
Recommendation: `node:sqlite` (`DatabaseSync`, disponível no Node instalado v25.8.2) ou wrapper com Promises; arrow functions (T-12).

### F-15 [MEDIUM] Logging com `console.log`, sem níveis
File: src/app.js:13 | src/utils.js:13
Catalog: AP-20
Description: `console.log(\`Frankenstein LMS rodando...\`)` e `console.log(\`[LOG] Salvando no cache: ${key}\`)`.
Impact: Sem níveis nem destino configurável; ruído em produção.
Recommendation: Logger mínimo com níveis controlado por `LOG_LEVEL` (T-14).

### F-16 [MEDIUM] Porta fixa e schema/seed acoplados à classe de rotas
File: src/utils.js:6 | src/app.js:9, 12 | src/AppManager.js:10-23
Catalog: AP-21
Description: `port: 3000` fixo (não lê `PORT`); schema e seed são criados dentro do mesmo objeto que registra rotas.
Impact: Não dá para subir duas instâncias nem mudar a porta por ambiente; o seed não pode ser reaproveitado nem desligado.
Recommendation: `PORT` e `DB_PATH` via ambiente com defaults atuais (3000, `:memory:`); schema e seed em módulo próprio (T-01, T-16).

### F-17 [MEDIUM] `utils.js` sem coesão
File: src/utils.js:1-25
Catalog: AP-26
Description: O mesmo módulo mistura configuração/segredos, cache global, contador de receita e hashing de senha.
Impact: Não há lugar óbvio para config ou segurança; mudar um assunto mexe nos outros.
Recommendation: `config/`, `utils/password.js` (ou `services/`) e remoção do que não é usado (T-18).

### F-18 [LOW] Magic numbers e strings de negócio
File: src/AppManager.js:21, 46, 48, 68, 108 | src/utils.js:19, 22
Catalog: AP-22
Description: A regra de aprovação é `cc.startsWith("4")`; status `'PAID'`/`"DENIED"` repetidos como literais; senha padrão `"123456"`; `10000` iterações e `substring(0, 10)` no hash.
Impact: Regras implícitas espalhadas pelo código.
Recommendation: Constantes nomeadas (`PAYMENT_STATUS`, `APPROVED_CARD_PREFIX`) (T-13).

### F-19 [LOW] Nomes ruins
File: src/AppManager.js:4, 29-33 | src/utils.js:12, 17
Catalog: AP-23
Description: `u`, `e`, `p`, `cid`, `cc` para os campos do checkout; classe genérica `AppManager`; funções `badCrypto` e `logAndCache`.
Impact: Leitura lenta; `e` sombreia o nome convencional de erro.
Recommendation: Nomes de domínio (`name`, `email`, `password`, `courseId`, `cardNumber`) mantendo as chaves do JSON (T-13).

### F-20 [LOW] Variáveis e configurações não usadas
File: src/AppManager.js:2 | src/utils.js:2-5, 10, 25
Catalog: AP-24
Description: `totalRevenue` é importado e nunca usado; `globalCache` é exportado e ninguém importa; `config.dbUser`, `dbPass` e `smtpUser` nunca são lidos.
Impact: Ruído que sugere funcionalidades (SMTP, auth de banco) que não existem.
Recommendation: Remover (T-13).

## Deprecated APIs

| API | Onde | Equivalente moderno |
|---|---|---|
| Driver `sqlite3` de callbacks + `.verbose()` | src/AppManager.js:1, 7, 37, 50, 54, 69, 83 | `node:sqlite` (`DatabaseSync`, Node ≥ 22.5; instalado v25.8.2) com transações explícitas |
| `const self = this` + `function(err)` para `this.lastID` | src/AppManager.js:26, 50, 54, 69 | arrow functions + `run(...).lastInsertRowid` |
| Hash de senha caseiro (base64) | src/utils.js:17-23 | `crypto.scryptSync` + `crypto.randomBytes` (salt) |

`node --trace-deprecation` não emitiu nenhum warning no boot da linha de base (Express 4.22.1, sqlite3 5.1.7, Node v25.8.2).

## Architecture Overview

- **Current:** Monolítica — `src/AppManager.js` concentra conexão, schema, seed, rotas, SQL e regra de negócio; `src/utils.js` mistura config com segredos, estado global e hashing.
- **Target:** `src/config` (env) → `src/database` (conexão, schema, seed) → `src/models` (users, courses, enrollments, payments, audit logs) → `src/services` (checkout, relatório, pagamento) → `src/controllers` → `src/routes` + `src/middlewares` (auth admin, erros), com `src/app.js` como composition root e `npm start` preservado.

```
================================
Total: 20 findings
================================
```
