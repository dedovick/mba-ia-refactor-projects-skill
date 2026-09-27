# Guidelines de Arquitetura — MVC Alvo

Use este guia na **Fase 3** para decidir a estrutura final e onde cada pedaço de código deve morar.

## 1. As camadas e suas responsabilidades

Numa API backend, o "V" do MVC é a **representação HTTP**: as rotas que recebem a requisição e os presenters/serializers que definem o formato da resposta.

| Camada | Responsabilidade | Pode | Não pode |
|---|---|---|---|
| **Config** | Ler configuração do ambiente e expor valores tipados | Ler variáveis de ambiente, definir defaults seguros para desenvolvimento | Conter segredos reais; ser alterada em runtime |
| **Database** | Criar e gerenciar conexões/sessões, schema e seed | Abrir/fechar conexão por requisição ou via pool, rodar migrations/seed | Conter regra de negócio |
| **Models** | Representar entidades e encapsular o acesso a dados | Queries **parametrizadas**, mapeamento linha → entidade, operações CRUD, transações de uma entidade | Conhecer HTTP (`request`, `res`), decidir regra de negócio, formatar resposta |
| **Services** *(opcional)* | Regra de negócio complexa ou compartilhada e integrações externas | Orquestrar vários models numa transação, falar com gateway de pagamento, e-mail, hashing | Conhecer HTTP |
| **Controllers** | Concentrar o **fluxo da aplicação** para cada caso de uso | Validar a entrada, chamar models/services, decidir o resultado, lançar erros de domínio | Escrever SQL, montar strings de resposta HTTP à mão, ler variáveis de ambiente |
| **Views / Routes** | Mapear HTTP ↔ controller e apresentar a resposta | Declarar paths e métodos, extrair params/body, chamar o controller, serializar com presenters, definir status code | Conter regra de negócio ou acesso a dados |
| **Middlewares** | Preocupações transversais | Tratamento central de erros, autenticação/autorização, logging de requisição, CORS configurado | Regra de negócio |
| **Entry point** | Composition root: montar tudo | Criar a app, carregar config, conectar banco, injetar dependências, registrar rotas e middlewares, iniciar o servidor | Conter lógica de rota ou de negócio |

**Services ou não?** Crie services quando a regra envolve mais de um model, precisa de transação entre entidades ou depende de algo externo (pagamento, e-mail). Para CRUD simples, o controller chama o model diretamente.

## 2. Regra de dependência

```
Entry point ──monta──▶ Routes/Views ──▶ Controllers ──▶ Services ──▶ Models ──▶ Database
                          │                                            ▲
                          └────────── Presenters (formato da resposta) │
Config ◀── lida por todos via injeção (nunca importada de dentro de models/controllers)
```

- As dependências apontam **para dentro**: rotas conhecem controllers, controllers conhecem services/models, models conhecem o banco. Nunca o contrário.
- Dependências externas (conexão, gateway, hasher, config) são **recebidas** por parâmetro, construtor ou factory, não instanciadas dentro da classe que as usa.
- Nenhuma camada abaixo das rotas importa objetos do framework HTTP.

## 3. Estrutura alvo por stack

Crie apenas as pastas que o projeto precisa, mas mantenha estes nomes para que a arquitetura seja reconhecível.

### Python / Flask

```
<projeto>/
├── app.py                     # launcher fino: from src.app import create_app; mantém `python app.py`
├── .env.example               # variáveis de ambiente documentadas, sem valores reais
├── requirements.txt
└── src/
    ├── __init__.py
    ├── app.py                 # create_app(): composition root
    ├── config/
    │   └── settings.py        # classe/objeto de config lendo os.environ
    ├── database/
    │   ├── connection.py      # conexão por requisição (g + teardown_appcontext) ou extensão do ORM
    │   └── seed.py            # criação de schema e dados iniciais (idempotente)
    ├── models/
    │   └── <entidade>_model.py
    ├── services/              # opcional
    │   └── <assunto>_service.py
    ├── controllers/
    │   └── <entidade>_controller.py
    ├── views/
    │   ├── <entidade>_routes.py   # Blueprint por domínio
    │   └── presenters.py          # serialização com whitelist de campos
    └── middlewares/
        ├── error_handler.py   # @app.errorhandler + exceções de domínio
        └── auth.py            # opcional: proteção de rotas administrativas
```

