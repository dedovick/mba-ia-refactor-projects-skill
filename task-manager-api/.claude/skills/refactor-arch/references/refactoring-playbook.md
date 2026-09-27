# Playbook de Refatoração

Use este playbook na **Fase 3**. Cada transformação resolve um ou mais anti-patterns do catálogo (`AP-xx`) e traz código antes/depois em Python e/ou JavaScript. Os exemplos usam um domínio neutro (contas, faturas, itens): adapte nomes, framework e estilo ao projeto real.

| ID | Transformação | Resolve |
|---|---|---|
| T-01 | Extrair configuração e segredos para o ambiente | AP-01, AP-07, AP-21 |
| T-02 | Parametrizar queries | AP-02 |
| T-03 | Quebrar God Class/Module em camadas | AP-05 |
| T-04 | Mover regra de negócio da rota/model para controller/service | AP-08, AP-09, AP-14, AP-18 |
| T-05 | Injetar dependências e eliminar estado global | AP-10, AP-11 |
| T-06 | Hash seguro de senha | AP-04 |
| T-07 | Presenter com whitelist e logs sem dados sensíveis | AP-03 |
| T-08 | Eliminar N+1 com JOIN/agregação | AP-15 |
| T-09 | Centralizar tratamento de erros | AP-16 |
| T-10 | Callbacks → async/await com transação | AP-12, AP-13 |
| T-11 | Validação de entrada numa camada única | AP-17, AP-18 |
| T-12 | Migrar APIs deprecated | AP-19 |
| T-13 | Constantes, nomes claros e remoção de código morto | AP-22, AP-23, AP-24 |
| T-14 | Logging estruturado no lugar de print/console | AP-20 |
| T-15 | Proteger endpoints administrativos | AP-06 |
| T-16 | Composition root (entry point) preservando o comando | AP-05, AP-21 |
| T-17 | Substituir condicionais em cadeia por dados, despacho ou expressão | AP-25 |
| T-18 | Reorganizar módulos por domínio (coesão) | AP-26 |

---

## T-01 — Extrair configuração e segredos para o ambiente

**Antes (Python)**
```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-fixa-123"
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Depois (Python)**
```python
# src/config/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "app.db"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
```
```dotenv
# .env.example — sem valores reais
SECRET_KEY=
FLASK_DEBUG=false
PORT=5000
DATABASE_PATH=
CORS_ORIGINS=http://localhost:3000
```

**Antes (JavaScript)**
```js
module.exports = { dbPass: "senha_prod", gatewayKey: "pk_live_abc", port: 3000 };
```

**Depois (JavaScript)**
```js
// src/config/index.js
module.exports = Object.freeze({
  port: Number(process.env.PORT) || 3000,
  gatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  db: { filename: process.env.DB_FILENAME || ":memory:" },
});
```

Regras: o default de desenvolvimento nunca é um segredo real; o caminho do banco é absoluto (baseado no arquivo, não no diretório atual); debug desligado por padrão; se o projeto já depende de `python-dotenv`/`dotenv`, carregue o `.env` no entry point.

---

## T-02 — Parametrizar queries

**Antes**
```python
cursor.execute("SELECT * FROM accounts WHERE login = '" + login + "'")
cursor.execute(f"UPDATE items SET qty = {qty} WHERE id = {item_id}")
```

**Depois**
```python
cursor.execute("SELECT * FROM accounts WHERE login = ?", (login,))
cursor.execute("UPDATE items SET qty = ? WHERE id = ?", (qty, item_id))
```

Filtros dinâmicos: monte só a estrutura com trechos fixos e passe os valores separados.
```python
clauses, params = [], []
if term:
    clauses.append("(name LIKE ? OR description LIKE ?)")
    params += [f"%{term}%", f"%{term}%"]
if min_price is not None:
    clauses.append("price >= ?")
    params.append(min_price)
