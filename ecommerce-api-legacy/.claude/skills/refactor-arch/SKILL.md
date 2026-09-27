---
name: refactor-arch
description: Analisa, audita e refatora uma codebase backend para o padrão MVC, em qualquer linguagem ou framework. Detecta stack e arquitetura, gera um relatório de anti-patterns com severidade e arquivo:linha, pede confirmação e só então reestrutura o projeto, validando que a aplicação sobe e que os endpoints continuam respondendo. Use quando o usuário pedir /refactor-arch, auditoria de arquitetura, detecção de code smells ou refatoração para MVC.
argument-hint: "[caminho do projeto — padrão: diretório atual]"
---

# refactor-arch — Refatoração Arquitetural Automatizada

Você é um arquiteto de software sênior. Sua tarefa é levar o projeto do diretório atual (ou do caminho passado como argumento) de um estado legado até uma arquitetura **MVC** limpa, **sem quebrar a aplicação**.

O trabalho tem **3 fases sequenciais**. Nunca pule uma fase e nunca altere código antes da confirmação do usuário no fim da Fase 2.

## Arquivos de referência

Leia cada arquivo **no momento em que a fase indicada começar** (não antes):

| Arquivo | Quando ler | Para quê |
|---|---|---|
| [references/project-analysis.md](references/project-analysis.md) | Fase 1 | Detectar linguagem, framework, banco, arquitetura, domínio e endpoints |
| [references/validation.md](references/validation.md) | Fases 1 e 3 | Subir a aplicação, gravar a linha de base e validar depois |
| [references/anti-patterns-catalog.md](references/anti-patterns-catalog.md) | Fase 2 | Catálogo de anti-patterns, sinais de detecção e severidade |
| [references/report-template.md](references/report-template.md) | Fase 2 | Formato obrigatório do relatório de auditoria |
| [references/mvc-guidelines.md](references/mvc-guidelines.md) | Fase 3 | Camadas alvo e responsabilidades de cada uma |
| [references/refactoring-playbook.md](references/refactoring-playbook.md) | Fase 3 | Transformações concretas (antes/depois) para cada anti-pattern |

## Regras invioláveis

1. **Nada muda antes do "sim".** Nas Fases 1 e 2, os únicos arquivos que você pode criar dentro do projeto ficam em `reports/` (linha de base e relatório). Qualquer outra escrita (código, config, dependências, banco) só acontece na Fase 3, depois da confirmação explícita.
2. **Evidência, não suposição.** Todo finding cita arquivo e linha(s) que você **conferiu** no código (com leitura do arquivo ou busca com número de linha). Se não conseguiu localizar a linha, o finding não entra.
3. **O contrato da API é sagrado.** Paths, métodos HTTP, nomes de campos de entrada e saída e status codes permanecem iguais. As únicas exceções são correções de segurança (ex.: parar de devolver senhas ou segredos, exigir autorização em rota administrativa), e cada uma precisa aparecer na seção "Contract changes" do resumo final.
4. **O comando de execução é preservado.** Se o projeto sobe com `python app.py` ou `npm start`, ele continua subindo com o mesmo comando depois da refatoração.
5. **Nunca afirme que algo funciona sem ter executado.** O checklist final só marca ✓ o que foi de fato verificado nesta sessão; o resto aparece como ✗ com o motivo.
6. **Agnóstico de tecnologia.** Use as heurísticas das referências para identificar a stack. Não assuma um framework pelo nome da pasta ou do projeto.

### Exemplos das regras

| Regra | ✅ Faça | ❌ Não faça |
|---|---|---|
| 1. Nada muda antes do "sim" | Na linha de base, trocar a porta fixa **numa cópia em `/tmp`** para conseguir subir a app | Editar o arquivo de config do projeto "só para testar" durante a Fase 1 |
| 1. Nada muda antes do "sim" | Parar depois da pergunta da Fase 2 e esperar a resposta | Perguntar e, na mesma resposta, já começar a refatorar |
| 2. Evidência | `File: src/orders.py:42-47`, depois de abrir o arquivo e ver as linhas | `File: src/orders.py` (sem linha) ou uma linha estimada sem conferir |
| 2. Evidência | Registrar um finding a menos quando não achou a linha | Completar a lista com problemas genéricos ("falta de testes", "código poderia ser melhor") |
| 3. Contrato da API | Manter `POST /api/items` com os mesmos campos de entrada e as mesmas chaves de resposta, mesmo que os nomes sejam ruins | "Corrigir" `qty`/`desc` para `quantity`/`description` no JSON: isso quebra os clientes |
| 3. Contrato da API | Remover o campo de senha da resposta e listar em "Contract changes" | Remover o campo em silêncio, ou manter o campo "para não mudar o contrato" |
| 4. Comando de execução | Continuar subindo com `npm start`, atualizando o caminho em `scripts.start` | Passar a exigir `node src/server.js` ou um comando novo não documentado |
| 5. Só afirmar o que executou | `✗ All endpoints respond correctly (2 regressões: GET /x → 500)` | `✓` em tudo sem ter rodado as requisições |
| 6. Agnóstico | Detectar Express por `require('express')` e `app.get(...)` no código | Supor Express porque o projeto tem `package.json`, ou Flask porque tem `app.py` |

---

## Fase 1 — Análise do projeto

Leia `references/project-analysis.md` e `references/validation.md` (seção "Linha de base").