Se o projeto já tem um script auxiliar na raiz (ex.: seed), mantenha o mesmo nome e comando, apontando para a nova estrutura.

### Node.js / Express

```
<projeto>/
├── package.json               # "start" continua funcionando (atualize o caminho se o entry mudar)
├── .env.example
└── src/
    ├── server.js              # listen: lê a porta da config e inicia a app
    ├── app.js                 # createApp(deps): composition root
    ├── config/
    │   └── index.js           # process.env com defaults de desenvolvimento
    ├── database/
    │   ├── connection.js      # cria a conexão e expõe helpers com Promise
    │   └── schema.js          # schema + seed
    ├── models/
    │   └── <entidade>Model.js
    ├── services/              # opcional
    │   └── <assunto>Service.js
    ├── controllers/
    │   └── <entidade>Controller.js
    ├── views/
    │   ├── routes.js          # express.Router() registrando os endpoints
    │   └── presenters.js      # formato das respostas
    └── middlewares/
        ├── errorHandler.js    # (err, req, res, next) + classes de erro
        └── asyncHandler.js    # repassa rejeições de handlers async ao errorHandler
```

### Outras stacks

Mantenha as mesmas camadas com a convenção idiomática da linguagem (ex.: FastAPI com `routers/` como views e `Depends` para injeção; Spring com `@RestController` como view/controller fino e `@Service`/`@Repository`). Informe no resumo final como cada pasta mapeia para Model, View e Controller.

## 4. Onde cada coisa vai

| Código encontrado | Destino |
|---|---|
| `SECRET_KEY`, senhas, chaves, porta, host, caminho do banco, flags de debug | `config` (lidos do ambiente) + `.env.example` |
| Abertura de conexão, `CREATE TABLE`, seed | `database` |
| `SELECT/INSERT/UPDATE/DELETE`, chamadas ao ORM | `models` |
| Cálculos de domínio (totais, descontos, status, prazos), fluxos com várias entidades | `services` ou `controllers` |
| Validação de entrada e decisão do resultado de um caso de uso | `controllers` |
| Decoradores/registro de rotas, leitura de `request`/`req`, `jsonify`/`res.json`, status code | `views` (routes) |
| `to_dict()`, montagem do JSON de resposta, remoção de campos sensíveis | `views/presenters` |
| `try/except` repetidos, formatação de erro | `middlewares/error_handler` |
| Envio de e-mail, gateway de pagamento, hash de senha | `services` (injetados) |
| Constantes de negócio (status válidos, limites, faixas) | módulo de constantes do domínio (ex.: `models/constants`, `config/constants`) |

## 5. Contrato de erro

- Exceções de domínio (`ValidationError` → 400, `UnauthorizedError` → 401, `ForbiddenError` → 403, `NotFoundError` → 404, `ConflictError` → 409) são lançadas pelos controllers/services e convertidas em resposta pelo handler central.
- O corpo de erro mantém **o mesmo formato que o projeto já usava** (mesmas chaves e mensagens), para não quebrar clientes. Se o projeto não tinha padrão, use `{"error": "<mensagem>"}`.
- Erros inesperados → 500 com mensagem genérica; o detalhe vai para o log, nunca para o cliente.

## 6. Projetos que já têm camadas

1. Mantenha o que está correto (models ORM coesos, blueprints bem divididos).
2. Crie a camada que falta, em geral **controllers**: tire das rotas a validação, a regra e as queries.
3. Una duplicações: uma única fonte para regras repetidas (ex.: um método do model usado em todos os lugares).
4. Ative ou remova o código morto: um service não usado passa a ser injetado onde faz sentido, ou é removido.
5. Mova recursos para o módulo certo (uma rota que está no blueprint de outro domínio vai para o seu próprio).
6. Adicione o que é transversal e está faltando: config, error handler, app factory.

## 7. Checklist de conformidade

- [ ] Nenhum segredo ou valor de ambiente fixo no código; `.env.example` existe
- [ ] Models: todo acesso a dados, sempre parametrizado
- [ ] Views/Routes: só HTTP; nenhuma query, nenhum cálculo de domínio
- [ ] Controllers: concentram o fluxo; nenhum SQL
- [ ] Error handler central; nenhum `except:`/`catch` vazio espalhado
- [ ] Entry point único e claro (composition root)
- [ ] Dependências externas injetadas
- [ ] Mesmo comando de execução de antes
