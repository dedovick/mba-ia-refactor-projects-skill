# Validação — Linha de Base e Verificação Pós-Refatoração

A skill só pode dizer que "a aplicação funciona" com evidência. Esta referência define como subir a aplicação e como comparar o comportamento **antes** (Fase 1) e **depois** (Fase 3), sem sujar o repositório.

## Princípios

- **Sempre numa cópia temporária**, fora do projeto: bancos, `node_modules`, venvs e arquivos gerados ficam lá.
- **Mesma sequência de requisições antes e depois**, partindo de um banco no estado inicial (seed recém-aplicado), para que ids e contagens coincidam.
- **Porta livre**, nunca assumida. Em macOS a 5000 costuma estar ocupada pelo AirPlay Receiver.
- **Nunca deixe processos rodando**: registre o PID e encerre ao final, mesmo em caso de falha.

## 1. Preparar a cópia

```bash
PROJECT_DIR="$(pwd)"
NAME="$(basename "$PROJECT_DIR")"
STAGE=baseline                                     # baseline (Fase 1) | after (Fase 3)
WORK="${TMPDIR:-/tmp}/refactor-arch-$NAME-$STAGE"
rm -rf "$WORK" && mkdir -p "$WORK"
rsync -a --exclude .git --exclude .claude --exclude node_modules --exclude venv --exclude .venv \
      --exclude __pycache__ --exclude '*.db' --exclude instance --exclude reports "$PROJECT_DIR/" "$WORK/"
```

Se `rsync` não existir, use `cp -R` e apague os mesmos itens depois.

## 2. Instalar dependências (na cópia)

| Stack | Comando |
|---|---|
| Python | `python3 -m venv "$WORK/.venv" && "$WORK/.venv/bin/pip" install -q -r "$WORK/requirements.txt"` (ou `pip install -e .` / `poetry install` conforme o manifesto) |
| Node.js | `(cd "$WORK" && npm install --silent)` (use `npm ci` se houver lockfile e a instalação limpa for possível) |
| Outras | o comando de instalação padrão do gerenciador detectado |

Rode os passos prévios do projeto (ex.: script de seed) exatamente como o README manda.

## 3. Escolher a porta e subir

```bash
PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()")
```

- Se a aplicação lê a porta do ambiente, passe `PORT=$PORT` (e as variáveis que ela exigir).
- Se a porta está **fixa no código** (situação típica na linha de base), altere o literal **apenas na cópia** (`sed` no arquivo da cópia) ou use um wrapper que importe a app e chame o servidor na porta escolhida. Nunca altere o projeto real na Fase 1.
- Suba em background, com o log em arquivo, e guarde o PID:

```bash
(cd "$WORK" && PORT=$PORT <comando de execução> > "$WORK/server.log" 2>&1 & echo $! > "$WORK/server.pid")
```

- Aguarde a aplicação responder (até ~30 s), consultando um endpoint GET simples:

```bash
for i in $(seq 1 30); do curl -s -o /dev/null "http://127.0.0.1:$PORT/<endpoint GET>" && break; sleep 1; done
```

- Para Python, suba com warnings visíveis (`python -W default ...`); para Node, `node --trace-deprecation ...` quando o script permitir. Guarde os warnings do log: eles entram na auditoria (APIs deprecated) e na comparação final.

## 4. Montar o plano de requisições

Use os endpoints da Fase 1. Para cada um, defina requisições nesta ordem, para que o estado do banco evolua igual antes e depois:

1. **Leituras** sem parâmetros (`GET /recurso`).
2. **Leituras** com parâmetro de rota, usando ids que o seed garante existir (e um id inexistente, para registrar o 404).
3. **Criações** (`POST`) com um corpo válido montado a partir do que o handler lê (ou dos exemplos do projeto: `*.http`, README, testes) **e** um corpo inválido/incompleto, para registrar o status de erro.
4. **Atualizações** (`PUT`/`PATCH`) com corpo válido.
5. **Remoções** (`DELETE`) de um recurso criado no passo 3 (preserve os dados do seed).
6. **Endpoints destrutivos ou administrativos** (reset, execução de comandos) por último. Se executá-los impediria o restante da validação, registre-os como "não executado — destrutivo" e apenas confirme que a rota existe.

Evite requisições que você sabe que derrubam o processo; se descobrir uma, registre o fato como finding e suba a aplicação de novo antes de continuar.

## 5. Registrar a resposta

Para cada requisição, registre: método, path, corpo enviado, **status**, tipo de conteúdo e **formato** da resposta (as chaves de primeiro nível do JSON; em listas, as chaves do primeiro item; em texto, os primeiros 80 caracteres).

```bash
curl -s -o "$WORK/resp.txt" -w "%{http_code} %{content_type}" -X POST "http://127.0.0.1:$PORT/<path>" \
     -H "Content-Type: application/json" -d '<corpo>'
```

Salve a tabela em `reports/baseline-endpoints.md` (Fase 1) com este formato:

```markdown
# Baseline — <projeto> (<data>)
Run command: <comando> | Port used: <porta> | Boot: OK | Warnings: <lista ou "nenhum">

| # | Request | Status | Response shape |
|---|---|---|---|
| 1 | GET /recurso | 200 | {dados: [id, nome, ...], sucesso} |
| 2 | GET /recurso/999 | 404 | {erro} |
| 3 | POST /recurso {"nome": "x"} | 201 | {dados: {id}, mensagem} |
```

## 6. Encerrar

```bash
kill "$(cat "$WORK/server.pid")" 2>/dev/null; sleep 1; kill -9 "$(cat "$WORK/server.pid")" 2>/dev/null
lsof -ti tcp:$PORT | xargs kill 2>/dev/null   # garante que a porta ficou livre
```

Apague `$WORK` ao final da fase (a linha de base já está salva em `reports/`).

---

## Validação pós-refatoração (Fase 3)

1. Prepare uma nova cópia (`after`) do projeto **já refatorado** e instale as dependências de novo (o manifesto pode ter mudado).
2. Rode os passos prévios (seed) e suba com o **mesmo comando de execução** de antes, agora passando a porta pelo ambiente (`PORT=$PORT`). Se isso não funcionar, a refatoração não terminou: a porta precisa ser configurável.
3. Confira o log de boot: nenhum erro, nenhum warning novo. Warnings de API deprecated que existiam antes devem ter sumido.
4. Execute **a mesma sequência** da linha de base e compare linha a linha:

| Resultado | Critério |
|---|---|
| ✓ Igual | Mesmo status e mesmas chaves de resposta |
| ✓ Mudança esperada | Diferença causada por uma correção de segurança listada em "Contract changes" (ex.: campo `password` removido, rota admin agora exige token → 401 sem token e o status original com token) |
| ✓ Correção de bug | Antes era 500 ou derrubava o processo; agora é 4xx com mensagem clara |
| ✗ Regressão | Qualquer outra diferença de status ou de formato — corrija antes de concluir |

5. Faça uma varredura rápida do catálogo nos arquivos novos (segredos, SQL concatenado, `except:` vazio, senha em resposta) para confirmar que os CRITICAL e HIGH foram resolvidos.
6. Salve o resultado em `reports/validation-results.md`: comando e porta usados, trecho do log de boot, tabela antes × depois com o veredito de cada linha e a lista de problemas não resolvidos.
7. Encerre o processo, libere a porta e apague a cópia temporária.