sql = "SELECT * FROM items" + (" WHERE " + " AND ".join(clauses) if clauses else "")
cursor.execute(sql, params)
```

**JavaScript**
```js
// Antes
db.get(`SELECT * FROM accounts WHERE email = '${email}'`, cb);
// Depois
db.get("SELECT * FROM accounts WHERE email = ?", [email], cb);
```

---

## T-03 — Quebrar God Class/Module em camadas

**Antes**
```js
class Core {
  constructor() { this.db = new sqlite3.Database(":memory:"); }
  initDb() { /* CREATE TABLE ... seed ... */ }
  setupRoutes(app) {
    app.post("/api/invoices", (req, res) => {
      /* valida, consulta, calcula, grava, responde */
    });
  }
}
```

**Depois**
```
src/database/connection.js   → cria e exporta a conexão (recebe config)
src/database/schema.js       → CREATE TABLE + seed
src/models/invoiceModel.js   → queries da entidade
src/controllers/invoiceController.js → fluxo do caso de uso
src/views/routes.js          → app.post("/api/invoices", controller.create)
src/app.js                   → monta tudo
```

Passos: (1) liste as responsabilidades do arquivo; (2) crie um módulo por responsabilidade e por domínio; (3) mova o código sem mudar comportamento; (4) ajuste imports; (5) apague o arquivo original quando estiver vazio.

---

## T-04 — Mover regra de negócio para controller/service

**Antes (rota gorda)**
```python
@bp.route("/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json()
    if not data.get("customer_id"):
        return jsonify({"error": "customer_id obrigatório"}), 400
    total = 0
    for item in data["items"]:
        row = db.execute("SELECT price FROM items WHERE id = ?", (item["id"],)).fetchone()
        total += row["price"] * item["qty"]
    if total > 1000:
        total *= 0.95
    cur = db.execute("INSERT INTO invoices (customer_id, total) VALUES (?, ?)",
                     (data["customer_id"], total))
    db.commit()
    return jsonify({"id": cur.lastrowid, "total": total}), 201
```

**Depois**
```python
# src/views/invoice_routes.py — só HTTP
@bp.route("/invoices", methods=["POST"])
def create_invoice():
    invoice = invoice_controller.create(request.get_json(silent=True) or {})
    return jsonify(present_invoice(invoice)), 201

# src/controllers/invoice_controller.py — fluxo e regra
DISCOUNT_THRESHOLD = 1000
DISCOUNT_RATE = 0.05

def create(data):
    validate_invoice_payload(data)                    # lança ValidationError → 400
    total = sum(item_model.price_of(i["id"]) * i["qty"] for i in data["items"])
    if total > DISCOUNT_THRESHOLD:
        total *= 1 - DISCOUNT_RATE
    return invoice_model.create(customer_id=data["customer_id"], total=total)

# src/models/invoice_model.py — só dados
def create(customer_id, total):
    db = get_db()
    cur = db.execute("INSERT INTO invoices (customer_id, total) VALUES (?, ?)", (customer_id, total))
    db.commit()
    return {"id": cur.lastrowid, "customer_id": customer_id, "total": total}
```

Quando a regra já existe em outro lugar (um método do model ou um helper não usado), **reutilize-o** e apague as cópias.

---

## T-05 — Injetar dependências e eliminar estado global

**Antes (Python)**
```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("app.db", check_same_thread=False)
    return db_connection
```

**Depois (Python — conexão por requisição)**
```python
# src/database/connection.py
import sqlite3
from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
```

**Antes (JavaScript)**
```js
class SubscriptionController {
  constructor() { this.gateway = new FakeGateway(); this.db = new sqlite3.Database(":memory:"); }
}
```

**Depois (JavaScript)**
```js
class SubscriptionController {
  constructor({ accountModel, invoiceModel, paymentGateway }) {
    this.accountModel = accountModel;
    this.invoiceModel = invoiceModel;
    this.paymentGateway = paymentGateway;
  }
}
// src/app.js (composition root)
const controller = new SubscriptionController({ accountModel, invoiceModel, paymentGateway });
```

Caches globais mutáveis: se nada lê o cache, remova-o; se é necessário, transforme em um objeto criado no entry point e injetado.

---

## T-06 — Hash seguro de senha

**Antes**
```python
user.password = hashlib.md5(password.encode()).hexdigest()
# ou senha em texto puro: INSERT INTO accounts (pwd) VALUES ('<senha>')
```

**Depois (Python, Werkzeug já vem com o Flask)**
```python
from werkzeug.security import generate_password_hash, check_password_hash

password_hash = generate_password_hash(password)          # scrypt/pbkdf2 com salt
ok = check_password_hash(stored_hash, password_informada)
```

**Depois (Node.js, sem dependência extra)**
```js
const crypto = require("node:crypto");

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(password, salt, 64).toString("hex");
  return `${salt}:${hash}`;
}
function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(":");
  const candidate = crypto.scryptSync(password, salt, 64);
  return crypto.timingSafeEqual(Buffer.from(hash, "hex"), candidate);
}
```

Atualize o seed para gravar hashes e verifique que o login com as credenciais do seed continua funcionando. Remova senhas padrão (`password || "123456"`): senha ausente é erro de validação.

**Conta existente reutilizada num fluxo (AP-06, identidade não verificada)**

```js
// Antes: quem informar um e-mail já cadastrado age em nome daquela conta
const existing = await accountModel.findByEmail(input.email);
const accountId = existing ? existing.id : await accountModel.create(input);

