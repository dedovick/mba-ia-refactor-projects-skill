# Plano — Skill `refactor-arch` (Refatoração Arquitetural Automatizada)

Objetivo: criar uma skill do Claude Code que **analisa, audita e refatora para MVC** qualquer projeto, e provar que ela é agnóstica de tecnologia rodando-a em 3 projetos (Flask desorganizado, Express, Flask parcialmente organizado).

Decisões:
- Ferramenta: **Claude Code** — skill em `.claude/skills/refactor-arch/` (SKILL.md + `references/*.md`)
- Repositório: https://github.com/dedovick/mba-ia-refactor-projects-skill (`origin`), `upstream` = devfullcycle
- Quem roda a skill nos 3 projetos: **o Pedro**, numa sessão interativa do Claude Code dentro de cada projeto (a Fase 2 precisa pausar para confirmação humana; as execuções geram os logs/prints do README)
- Análise manual: [`docs/analise-manual.md`](docs/analise-manual.md) — 24 + 22 + 20 findings

---

## 1. Desenho da skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                         # o "prompt": 3 fases, gates, regras de segurança
└── references/
    ├── project-analysis.md          # heurísticas: linguagem, framework, banco, arquitetura, endpoints
    ├── anti-patterns-catalog.md     # ≥ 8 anti-patterns (incl. APIs deprecated): sinais de detecção + severidade
    ├── report-template.md           # formato fixo do relatório da Fase 2
    ├── mvc-guidelines.md            # camadas alvo e responsabilidades (por stack)
    ├── refactoring-playbook.md      # ≥ 8 transformações com código antes/depois (Python e JS)
    └── validation.md                # como subir a app, smoke test e comparação com a linha de base
