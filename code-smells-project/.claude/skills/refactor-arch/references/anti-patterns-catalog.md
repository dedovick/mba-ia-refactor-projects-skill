# Catálogo de Anti-Patterns

Use este catálogo na **Fase 2**. Percorra **todos** os itens, em ordem, em todos os arquivos-fonte. Cada item traz os sinais de detecção (o que procurar), a severidade padrão, quando ajustá-la e a transformação do playbook que resolve o problema.

## Escala de severidade

| Severidade | Critério |
|---|---|
| **CRITICAL** | Falha grave de arquitetura ou segurança: impede o funcionamento correto, expõe dados sensíveis (credenciais hardcoded, SQL Injection, senhas em respostas) ou viola completamente a separação de responsabilidades (God Class com banco, regra e roteamento juntos) |
| **HIGH** | Forte violação de MVC ou SOLID que dificulta muito manutenção e testes: regra de negócio pesada em controllers/rotas, acoplamento forte sem injeção de dependência, estado global mutável |
| **MEDIUM** | Padronização, duplicação ou performance moderada: N+1, uso inadequado de middlewares, validação ausente nas rotas, tratamento de erro inconsistente, APIs deprecated |
| **LOW** | Legibilidade: nomes ruins, magic numbers, imports e código mortos, estilo desatualizado |

## Índice

| ID | Anti-pattern | Severidade padrão | Correção |
|---|---|---|---|
| AP-01 | Credenciais e segredos hardcoded | CRITICAL | T-01 |
| AP-02 | SQL Injection (query montada com strings) | CRITICAL | T-02 |
| AP-03 | Dados sensíveis expostos (respostas, logs) | CRITICAL | T-07 |
| AP-04 | Armazenamento inseguro de senhas | CRITICAL | T-06 |
| AP-05 | God Class / God Module | CRITICAL | T-03 / T-16 |
| AP-06 | Endpoints perigosos sem autenticação/autorização | CRITICAL | T-15 |
| AP-07 | Modo debug ou config de desenvolvimento em produção | CRITICAL | T-01 |
| AP-08 | Regra de negócio em rotas/controllers ("fat controller") | HIGH | T-04 |
| AP-09 | Regra de negócio ou orquestração dentro de models | HIGH | T-04 |
| AP-10 | Estado global mutável / conexão compartilhada | HIGH | T-05 |
| AP-11 | Acoplamento forte sem injeção de dependência | HIGH | T-05 |
| AP-12 | Operação multi-etapa sem transação | HIGH | T-10 |
| AP-13 | Callback hell / fluxo assíncrono sem controle de erro | HIGH | T-10 |
| AP-14 | Camada morta ou duplicada (código existe e não é usado) | HIGH | T-04 |
| AP-15 | Queries N+1 e agregações ineficientes | MEDIUM | T-08 |
| AP-16 | Tratamento de erro ausente, genérico ou disperso | MEDIUM | T-09 |
| AP-17 | Validação de entrada ausente ou inconsistente | MEDIUM | T-11 |
| AP-18 | Código duplicado | MEDIUM | T-04 / T-11 |
| AP-19 | Uso de API deprecated ou legada | MEDIUM | T-12 |
| AP-20 | Logging com print / console e sem níveis | MEDIUM | T-14 |
| AP-21 | Middleware ou configuração HTTP inadequada (CORS aberto, sem limites) | MEDIUM | T-01 / T-16 |
| AP-22 | Magic numbers e strings | LOW | T-13 |
| AP-23 | Nomes ruins | LOW | T-13 |
| AP-24 | Imports, variáveis e funções não usados | LOW | T-13 |

---

## CRITICAL

### AP-01 — Credenciais e segredos hardcoded
**Sinais de detecção**
- Atribuições literais a nomes como `SECRET_KEY`, `password`, `passwd`, `pass`, `secret`, `token`, `api_key`, `apiKey`, `gatewayKey`, `private_key`, `smtp_*`, `db_user`, `db_pass`.
- Prefixos de chaves reais: `sk_live_`, `pk_live_`, `AKIA`, `ghp_`, `xoxb-`, `-----BEGIN`.
- Strings de conexão com usuário e senha (`postgres://user:pass@`, `mongodb+srv://`).
- Dependência como `python-dotenv` declarada, mas nenhuma leitura de variável de ambiente no código.
```bash
grep -rnEi "(secret|passw|pwd|token|api[_-]?key|private[_-]?key|smtp)[a-z_]*['\"]?\s*[:=]\s*['\"][^'\"]{3,}" --include=*.{py,js,ts} .
```
**Por que importa:** segredos versionados vazam junto com o repositório e não podem ser trocados por ambiente.