// Depois: a conta existente só é usada com a credencial correta
const existing = await accountModel.findByEmail(input.email);
if (existing && !verifyPassword(input.password ?? "", existing.passwordHash)) {
  throw new AppError("Credenciais inválidas", 401);     // nada é gravado
}
const accountId = existing ? existing.id : await accountModel.create(input);
```

Faça a verificação **antes** de qualquer efeito colateral (cobrança, gravação). A resposta nova (401) é uma correção de segurança: liste-a em "Contract changes".

---

## T-07 — Presenter com whitelist e logs sem dados sensíveis

**Antes**
```python
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password}
```
```js
console.log(`Cobrando cartão ${cardNumber} com a chave ${config.gatewayKey}`);
```

**Depois**
```python
# src/views/presenters.py
PUBLIC_ACCOUNT_FIELDS = ("id", "name", "email", "role", "created_at")

def present_account(account):
    return {field: account[field] for field in PUBLIC_ACCOUNT_FIELDS if field in account}
```
```js
const masked = `**** **** **** ${String(cardNumber).slice(-4)}`;
logger.info(`Processando pagamento com cartão ${masked}`);
```

Endpoints de health/info devolvem só estado (`{"status": "ok", "database": "connected"}`), nunca configuração. Registre a remoção de campos na seção "Contract changes".

---

## T-08 — Eliminar N+1 com JOIN/agregação

**Antes**
```python
invoices = db.execute("SELECT * FROM invoices").fetchall()
for inv in invoices:
    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (inv["id"],)).fetchall()
    for it in items:
        name = db.execute("SELECT name FROM items WHERE id = ?", (it["item_id"],)).fetchone()
```

**Depois**
```python
rows = db.execute("""
    SELECT inv.id AS invoice_id, inv.total, ii.qty, ii.unit_price, i.name AS item_name
    FROM invoices inv
    LEFT JOIN invoice_items ii ON ii.invoice_id = inv.id
    LEFT JOIN items i ON i.id = ii.item_id
    ORDER BY inv.id
""").fetchall()
# agrupe em Python por invoice_id mantendo o mesmo formato de resposta de antes
```

ORM (SQLAlchemy):
```python
# Antes: for t in tasks: owner = User.query.get(t.user_id)
# Depois:
stmt = db.select(Task).options(selectinload(Task.owner))
tasks = db.session.execute(stmt).scalars().all()
```

Contagens: troque vários `COUNT` separados por um `SELECT status, COUNT(*) ... GROUP BY status`.

---

## T-09 — Centralizar tratamento de erros

**Antes**
```python
def get_item(item_id):
    try:
        ...
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Depois (Flask)**
```python
# src/middlewares/error_handler.py
class AppError(Exception):
    status = 500
    def __init__(self, message, status=None):
        super().__init__(message)
        self.message = message
        if status:
            self.status = status

class ValidationError(AppError): status = 400
class NotFoundError(AppError): status = 404

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"error": err.message}), err.status  # use as MESMAS chaves de erro que o projeto já usava

    @app.errorhandler(HTTPException)          # from werkzeug.exceptions import HTTPException
    def handle_http_error(err):               # 404, 405 etc. mantêm o status original
        return jsonify({"error": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Erro inesperado")
        return jsonify({"error": "Erro interno do servidor"}), 500
```

