# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

Requer Node.js >= 22.13 (usa o módulo nativo `node:sqlite`).

```bash
npm install
cp .env.example .env   # opcional: documenta as variáveis; exporte-as no shell
ADMIN_TOKEN=<token> npm start
```

A aplicação sobe em `http://localhost:3000` (ou na porta de `PORT`). Por padrão o banco SQLite é em memória (`DB_PATH=:memory:`) e carrega os seeds automaticamente no boot.

As rotas administrativas (`GET /api/admin/financial-report` e `DELETE /api/users/:id`) exigem o header `X-Admin-Token` igual a `ADMIN_TOKEN`; sem `ADMIN_TOKEN` configurado elas respondem `401`.

| Variável | Padrão | Uso |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DB_PATH` | `:memory:` | Caminho do banco SQLite |
| `PAYMENT_GATEWAY_KEY` | vazio | Chave do gateway de pagamento |
| `ADMIN_TOKEN` | vazio | Token das rotas administrativas |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warn` ou `error` |

## Estrutura

```
src/
├── server.js       # entry point: config, banco, listen
├── app.js          # composition root: injeta dependências e registra rotas
├── config/         # variáveis de ambiente
├── database/       # conexão, transação, schema e seed
├── models/         # acesso a dados por entidade (queries parametrizadas)
├── services/       # checkout, relatório financeiro, gateway de pagamento
├── controllers/    # validação de entrada e orquestração dos casos de uso
├── views/          # rotas Express e presenters (formato das respostas)
├── middlewares/    # autorização admin e tratamento central de erros
└── utils/          # logger e hash de senha
```

Exemplos de requisições estão em `api.http`.