### AP-02 — SQL Injection
**Sinais de detecção**
- SQL montado com concatenação ou interpolação: `"... WHERE x = '" + valor + "'"`, `f"SELECT ... {valor}"`, `"..." % valor`, template literals `` `SELECT ... ${valor}` ``.
- `execute(query)` onde `query` vem, direta ou indiretamente, de input do usuário.
- Endpoint que recebe SQL do cliente e executa (é AP-02 **e** AP-06).
```bash
grep -rnE "(SELECT|INSERT|UPDATE|DELETE)[^\"']*[\"']\s*\+|f[\"'](SELECT|INSERT|UPDATE|DELETE)|\\$\{[^}]+\}[^\`]*(WHERE|VALUES)" --include=*.{py,js,ts} .
```
**Por que importa:** permite burlar autenticação, ler, alterar ou apagar o banco. Um valor com apóstrofo já quebra a query.

### AP-03 — Dados sensíveis expostos
**Sinais de detecção**
- Serialização de entidades que inclui `password`, `senha`, `hash`, `token`, `secret` (ex.: `to_dict()` com a senha, `SELECT *` devolvido direto).
- Endpoints de health/debug/info que devolvem configuração (`secret_key`, `debug`, caminhos, strings de conexão).
- Logs com dados de cartão, senhas, tokens ou chaves (`print(...)`, `console.log(...)` com essas variáveis).
- Mensagens de erro internas repassadas ao cliente (`str(e)`, `err.message`, stack traces).

**Por que importa:** vazamento direto de credenciais e dados pessoais (LGPD, PCI-DSS).

### AP-04 — Armazenamento inseguro de senhas
**Sinais de detecção**
- Senha gravada ou comparada em texto puro (`WHERE password = ?`, `if user.password == password`).
- Hashes rápidos e sem salt: `md5`, `sha1`, `sha256` direto, base64 ou "criptografia" caseira.
- Senha padrão quando o campo vem vazio (`password or "123456"`).

**Por que importa:** qualquer vazamento do banco expõe todas as senhas; hashes rápidos caem com rainbow tables.

### AP-05 — God Class / God Module
**Sinais de detecção**
- Um arquivo ou classe que faz **três ou mais** destas coisas: abrir conexão/criar schema, registrar rotas, executar SQL, aplicar regra de negócio, formatar resposta, configurar a aplicação.
- Arquivos muito maiores que os demais concentrando vários domínios (clientes, faturas e estoque no mesmo arquivo).
- Classes com nome genérico (`Manager`, `Core`, `Utils`, `Helper`) e dezenas de responsabilidades.

**Ajuste:** se o arquivo concentra muito, mas as camadas estão separadas em funções coesas, rebaixe para HIGH.
**Por que importa:** nada pode ser testado isoladamente, e qualquer mudança afeta tudo.

### AP-06 — Endpoints perigosos sem autenticação/autorização
**Sinais de detecção**
- Rotas administrativas (`/admin/*`, `reset`, `query`, `report`, `delete`) sem verificação de identidade ou papel.
- Login que não emite token/sessão, ou token previsível (ex.: prefixo fixo + id do usuário) que nenhuma rota valida.
- Campo `role`/`tipo` aceito do cliente na criação de usuário, permitindo criar administradores.

**Ajuste:** HIGH quando a rota só lê dados não sensíveis; CRITICAL quando destrói dados, executa comandos ou expõe dados pessoais/financeiros.
**Por que importa:** qualquer pessoa apaga dados ou lê informações restritas.

### AP-07 — Debug ou config de desenvolvimento em produção
**Sinais de detecção**
- `debug=True`, `DEBUG = True`, `app.run(debug=True, host="0.0.0.0")` fixos no código.
- Stack traces devolvidos ao cliente; `NODE_ENV` ignorado.

**Ajuste:** CRITICAL com bind público (`0.0.0.0`); HIGH se só local.
**Por que importa:** o debugger interativo (ex.: Werkzeug) permite execução remota de código.

---

## HIGH

### AP-08 — Regra de negócio em rotas/controllers ("fat controller")
**Sinais de detecção**
- Handlers de rota com dezenas de linhas que validam, calculam, consultam o banco e formatam a resposta.
- Queries SQL/ORM escritas dentro do handler.
- Cálculos de domínio (totais, descontos, status, prazos) dentro da função da rota.

**Por que importa:** a regra fica presa ao HTTP, não pode ser reutilizada nem testada sem subir o servidor.

### AP-09 — Regra de negócio ou orquestração dentro de models
**Sinais de detecção**
- Funções de acesso a dados que também decidem regras (checar saldo ou disponibilidade e debitar, aplicar desconto por faixa, disparar notificação).
- Models que chamam outros models em sequência para montar um fluxo.

**Por que importa:** mistura persistência com decisão de negócio; muda a regra, muda a camada de dados.