> Registre um handler para `HTTPException` **antes** de confiar no handler genérico de `Exception`; sem ele, um 405 do próprio framework vira 500.

**Depois (Express)**
```js
// src/middlewares/asyncHandler.js
module.exports = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// src/middlewares/errorHandler.js
class AppError extends Error { constructor(message, status = 500) { super(message); this.status = status; } }
function errorHandler(err, req, res, _next) {
  if (err instanceof AppError) return res.status(err.status).send(err.message);  // mesmo formato de antes
  console.error(err);
  return res.status(500).send("Erro interno");
}
module.exports = { AppError, errorHandler };
// app.js: app.use(errorHandler) — sempre por último
```

---

## T-10 — Callbacks → async/await com transação

**Antes**
```js
db.get("SELECT * FROM plans WHERE id = ?", [planId], (err, plan) => {
  db.run("INSERT INTO accounts ...", [], function (err) {
    const accountId = this.lastID;
    db.run("INSERT INTO subscriptions ...", [accountId, planId], function (err) {
      db.run("INSERT INTO charges ...", [this.lastID], (err) => res.json({ ok: true }));
    });
  });
});
```

**Depois**
```js
// src/database/connection.js — helpers com Promise sobre o driver existente
const run = (db, sql, params = []) => new Promise((resolve, reject) =>
  db.run(sql, params, function (err) { err ? reject(err) : resolve({ lastID: this.lastID, changes: this.changes }); }));
const get = (db, sql, params = []) => new Promise((resolve, reject) =>
  db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row))));

async function transaction(db, work) {
  await run(db, "BEGIN");
  try { const result = await work(); await run(db, "COMMIT"); return result; }
  catch (err) { await run(db, "ROLLBACK"); throw err; }
}

// src/controllers/subscriptionController.js
async subscribe(input) {
  const plan = await this.planModel.findById(input.planId);
  if (!plan) throw new AppError("Plano não encontrado", 404);
  const approved = await this.paymentGateway.charge(input.card, plan.price);   // decide antes de gravar
  if (!approved) throw new AppError("Cobrança recusada", 402);
  return transaction(this.db, async () => {
    const accountId = await this.accountModel.findOrCreate(input);
    const subscriptionId = await this.subscriptionModel.create(accountId, plan.id);
    await this.chargeModel.create(subscriptionId, plan.price, "PAID");
    return subscriptionId;
  });
}
```

Python (sqlite3): use `with conn:` para commit/rollback automático do bloco; com SQLAlchemy, `with db.session.begin():`.

> Mudou a ordem dos efeitos colaterais (ex.: não gravar nada quando o pagamento é recusado)? É correção de bug; registre no resumo final.

---

## T-11 — Validação de entrada numa camada única

**Antes**
```python
# POST valida, PUT não; tipos errados viram 500
if data["price"] < 0: ...
```

**Depois**
```python
# src/controllers/validators.py
def require_fields(data, *fields):
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Campos obrigatórios: {', '.join(missing)}")

def require_number(data, field, minimum=None):
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} deve ser numérico")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{field} deve ser >= {minimum}")
    return value
```
```js
function requireString(value, field) {
  if (typeof value !== "string" || value.trim() === "") throw new AppError(`${field} inválido`, 400);
  return value.trim();
}
```

Reutilize as mesmas funções em todos os endpoints equivalentes (criar e atualizar). Mantenha as mensagens de erro que o projeto já tinha quando elas fazem parte do contrato.

---

## T-12 — Migrar APIs deprecated

```python
# Antes
from datetime import datetime
created_at = db.Column(db.DateTime, default=datetime.utcnow)
task = Task.query.get(task_id)
# Depois
from datetime import datetime, timezone
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
task = db.session.get(Task, task_id)
```
```js
// Antes
const buf = new Buffer(text);
const { query } = url.parse(req.url, true);
// Depois
const buf = Buffer.from(text);
const { searchParams } = new URL(req.url, "http://localhost");
```

Depois de migrar, suba a aplicação com warnings ativos e confirme que eles sumiram. Cuidado com comparações de datas: se passar a gravar datetimes com timezone, compare com valores também com timezone.

---