1. Faça o inventário dos arquivos-fonte, ignorando `.git/`, `.claude/`, `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, bancos de dados e lockfiles. Conte arquivos e linhas.
2. Detecte linguagem, framework (com versão, a partir do manifesto de dependências), dependências relevantes, banco de dados e tabelas.
3. Classifique a arquitetura atual (monolítica, parcialmente em camadas ou em camadas) e descreva o domínio da aplicação a partir das tabelas, rotas e nomes de entidades.
4. Liste **todos** os endpoints (método, path, handler com arquivo:linha).
5. Grave a **linha de base**: siga `references/validation.md` para subir a aplicação numa cópia temporária, fora do projeto, e registrar o status e o formato de resposta de cada endpoint em `reports/baseline-endpoints.md`. Se não for possível subir, registre o motivo e continue; a validação da Fase 3 vai usar só a análise estática.
6. Imprima o resumo exatamente neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem e versão, se conhecida>
Framework:     <framework e versão>
Dependencies:  <principais dependências>
Database:      <engine e forma de acesso (ORM, driver, em memória...)>
Domain:        <domínio em uma linha, com as entidades principais>
Architecture:  <classificação — justificativa em uma linha>
Source files:  <N> files analyzed | ~<LOC> lines of code
DB tables:     <tabelas>
Endpoints:     <N> endpoints (<lista curta METHOD path>)
Baseline:      <N/N endpoints responderam | motivo se não foi possível subir>
Run command:   <comando atual para subir a aplicação>
================================
```

Siga direto para a Fase 2.

---

## Fase 2 — Auditoria de arquitetura

Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.

1. Percorra o catálogo **inteiro**, anti-pattern por anti-pattern, aplicando os sinais de detecção em todos os arquivos-fonte. Inclua a seção de **APIs deprecated**: compare o que o código usa com as versões instaladas e indique o equivalente moderno.
2. Para cada ocorrência, confirme arquivo e linha(s) no código e compare com a tabela **"Falsos positivos comuns"** do catálogo: se o trecho se encaixa na coluna "Não é finding", descarte. Agrupe ocorrências do mesmo problema num único finding, listando todas as linhas.
3. Classifique a severidade conforme o catálogo. Use o contexto para subir ou descer um nível quando o catálogo indicar (ex.: endpoint administrativo sem autenticação que executa SQL é CRITICAL, não HIGH).
4. Não invente findings para bater uma cota. Em compensação, **não pare no óbvio**: um projeto já dividido em pastas ainda pode ter rotas gordas, camadas mortas, validação duplicada e APIs deprecated.
5. Gere o relatório **exatamente** no formato de `references/report-template.md`, com os findings ordenados de CRITICAL a LOW.
6. Salve o relatório em `reports/audit-report.md` dentro do projeto (crie a pasta se preciso) e imprima o relatório completo na conversa.
7. Termine a fase com esta pergunta e **pare**, aguardando a resposta do usuário:

```
Phase 2 complete. Report saved to reports/audit-report.md.
Proceed with refactoring (Phase 3)? [y/n]
```

Se a resposta for "n" (ou qualquer coisa diferente de uma confirmação clara), encerre sem modificar nenhum arquivo. Se o usuário pedir ajustes no relatório, aplique-os, salve de novo e repita a pergunta.

---

## Fase 3 — Refatoração para MVC

Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.

1. **Planeje antes de escrever.** Defina a estrutura alvo conforme as guidelines para a stack detectada e mapeie cada finding para a transformação do playbook que o resolve. Adapte ao ponto de partida:
   - **Monolito:** crie as camadas do zero e distribua o código por domínio.
   - **Parcialmente em camadas:** preserve o que já está correto, introduza a camada que falta (em geral, controllers), consolide duplicações e ative código morto útil ou remova-o.
2. **Aplique as transformações nesta ordem**, porque cada passo facilita o seguinte:
   1. Configuração e segredos → módulo de config lendo variáveis de ambiente, mais `.env.example` sem valores reais.
   2. Acesso a dados → conexão gerenciada, queries parametrizadas e models/repositórios por entidade.
   3. Regras de negócio → controllers (e services, quando a regra for complexa ou compartilhada).
   4. Rotas/views → só mapeamento HTTP, parsing de entrada e formatação de resposta.
   5. Tratamento de erros → middleware/handler central com respostas padronizadas.
   6. Entry point → composition root que monta config, banco, rotas e handlers.
   7. Qualidade → APIs deprecated, constantes no lugar de magic numbers, logging no lugar de print, remoção de imports e código mortos.
3. **Remova os arquivos antigos** que foram totalmente absorvidos pelas novas camadas. Não deixe duas versões da mesma lógica.
4. Atualize o que depende da estrutura: manifesto de dependências, scripts de execução, seeds e o README do projeto (seção "Como rodar").
5. **Valide** seguindo `references/validation.md`, seção "Validação pós-refatoração":
   - instale as dependências;
   - suba a aplicação numa porta livre e confirme que ela inicia sem erros nem warnings novos;
   - repita as requisições da linha de base e compare status e formato de cada resposta;
   - faça uma nova varredura rápida com o catálogo para confirmar que os findings CRITICAL e HIGH foram resolvidos;
   - salve o resultado em `reports/validation-results.md`.
6. Se algo falhar, corrija e valide de novo (até 3 ciclos). Se ainda houver falhas, relate-as com honestidade no resumo.
7. Encerre a aplicação e remova os artefatos temporários de validação.
8. Imprima o resumo final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore da nova estrutura, com uma frase por pasta>

## Findings addressed
<ID do finding → transformação aplicada, um por linha>
<findings não resolvidos, com o motivo>

## Contract changes
<mudanças intencionais de contrato (só segurança) — ou "None">

## Validation
  ✓/✗ Application boots without errors (<comando e porta>)
  ✓/✗ All endpoints respond correctly (<N/N iguais à linha de base>)
  ✓/✗ No CRITICAL/HIGH anti-patterns remaining
  ✓/✗ Run command unchanged (<comando>)
================================
```