```

As 5 áreas obrigatórias viram um arquivo cada; `validation.md` é extra (a Fase 3 é onde as skills costumam falhar).

### As 3 fases

| Fase | O que faz | Saída | Gate |
|---|---|---|---|
| 1 — Análise | Detecta stack, domínio, arquitetura, tabelas e **lista todos os endpoints**; sobe a app e grava a **linha de base** das respostas | Resumo no formato do enunciado | — |
| 2 — Auditoria | Cruza o código com o catálogo; cada finding com arquivo:linha verificados; ordena CRITICAL → LOW; salva o relatório | Relatório + arquivo `reports/audit-report.md` | **Pausa e pede confirmação**; não altera nenhum arquivo do código antes do "sim" |
| 3 — Refatoração | Aplica o playbook, gera a estrutura MVC, sobe a app numa porta livre e compara cada endpoint com a linha de base | Nova estrutura + checklist de validação | Só termina com a app subindo e os endpoints respondendo |

### Regras que vêm da análise manual

1. **Contrato da API preservado:** mesmos paths, métodos, campos e status codes. Mudanças só por segurança (tirar senhas/segredos das respostas, proteger rotas admin), sempre listadas no relatório final.
2. **Linha de base antes de mexer:** as respostas dos endpoints são registradas na Fase 1 e comparadas na Fase 3.
3. **Porta configurável:** `PORT` via env/config; validação numa porta livre (a 5000 é do AirPlay no macOS).
4. **Julgar responsabilidades, não pastas:** um projeto com `models/` e `routes/` ainda pode ter rotas gordas, serviços mortos e validação duplicada.
5. **Adaptar a transformação ao ponto de partida:** monolito → criar camadas; projeto parcialmente organizado → mover lógica para controllers e consolidar.
6. **Nada de segredos no código:** config em módulo próprio lendo variáveis de ambiente, com `.env.example`.

### Pontos de atenção

- **Plugins globais do Claude Code:** a sua instalação carrega plugins que também sugerem skills (ex.: superpowers). Se atrapalharem a execução, rodar com esses plugins desativados.
- **Relatório:** a skill salva em `reports/audit-report.md` dentro do projeto; depois copiamos para `reports/audit-project-N.md` na raiz, como pede o enunciado.
- **Iteração segura:** cada execução começa de um estado commitado. Se uma rodada falhar, voltamos o projeto com `git restore`/`git clean` e ajustamos a skill.

---

## 2. Checklist de requisitos

### Setup
- [x] R1. Fork público em `dedovick`, remotes `origin`/`upstream`
- [x] R2. Análise manual dos 3 projetos, com ≥ 5 problemas cada (≥ 1 CRITICAL/HIGH, ≥ 2 MEDIUM, ≥ 2 LOW)

### Skill
- [x] R3. `SKILL.md` com as 3 fases sequenciais
- [x] R4. Referência: análise de projeto (linguagem, framework, banco, arquitetura)
- [x] R5. Referência: catálogo com ≥ 8 anti-patterns, severidade distribuída e sinais de detecção
- [x] R6. Catálogo inclui detecção de APIs deprecated com o equivalente moderno
- [x] R7. Referência: template do relatório
- [x] R8. Referência: guidelines MVC (Models, Views/Routes, Controllers)
- [x] R9. Referência: playbook com ≥ 8 transformações com código antes/depois
- [x] R10. Fase 2 pausa e pede confirmação antes de alterar arquivos
- [x] R11. Fase 3 valida boot + endpoints
- [x] R12. Skill agnóstica: nenhuma referência específica aos 3 projetos

### Execução (para cada projeto: P1 code-smells, P2 ecommerce-legacy, P3 task-manager)
- [ ] R13. P1: Fase 1 correta · ≥ 5 findings · ≥ 1 CRITICAL/HIGH · app funciona · `reports/audit-project-1.md` · commit
- [ ] R14. P2: skill copiada · mesmas verificações · `reports/audit-project-2.md` · commit
- [ ] R15. P3: skill copiada · detecta o domínio Task Manager · achados mesmo com camadas · endpoints OK · `reports/audit-project-3.md` · commit
- [ ] R16. Checklist de validação do enunciado preenchido para os 3

### README
- [ ] R17. Seção "Análise Manual"
- [ ] R18. Seção "Construção da Skill" (decisões, catálogo, agnosticismo, desafios)
- [ ] R19. Seção "Resultados" (findings por severidade, antes/depois, checklists, prints/logs, comportamento por stack)
- [ ] R20. Seção "Como Executar"

---

## 3. Ondas

**Onda 0 — Setup:** fork e remotes ✓

**Onda 1 — Análise manual:** ✓ [`docs/analise-manual.md`](docs/analise-manual.md)

**Onda 2 — Skill:** escrever `SKILL.md` e as 6 referências no `code-smells-project`. Revisar contra R3–R12.

**Onda 3 — Execução e iteração:**
1. P1: Pedro roda `/refactor-arch` → revisamos a Fase 1 e o relatório → confirma → revisamos a Fase 3 → ajustes na skill se preciso → commit.
2. P2: copiar a skill (já ajustada) → rodar → revisar → commit.
3. P3: idem.
4. Se um ajuste da skill nascer no P2 ou P3, propagar para as 3 cópias.

**Onda 4 — README e entrega:** 4 seções, checklist item a item, push.

---

## 4. Linha de base (antes da refatoração)

| Projeto | Como sobe | Endpoints | Observações do boot |
|---|---|---|---|
| P1 | `python app.py` (porta 5000 fixa) | 19 | Sobe limpo numa porta livre; `/usuarios` devolve senhas; SQLi no login confirmado |
| P2 | `npm start` (porta 3000 fixa) | 3 | Sobe limpo; checkout OK/recusado conforme `api.http`; `"card": 4111` derruba o processo |
| P3 | `python seed.py && python app.py` (porta 5000 fixa) | 22 | Sobe com `LegacyAPIWarning` (`Query.get`) e `DeprecationWarning` (`utcnow`); inputs inválidos geram 500 |

## 5. Log de iterações

| # | Data | Projeto | Mudança na skill | Findings (C/H/M/L) | App OK? | Observações |
|---|---|---|---|---|---|---|
| 1 | 2026-09-26 | P1 | v1 (24 APs, 16 Ts) | 20 (6/5/6/3) | Sim — boot OK, mudanças só de segurança | Interrompida na Fase 3 pelo Pedro para incluir melhorias. Artefatos em `docs/iteracoes/p1-skill-v1-interrompida/`. Estrutura seguiu `views/`. |
| — | 2026-09-26 | — | v2: +AP-25 (condicionais em cadeia), +AP-26 (coesão de módulos), +T-17, +T-18; tabela de falsos positivos; exemplos ✅/❌ das regras; exemplos 100% fictícios | — | — | Sugestões do Pedro: `if` sequenciais e organização de módulos; exemplos genéricos para testar generalização |
| 2 | 2026-09-26 | P1 | `skill-v2` | 23 (6/6/7/4) | Sim — 35/35 iguais à linha de base; validação independente: SQLi no login bloqueado, senha fora das respostas, /admin com token, quantidade negativa → 400 | Commit `3366ae4`. AP-25 e AP-26 detectados. |
| 3 | 2026-09-27 | P2 | `skill-v2` | 20 (6/4/7/3) | Sim — contrato do `api.http` idêntico; `card` numérico → 400 (antes derrubava); cartão mascarado no log; admin com token; `sqlite3` → `node:sqlite` | **Falhou em detectar** o checkout com e-mail existente e senha errada (continua 200). Motiva a v3. |
| — | 2026-09-27 | — | `skill-v3`: sondas de segurança/robustez antes e depois; Fase 2 cruza a linha de base e as sondas com os findings (`Evidence:`); sinal de identidade não verificada no AP-06 + correção no playbook; comparação de listas sem depender da ordem; status que mentem como exceção de contrato; nomes de pastas das guidelines no relatório | — | — | Motivado pelo P2: finding de identidade não detectado e, por isso, não corrigido. Propagada para as 3 cópias. |
| — | 2026-09-27 | P1, P2 | — | — | — | P1 e P2 restaurados ao código original para reexecução com `skill-v3` (checagem de regressão). Resultados da v2 guardados em `docs/iteracoes/p{1,2}-skill-v2/` e nos commits `3366ae4` e `b335106`. |