## T-13 — Constantes, nomes claros e remoção de código morto

**Antes**
```python
if total > 10000: discount = total * 0.1
elif total > 5000: discount = total * 0.05
def f(u, e, cc): ...
import os, sys, json   # nenhum usado
```

**Depois**
```python
DISCOUNT_TIERS = ((10_000, 0.10), (5_000, 0.05))

def discount_for(total):
    return next((total * rate for limit, rate in DISCOUNT_TIERS if total > limit), 0)

def charge(user_name, email, card_number): ...
```

Remova imports, variáveis e funções sem uso (confirme com busca antes de apagar). Status e papéis viram constantes (ou `Enum`) num único lugar.

---

## T-14 — Logging estruturado

**Antes**
```python
print("ENVIANDO EMAIL para " + email)
```
```js
console.log("Fatura criada", id);
```

**Depois**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Notificação enviada", extra={"account_id": account_id})
```
```js
// src/config/logger.js
const logger = { info: (...a) => console.info("[info]", ...a), error: (...a) => console.error("[error]", ...a) };
module.exports = logger;
```

Nunca registre senhas, tokens, números de cartão completos ou chaves (veja T-07).

---

## T-15 — Proteger endpoints administrativos

**Antes**
```python
@app.route("/admin/reset", methods=["POST"])
def reset():
    db.execute("DELETE FROM accounts")
```

**Depois**
```python
# src/middlewares/auth.py
import hmac
from functools import wraps
from flask import current_app, request

def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        provided = request.headers.get("X-Admin-Token", "")
        if not expected or not hmac.compare_digest(provided, expected):
            raise UnauthorizedError("Não autorizado")        # 401 pelo handler central
        return view(*args, **kwargs)
    return wrapper
```
```js
function requireAdmin(config) {
  return (req, res, next) => {
    const token = req.get("X-Admin-Token");
    if (!config.adminToken || token !== config.adminToken) return res.status(401).send("Não autorizado");
    next();
  };
}
```

Um endpoint que executa SQL arbitrário do cliente não deve continuar existindo como tal: remova-o ou restrinja-o a leitura por trás de `require_admin`, e documente a decisão em "Contract changes". O token vem da config (T-01) e fica em branco no `.env.example`.

---

## T-16 — Composition root preservando o comando de execução

**Depois (Flask)**
```python
# src/app.py
def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app, origins=settings.CORS_ORIGINS)
    database.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(item_routes.bp)
    app.register_blueprint(account_routes.bp)
    with app.app_context():
        seed.init_db()
    return app

# app.py (raiz) — o mesmo comando de antes: python app.py
from src.app import create_app
from src.config.settings import Settings

app = create_app()

if __name__ == "__main__":
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
```

**Depois (Express)**
```js
// src/app.js
function createApp({ config, db }) {
  const app = express();
  app.use(express.json());
  app.use(buildRoutes({ config, db }));
  app.use(errorHandler);
  return app;
}
module.exports = { createApp };

// src/server.js
const config = require("./config");
const { createDatabase } = require("./database/connection");
const { createApp } = require("./app");

(async () => {
  const db = await createDatabase(config);        // schema + seed aguardados antes do listen
  createApp({ config, db }).listen(config.port, () => console.info(`Servidor na porta ${config.port}`));
})();
// package.json: "start": "node src/server.js"
```

---

## T-17 — Substituir condicionais em cadeia por dados, despacho ou expressão

Escolha a técnica pelo **tipo** de condicional (veja AP-25). Trocar `if/elif` por `switch` só ajuda no caso "b".

### T-17a — Faixas → tabela de dados

**Antes**
```python
fee = 0
if amount > 10000:
    fee = amount * 0.01
elif amount > 5000:
    fee = amount * 0.02
elif amount > 1000:
    fee = amount * 0.03
```

**Depois**
```python
FEE_TIERS = ((10_000, 0.01), (5_000, 0.02), (1_000, 0.03))   # (limite exclusivo, taxa), do maior para o menor

def fee_for(amount):
    return next((amount * rate for limit, rate in FEE_TIERS if amount > limit), 0)