### AP-10 — Estado global mutável / conexão compartilhada
**Sinais de detecção**
- Variáveis de módulo reatribuídas (`global x`, `let cache = {}` exportado e mutado).
- Uma conexão de banco única para todas as requisições (conexão criada no import e reutilizada; flags que desligam a checagem de thread do driver).
- Contadores ou caches globais sem dono.

**Por que importa:** condições de corrida, testes que interferem entre si, comportamento imprevisível sob concorrência.

### AP-11 — Acoplamento forte sem injeção de dependência
**Sinais de detecção**
- Classes que instanciam suas dependências internamente (`new Database(...)`, `smtplib.SMTP(...)`, `new PaymentGateway()` dentro do construtor ou do handler).
- Controllers importando e usando diretamente o driver do banco, pulando a camada de model.
- Configuração importada de um módulo global em vez de recebida.

**Por que importa:** impossível substituir por mocks nos testes ou trocar a implementação.

### AP-12 — Operação multi-etapa sem transação
**Sinais de detecção**
- Sequências de `INSERT`/`UPDATE` dependentes (cabeçalho + itens + atualização de saldo; cadastro + cobrança) sem `BEGIN/COMMIT/ROLLBACK`, `session.begin()` ou `db.transaction`.
- Efeitos colaterais gravados antes de uma validação que pode falhar (registro criado antes de uma etapa posterior ser recusada).

**Por que importa:** uma falha no meio deixa o banco inconsistente (registros órfãos, estoque errado).

### AP-13 — Callback hell / fluxo assíncrono sem controle de erro
**Sinais de detecção**
- Três ou mais níveis de callbacks aninhados.
- Callbacks `(err, ...)` que ignoram `err`.
- Promises sem `catch`, handlers `async` sem `try/catch` num framework que não repassa rejeições ao error handler.
- Operações que podem lançar exceção (`.startsWith`, `.length`, `JSON.parse`) sobre input não validado, derrubando o processo.

**Ajuste:** CRITICAL se um único request malformado derruba o servidor.
**Por que importa:** erros silenciosos, fluxos que param no meio, processo que cai.

### AP-14 — Camada morta ou duplicada
**Sinais de detecção**
- Services, helpers, validadores ou métodos de model que existem e nunca são chamados (confirme com busca pelo nome).
- Dependências declaradas e nunca importadas.
- Rotas que reimplementam o que um método do model já faz.

**Ajuste:** MEDIUM se o código morto é pequeno e isolado; HIGH quando a lógica "oficial" existe e é ignorada, gerando duas fontes de verdade.
**Por que importa:** a estrutura promete uma arquitetura que o código não segue.

---

## MEDIUM

### AP-15 — Queries N+1 e agregações ineficientes
**Sinais de detecção**
- Query dentro de loop sobre o resultado de outra query (`for row in rows: cursor.execute(... row.id)`; `Model.query.get(x.id)` por item).
- Acesso lazy a relacionamentos dentro de loop (`len(parent.children)` para cada registro).
- Vários `COUNT`/`SUM` separados que um `GROUP BY` resolveria.

**Por que importa:** o número de queries cresce com os dados; lentidão progressiva.

### AP-16 — Tratamento de erro ausente, genérico ou disperso
**Sinais de detecção**
- `except:` sem tipo, `except Exception` que devolve `str(e)`, `catch (e) {}` vazio.
- `try/except` repetido em cada handler em vez de um handler central (`@app.errorhandler`, middleware de erro do Express).
- Respostas de erro com formatos diferentes (texto puro × JSON; chaves diferentes).
- Status errado (sucesso quando nada foi alterado; 404 para qualquer erro).

**Por que importa:** bugs escondidos, contrato de erro imprevisível para o cliente.

### AP-17 — Validação de entrada ausente ou inconsistente
**Sinais de detecção**
- Campos do body usados sem checar presença, tipo ou formato (e-mail, datas, números negativos).
- Validação num endpoint e ausente no endpoint equivalente (POST valida, PUT não).
- `body.get(...)` com body possivelmente nulo.
- Tipos errados gerando 500 em vez de 400.

**Por que importa:** dados inválidos no banco e erros 500 no lugar de respostas 400 claras.

### AP-18 — Código duplicado
**Sinais de detecção**
- Blocos quase idênticos (mesma query ou mesmo mapeamento row → dict em vários lugares).
- A mesma regra ou lista de valores válidos repetida em vários arquivos.

**Por que importa:** um bug corrigido num lugar continua nos outros.

### AP-19 — Uso de API deprecated ou legada
Compare o código com a versão instalada das dependências. Rode a aplicação com warnings ativos quando possível (`python -W default`, `node --trace-deprecation`) e registre o que aparece.

