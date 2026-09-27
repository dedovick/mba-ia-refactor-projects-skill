# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

Requer Node.js >= 22.13 (usa o módulo nativo `node:sqlite`).

```bash
npm install
ADMIN_TOKEN=troque-me npm start
```

A aplicação sobe em `http://localhost:3000` (ou na porta de `PORT`). O banco SQLite é em memória por padrão e carrega os seeds automaticamente no boot. As variáveis de ambiente estão documentadas em `.env.example`.

As rotas administrativas (`GET /api/admin/financial-report` e `DELETE /api/users/:id`) exigem o cabeçalho `X-Admin-Token` com o valor de `ADMIN_TOKEN`. Sem a variável, elas ficam bloqueadas.

No checkout, um e-mail já cadastrado só é aceito com a senha correta (`pwd`).

Exemplos de requisições estão em `api.http`.

## Estrutura

```
src/
├── server.js       # entry point: config, banco, seed e listen
├── app.js          # createApp(): composition root
├── config/         # variáveis de ambiente e logger
├── database/       # conexão node:sqlite, transação, schema e seed
├── models/         # acesso a dados por entidade e constantes do domínio
├── services/       # checkout, relatório, remoção de usuário, gateway e hash de senha
├── controllers/    # validação da entrada e fluxo de cada caso de uso
├── views/          # rotas Express e presenters (formato das respostas)
└── middlewares/    # erros centralizados e autorização administrativa
```