```
```js
const FEE_TIERS = [[10_000, 0.01], [5_000, 0.02], [1_000, 0.03]];
const feeFor = (amount) => {
  const tier = FEE_TIERS.find(([limit]) => amount > limit);
  return tier ? amount * tier[1] : 0;
};
```
Preserve exatamente os limites (`>` × `>=`) e a ordem de avaliação do código original.

### T-17b — Valor → ação: tabela de despacho, `match`/`switch` ou Strategy

**Antes**
```python
if new_state == "approved":
    notify_approval(ticket_id)
if new_state == "rejected":
    notify_rejection(ticket_id)
if new_state == "escalated":
    page_on_call(ticket_id)
```

**Depois — tabela de despacho (preferida quando cada caso é uma chamada)**
```python
ON_STATE_CHANGE = {
    "approved": notify_approval,
    "rejected": notify_rejection,
    "escalated": page_on_call,
}

if handler := ON_STATE_CHANGE.get(new_state):
    handler(ticket_id)
```

**Depois — `match` (Python ≥ 3.10) / `switch` (JS), quando os casos têm lógica diferente entre si**
```python
match new_state:
    case "approved":
        notify_approval(ticket_id)
    case "rejected" | "escalated":
        notify_team(ticket_id, new_state)
    case _:
        pass
```
```js
switch (newState) {
  case "approved": notifyApproval(ticketId); break;
  case "rejected":
  case "escalated": notifyTeam(ticketId, newState); break;
  default: break;
}
```
Use `match` só se a versão mínima de Python do projeto for 3.10 ou superior. Quando cada caso cresce (várias etapas, dependências próprias), promova para Strategy: uma classe ou função por caso, registrada no mesmo dicionário.

### T-17c — `if` aninhado retornando booleano → expressão ou guard clauses

**Antes**
```python
def is_expired(self):
    if self.expires_at:
        if self.expires_at < now():
            if self.state != "closed" and self.state != "archived":
                return True
            else:
                return False
        else:
            return False
    else:
        return False
```

**Depois**
```python
FINAL_STATES = frozenset({"closed", "archived"})

def is_expired(self, reference=None):
    reference = reference or now()
    return bool(self.expires_at) and self.expires_at < reference and self.state not in FINAL_STATES
```

Quando a condição tem efeitos ou mensagens diferentes por ramo, use guard clauses (retorno antecipado) em vez de aninhar:
```python
def cancel(ticket):
    if ticket is None:
        raise NotFoundError("Chamado não encontrado")
    if ticket.state in FINAL_STATES:
        raise ValidationError("Chamado já encerrado")
    ticket.state = "cancelled"
```

Se a mesma regra aparece em vários lugares, crie **um** método (no model ou no service) e substitua todas as cópias por chamadas a ele.

---

## T-18 — Reorganizar módulos por domínio (coesão)

**Antes**
```
handlers/
├── account_handlers.py
└── analytics_handlers.py # métricas + CRUD completo de "labels" (outro domínio)
common/
└── misc.py               # valida e-mail, formata data, calcula juros, constantes de status
```

**Depois**
```
views/
├── account_routes.py
├── analytics_routes.py   # só métricas
└── label_routes.py       # CRUD de labels no módulo do seu domínio
controllers/
├── analytics_controller.py
└── label_controller.py
models/
└── constants.py          # status e limites do domínio
controllers/validators.py # validações de entrada reutilizadas
```

Passos:
1. Para cada arquivo, liste as entidades e os paths de rota que ele manipula. Tudo o que não pertence ao domínio do nome do arquivo é candidato a mudar de lugar.
2. Mova cada recurso para o módulo do seu domínio **sem mudar o path das rotas** (o contrato não muda por causa da organização interna).
3. Quebre `utils`/`helpers` genéricos por assunto: validação → `validators`, formatação de resposta → `views/presenters`, regras de negócio → `controllers`/`services`, constantes → `constants` do domínio. O que não é usado em lugar nenhum é removido (T-13).
4. Atualize os imports e o registro de rotas (blueprints/routers) no entry point.

```python
# src/app.py — o registro deixa explícito cada domínio
app.register_blueprint(account_routes.bp)
app.register_blueprint(analytics_routes.bp)
app.register_blueprint(label_routes.bp)    # antes escondido dentro de analytics_handlers
```