| Ecossistema | Deprecated / legado | Equivalente moderno |
|---|---|---|
| Python | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| Python | adapters padrão de datetime do `sqlite3` (deprecated no 3.12) | registrar adapters/converters explícitos ou gravar ISO 8601 |
| Python | `pkg_resources`, `imp`, `distutils`, `asyncio.get_event_loop()` fora de loop | `importlib.metadata`/`importlib.resources`, `importlib`, `setuptools`, `asyncio.run()` |
| SQLAlchemy 2.x | `Model.query.get(id)` (`LegacyAPIWarning`) | `db.session.get(Model, id)` ou `db.get_or_404(Model, id)` |
| SQLAlchemy 2.x | `Model.query.filter(...).all()` (estilo 1.x) | `db.session.execute(db.select(Model).where(...)).scalars().all()` |
| SQLAlchemy 2.x | `relationship(..., backref=...)`, `Column` sem tipagem | `back_populates`, `Mapped[...]` + `mapped_column()` |
| Flask | `@app.before_first_request` (removido no 2.3) | executar na criação da app (`create_app`) ou `with app.app_context()` |
| Flask | `flask.json.JSONEncoder`, `app.json_encoder`, `FLASK_ENV` | `app.json` (`DefaultJSONProvider`), `FLASK_DEBUG` |
| Flask/Werkzeug | `safe_str_cmp`, `werkzeug.contrib.*` | `hmac.compare_digest`, pacotes dedicados |
| Node.js | `new Buffer(x)` | `Buffer.from(x)` / `Buffer.alloc(n)` |
| Node.js | `url.parse()`, `querystring` | `new URL()`, `URLSearchParams` |
| Node.js | `fs.exists`, callbacks de `fs` | `fs.existsSync` / `fs.promises` (`node:fs/promises`) |
| Node.js | `crypto.createCipher`, hash caseiro de senha | `crypto.createCipheriv`, `crypto.scrypt` / `bcrypt` |
| Node.js | driver `sqlite3` baseado em callbacks | `node:sqlite` (Node ≥ 22.5), `better-sqlite3` ou wrapper com promises + `async/await` |
| Express | `body-parser` separado | `express.json()` / `express.urlencoded()` |
| Express | `res.send(status, body)`, `res.json(status, body)`, `req.param()` | `res.status(s).send(body)`, `req.params` / `req.query` / `req.body` |
| Express 4 | handlers `async` sem repasse de erro | Express 5 (repasse automático) ou wrapper `asyncHandler` |
| JavaScript | `var`, `self = this` com `function()` | `const`/`let`, arrow functions, `async/await` |

**Ajuste:** HIGH se a API já foi **removida** na versão instalada e o código quebra; LOW se é só estilo legado sem aviso da ferramenta.
**Por que importa:** quebra em futuras atualizações e esconde warnings importantes no log.

### AP-20 — Logging com print/console e sem níveis
**Sinais de detecção**
- `print(...)`, `console.log(...)` para eventos da aplicação, erros ou "envio de e-mail" simulado.
- Nenhum uso de `logging`/logger estruturado.

**Ajuste:** se o log contém dado sensível, o finding é AP-03 (CRITICAL).
**Por que importa:** sem níveis nem destino configurável; ruído em produção.

### AP-21 — Middleware ou configuração HTTP inadequada
**Sinais de detecção**
- CORS liberado para qualquer origem (`CORS(app)`, `cors()` sem opções) numa API sem autenticação.
- Porta, host e caminho do banco fixos no código, com caminho relativo ao diretório de execução.
- Schema/seed executados como efeito colateral do import.

**Por que importa:** superfície de ataque maior e aplicação que se comporta diferente conforme de onde é executada.

---

## LOW

### AP-22 — Magic numbers e strings
**Sinais de detecção:** números e strings com significado de negócio soltos no código (faixas de desconto, limites de tamanho, prioridades, status como string literal repetida, prefixos ou dígitos com significado especial, portas).
**Por que importa:** a regra fica implícita e se espalha.

### AP-23 — Nomes ruins
**Sinais de detecção:** variáveis de uma ou duas letras fora de laços curtos (`x`, `v`, `tmp`, `a1`), nomes que sombreiam builtins (`id`, `type`, `list`), nomes genéricos ou numerados (`data2`, `result3`, `Manager`, `utils`), funções quase homônimas com papéis diferentes.
**Por que importa:** leitura lenta e erros por confusão.

### AP-24 — Imports, variáveis e funções não usados
**Sinais de detecção:** imports sem uso, parâmetros ignorados, variáveis exportadas nunca lidas, funções utilitárias sem chamadas.
**Por que importa:** ruído que confunde sobre o que o código realmente faz.

---

## Como registrar um finding

- **Um finding por problema**, com **todas** as linhas afetadas (`models.py:28, 48-49, 110`).
- Cite um trecho curto do código problemático na descrição.
- Se o mesmo trecho viola dois anti-patterns, registre os dois apenas se as correções forem diferentes.
- Marque findings de APIs deprecated com `[DEPRECATED]` no título.
