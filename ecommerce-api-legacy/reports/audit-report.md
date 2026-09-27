# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js v25.8.2) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code
Date:    2026-09-27
================================
```

## Summary

CRITICAL: 7 | HIGH: 5 | MEDIUM: 6 | LOW: 4
Probes: 11 vulneráveis de 13 executadas — todas cobertas por findings (P1→F-02, P2/P10→F-03, P7/P12→F-04, P4/P5→F-07, P8→F-08, P11→F-12, P9→F-14, P6→F-15)

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | 7 | F-01, F-02, F-03, F-04, F-05, F-06, F-07 |
| HIGH | 5 | F-08, F-09, F-10, F-11, F-12 |
| MEDIUM | 6 | F-13, F-14, F-15, F-16, F-17, F-18 |
| LOW | 4 | F-19, F-20, F-21, F-22 |

## Findings

### F-01 [CRITICAL] Credenciais e chave de pagamento hardcoded
File: src/utils.js:2-6
Catalog: AP-01
Description: O objeto `config` guarda segredos de produção literais: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `dbUser: "admin_master"`, `smtpUser: ...`, e a porta fixa `port: 3000`. Nenhuma variável de ambiente é lida em lugar nenhum do código.
Impact: Os segredos vazam junto com o repositório e não podem ser trocados por ambiente. A chave `pk_live_` também é impressa no log a cada checkout (F-04).
Recommendation: Criar um módulo `config/` que lê `process.env` com defaults de desenvolvimento, e um `.env.example` sem valores reais (T-01).

### F-02 [CRITICAL] O checkout age em nome de uma conta existente sem verificar a senha
File: src/AppManager.js:31, 40, 66-75
Catalog: AP-06
Evidence: probe P1
Description: A conta é localizada só pelo e-mail enviado (`SELECT id FROM users WHERE email = ?`). Se ela existe, `processPaymentAndEnroll(user.id)` roda sem comparar `pwd`. A senha só é usada no ramo de criação (`badCrypto(p || "123456")`).
Impact: Qualquer pessoa que conheça o e-mail de alguém consegue matricular e cobrar em nome dessa conta. Na sonda P1, `senha-errada` criou uma matrícula paga na conta de Leonan.
Recommendation: Quando o e-mail já existe, exigir `pwd` e compará-la com o hash guardado (comparação em tempo constante). Se não bater, responder 401 sem criar nada (T-15, T-06).

### F-03 [CRITICAL] Relatório financeiro e remoção de usuários sem autenticação
File: src/AppManager.js:80, 131-137
Catalog: AP-06
Evidence: probe P2, probe P10
Description: `GET /api/admin/financial-report` devolve a receita de cada curso com os nomes dos alunos, e `DELETE /api/users/:id` apaga usuários. Nenhuma das duas rotas verifica identidade ou papel.
Impact: Dados financeiros e pessoais ficam públicos, e qualquer cliente pode apagar qualquer usuário (P10 removeu o usuário 2 sem credencial).
Recommendation: Aplicar um middleware de autorização administrativa (token lido da config e enviado em cabeçalho) nas duas rotas: 401 sem token e 403 com token inválido (T-15).

### F-04 [CRITICAL] Número do cartão e chave do gateway no log; stack trace devolvido ao cliente
File: src/AppManager.js:45 | src/app.js:5-14
Catalog: AP-03
Evidence: probe P12, probe P7
Description: Cada checkout executa `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`. Além disso, `app.js` não registra nenhum error handler, então o handler padrão do Express devolve o stack trace, com caminhos absolutos do servidor, para JSON inválido (`NODE_ENV` nunca é definido nem lido).
Impact: O PAN completo e a chave live ficam no log, o que viola a PCI-DSS (P12 encontrou 8 ocorrências numa sessão curta). Os stack traces revelam a estrutura interna e as versões das dependências.
Recommendation: Nunca logar o cartão nem os segredos; no máximo os 4 últimos dígitos, via logger (T-07, T-14). Registrar um error handler central que responde com uma mensagem genérica (T-09).

### F-05 [CRITICAL] Hash de senha caseiro, senha padrão e seed em texto puro
File: src/utils.js:17-23 | src/AppManager.js:18, 68
Catalog: AP-04
Description: `badCrypto` repete os 2 primeiros caracteres do base64 da senha e corta em 10: `hash += Buffer.from(pwd).toString('base64').substring(0, 2)`. Isso é determinístico, sem salt e reversível na prática. Quando `pwd` falta, usa `"123456"`. O seed grava `'123'` em texto puro.
Impact: Senhas diferentes com o mesmo prefixo geram o mesmo "hash", e qualquer vazamento do banco expõe todas as senhas. Contas criadas sem senha ficam com uma senha conhecida.
Recommendation: Usar `crypto.scrypt` com salt aleatório e `timingSafeEqual`. Exigir `pwd` ao criar conta e guardar o seed já com hash (T-06).

### F-06 [CRITICAL] God Class `AppManager`
File: src/AppManager.js:4-141
Catalog: AP-05
Description: Uma única classe abre a conexão (`:7`), cria o schema e o seed (`:10-23`), registra todas as rotas (`:25-137`), executa SQL inline e aplica a regra de pagamento (`:46`) e de relatório (`:89-127`), além de formatar as respostas.
Impact: Nenhuma parte pode ser testada ou reutilizada isoladamente, e qualquer mudança (outro banco, outro gateway, outra rota) mexe no mesmo arquivo.
Recommendation: Dividir em `database/`, `models/` por entidade, `services/` de checkout e relatório, `controllers/`, `views/routes.js` e um composition root em `app.js` (T-03, T-16).

### F-07 [CRITICAL] Um único request malformado derruba o servidor; callbacks aninhados que ignoram `err`
File: src/AppManager.js:37-77, 46, 57, 92-93, 104, 106, 133
Catalog: AP-13
Evidence: probe P4, probe P5
Description: `cc.startsWith("4")` roda sobre `req.body.card` sem validar o tipo. Com `card` numérico ou objeto, lança `TypeError` dentro de um callback do sqlite3, fora do alcance do Express, e o processo termina. O checkout tem 5 níveis de callbacks (`:37→40→50→54→57`). Vários callbacks ignoram `err`: `:57` (audit), `:92-93` (`enrollments.length` com `err` ignorado), `:104`, `:106` e `:133`.
Impact: Negação de serviço trivial. Como o banco é em memória, cada queda também apaga todos os dados (P4 e P5 derrubaram o processo e zeraram o banco). Erros de banco passam em silêncio ou viram crash.
Recommendation: Migrar para `async/await` sobre helpers com Promise, repassar rejeições ao error handler (`asyncHandler`) e validar os tipos antes de usar (T-10, T-11).

### F-08 [HIGH] Checkout multi-etapa sem transação: usuário gravado mesmo quando o pagamento é recusado
File: src/AppManager.js:46-48, 50-61, 66-72
Catalog: AP-12
Evidence: probe P8, probe P4
Description: O usuário é inserido (`:69`) **antes** da decisão de pagamento (`:46-48`). Se o pagamento é recusado, a resposta é 400, mas o usuário continua gravado. Os três inserts seguintes (enrollment `:50`, payment `:54`, audit `:57`) também não estão numa transação.
Impact: Na P8, o usuário "Fantasma" (pagamento recusado) ficou gravado, e o checkout seguinte com o mesmo e-mail reutilizou esse registro e ignorou o nome enviado. Uma falha entre os inserts deixa uma matrícula sem pagamento.
Recommendation: Decidir o pagamento antes de qualquer escrita e envolver criação de usuário, matrícula, pagamento e audit em `BEGIN/COMMIT/ROLLBACK` (T-10).

### F-09 [HIGH] Regra de negócio e SQL dentro dos handlers de rota
File: src/AppManager.js:28-78, 80-129
Catalog: AP-08
Description: O handler de `POST /api/checkout` valida a entrada, consulta cursos e usuários, cria a conta, decide o pagamento (`cc.startsWith("4") ? "PAID" : "DENIED"`), grava três tabelas e monta a resposta. O handler do relatório calcula a receita (`courseData.revenue += payment.amount`) e monta a estrutura com contadores manuais.
Impact: A regra de pagamento e o cálculo de receita ficam presos ao HTTP e não podem ser testados sem subir o servidor.
Recommendation: Mover as regras para `CheckoutService`/`ReportService` e o SQL para models, deixando nas rotas só o mapeamento HTTP (T-04).

### F-10 [HIGH] Estado global mutável e conexão única compartilhada
File: src/utils.js:9-15, 25 | src/AppManager.js:7, 59
Catalog: AP-10
Description: `let globalCache = {}` é exportado e mutado por `logAndCache` a cada checkout (`:59`), mas nunca é lido. `let totalRevenue = 0` é exportado como primitivo (a cópia importada nunca muda). A conexão única `new sqlite3.Database(':memory:')` fica presa na instância.
Impact: O cache cresce sem limite (um item por usuário) e sem dono, e os módulos que o importam compartilham estado entre requisições e testes.
Recommendation: Remover o cache e o contador mortos. A conexão passa a ser criada pelo composition root e injetada (T-05).

### F-11 [HIGH] Acoplamento forte sem injeção de dependência
File: src/AppManager.js:1-2, 5-8, 45-46 | src/app.js:8-10
Catalog: AP-11
Description: `AppManager` instancia o próprio banco no construtor (`new sqlite3.Database(':memory:')`), importa `config` de um módulo global e embute o "gateway de pagamento" como uma condição inline. `app.js` não injeta nada.
Impact: Não dá para trocar o banco nem simular o gateway em testes, e a regra de aprovação de cartão não tem ponto de extensão.
Recommendation: Criar `createApp({ config, db })`, onde o composition root instancia a conexão e um `paymentGateway` e os passa por construtor/fábrica (T-05).

### F-12 [HIGH] Remover usuário deixa matrículas e pagamentos órfãos contados como receita
File: src/AppManager.js:131-136, 104-115
Catalog: AP-12
Evidence: probe P11
Description: `DELETE FROM users WHERE id = ?` remove só o usuário. A própria mensagem admite: `"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."`. O relatório segue somando esses pagamentos e mostra `student: 'Unknown'`.
Impact: Integridade referencial quebrada: depois de P11, o relatório lista `{"student":"Unknown","paid":997}` e a receita mantém valores de alunos inexistentes.
Recommendation: Remover payments → enrollments → user numa transação (cascata explícita) e manter a mensagem de resposta (T-10).

### F-13 [MEDIUM] N+1 no relatório financeiro e ordem de resposta não determinística
File: src/AppManager.js:83, 92, 104, 106, 95-99, 117-122
Catalog: AP-15
Evidence: baseline #1, #6, probe P2
Description: Uma query de cursos, depois uma de matrículas por curso e duas (usuário + pagamento) por matrícula: são 1 + C + 2E queries. A conclusão depende de contadores manuais duplicados (`coursesPending--; if (coursesPending === 0) res.json(report)` em `:96-98` e `:119-121`), então a ordem dos cursos no array depende de qual callback termina primeiro.
Impact: O número de queries cresce linearmente com as matrículas. A ordem dos cursos mudou entre as requisições da linha de base (Docker primeiro em #1, Clean Architecture primeiro em P2).
Recommendation: Uma única query com `LEFT JOIN` + agregação no service, ordenada por id do curso (T-08).

### F-14 [MEDIUM] Tratamento de erro disperso e status que mentem
File: src/AppManager.js:35, 38, 41, 48, 51, 55, 70, 84, 133-135
Catalog: AP-16
Evidence: probe P9, probe P7
Description: Cada handler trata erro à sua maneira: texto puro (`res.status(500).send("Erro DB")`) no meio de respostas JSON, erro de banco convertido em 404 (`if (err || !course) return res.status(404)`), e `DELETE` que responde 200 sem checar `err` nem `this.changes`. Não existe error handler central.
Impact: `DELETE /api/users/999` responde "Usuário deletado" sem remover nada (P9). Uma falha de banco aparece como "Curso não encontrado", e o cliente não tem um formato de erro previsível.
Recommendation: Criar um middleware central com classes de erro (`NotFoundError`, `ValidationError`...). O DELETE de um id inexistente passa a responder 404. As mensagens e status de sucesso atuais continuam os mesmos (T-09).

### F-15 [MEDIUM] Validação de entrada só de presença, sem tipo nem formato
File: src/AppManager.js:29-35, 68, 132
Catalog: AP-17
Evidence: probe P6
Description: `if (!u || !e || !cid || !cc)` só testa se o valor é truthy. `usr: 123` e `eml: ["a"]` passam e são gravados. `pwd` é opcional. `c_id` e `:id` não são validados como inteiros.
Impact: Dados inválidos chegam ao banco: na P6, um usuário com nome `123` e e-mail vindo de um array. Tipos errados em `card` derrubam o processo (F-07).
Recommendation: Validar tipos (strings não vazias, e-mail em formato válido, `c_id` inteiro positivo, `card` string de dígitos) no controller e responder 400 com a mesma mensagem `Bad Request` (T-11).

### F-16 [MEDIUM] Logging com `console.log`, sem níveis
File: src/app.js:13 | src/utils.js:13
Catalog: AP-20
Description: Eventos da aplicação são registrados com `console.log` (`[LOG] Salvando no cache: ...`, banner de boot), sem nível nem destino configurável. O log de cartão em `AppManager.js:45` está coberto por F-04.
Impact: Não dá para filtrar ou silenciar o log por ambiente, o que gera ruído em produção.
Recommendation: Criar um logger mínimo com níveis, configurado por `LOG_LEVEL` (T-14).

### F-17 [MEDIUM] Porta fixa no código e schema/seed acoplados à classe de rotas
File: src/utils.js:6 | src/app.js:12 | src/AppManager.js:9-23
Catalog: AP-21
Description: `port: 3000` é literal e `app.listen(config.port)` não aceita override. Schema e seed são executados pela mesma classe que registra as rotas.
Impact: A aplicação não sobe onde a porta 3000 está ocupada (a linha de base só rodou porque o literal foi alterado numa cópia), e não dá para criar o schema sem montar as rotas.
Recommendation: Ler `PORT` do ambiente (default 3000) e mover schema/seed para `database/schema.js` (T-01, T-16).

### F-18 [MEDIUM] `utils.js` sem coesão
File: src/utils.js:1-25
Catalog: AP-26
Description: O mesmo módulo "utilitário" mistura configuração e segredos, um cache global, um contador de receita e o hash de senha.
Impact: Não existe um lugar óbvio para config, segurança ou estado, e mudar um assunto mexe num arquivo que todos importam.
Recommendation: Separar em `config/index.js`, `services/passwordHasher.js` e remover o estado morto (T-18).

### F-19 [LOW] Magic numbers e strings de negócio
File: src/AppManager.js:21, 46, 48, 68, 108 | src/utils.js:6, 19, 22
Catalog: AP-22
Description: A regra de aprovação é `cc.startsWith("4")`, sem nome. Os status `'PAID'`/`'DENIED'` aparecem como literais em quatro pontos. O default de senha é `"123456"`, e `badCrypto` usa `10000`/`substring(0, 10)`.
Impact: A regra de aprovação fica implícita e os status podem divergir entre os pontos de uso.
Recommendation: Criar constantes de domínio (`PAYMENT_STATUS`, `APPROVED_CARD_PREFIX`) (T-13).

### F-20 [LOW] Nomes ruins
File: src/AppManager.js:4, 29-33 | src/utils.js:12, 17
Catalog: AP-23
Description: As variáveis locais `u`, `e`, `p`, `cid`, `cc`, a classe genérica `AppManager` e as funções `badCrypto` e `logAndCache`. Os nomes dos campos do JSON (`usr`, `eml`, `pwd`, `c_id`, `card`) fazem parte do contrato e **não** devem mudar.
Impact: A leitura fica lenta e a intenção obscura.
Recommendation: Usar nomes descritivos internamente, mantendo os nomes dos campos da API (T-13).

### F-21 [LOW] Imports, exports e campos de config não usados
File: src/AppManager.js:2 | src/utils.js:2-3, 5, 10, 25
Catalog: AP-24
Description: `totalRevenue` é importado em `AppManager.js:2` e nunca lido. `dbUser`, `dbPass` e `smtpUser` nunca são usados (confirmado por busca). `globalCache` é exportado e nunca lido.
Impact: O código parece ter integrações (SMTP, banco autenticado, contador de receita) que não existem.
Recommendation: Remover (T-13).

### F-22 [LOW] [DEPRECATED] Driver `sqlite3` baseado em callbacks e estilo `self = this` + `function()`
File: src/AppManager.js:1, 7, 26, 50, 54, 69
Catalog: AP-19
Description: O driver `sqlite3` (5.1.7) só tem API de callbacks. O código usa `const self = this` e `function(err) { this.lastID }` para contornar o `this`. O npm não marca a 5.1.7 como deprecated e o boot não emitiu warnings, então aqui é estilo legado (LOW). A consequência grave (callback hell) está em F-07.
Impact: O fluxo assíncrono fica impossível de compor com `try/catch`, o que é a causa raiz de F-07 e F-08.
Recommendation: Usar `node:sqlite` (`DatabaseSync`, disponível no Node ≥ 22.5; instalado v25.8.2) ou um wrapper com Promise + `async/await` (T-12).

## Deprecated APIs

| API | Onde | Equivalente moderno |
|---|---|---|
| driver `sqlite3` com callbacks (`db.get/run/all(sql, params, cb)`) | src/AppManager.js:1, 7, 37-133 | `node:sqlite` (`DatabaseSync`, Node ≥ 22.5) ou wrapper com Promise + `async/await` |
| `const self = this` + `function(err) { this.lastID }` | src/AppManager.js:26, 50, 54, 69 | arrow functions + `async/await` (`const { lastInsertRowid } = stmt.run(...)`) |

Versões verificadas: Node v25.8.2, express 4.22.1, sqlite3 5.1.7 (sem aviso de deprecation no npm nem no boot com `--trace-deprecation`).

## Architecture Overview

- **Current:** Monolítica. `src/AppManager.js` concentra conexão, schema, seed, rotas, SQL e regras, e `utils.js` mistura config, segredos, estado global e hash de senha.
- **Target:** `src/server.js` (listen) + `src/app.js` (composition root `createApp`), `config/`, `database/` (connection + schema/seed), `models/` (user, course, enrollment, payment, auditLog), `services/` (checkout, report, paymentGateway, passwordHasher), `controllers/` (checkout, report, user), `views/` (routes + presenters) e `middlewares/` (errorHandler, asyncHandler, requireAdmin).

```
================================
Total: 22 findings
================================
```
