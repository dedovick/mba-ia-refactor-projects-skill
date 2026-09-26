# Template do Relatório de Auditoria (Fase 2)

O relatório é impresso na conversa **e** salvo em `reports/audit-report.md`. Use exatamente esta estrutura. O arquivo salvo é Markdown: o bloco de cabeçalho vai dentro de um bloco de código para manter o alinhamento.

## Regras

- Findings ordenados por severidade: todos os CRITICAL, depois HIGH, MEDIUM e LOW. Dentro da mesma severidade, do mais impactante para o menos.
- Numeração contínua (`F-01`, `F-02`...), usada depois no resumo da Fase 3.
- `File:` sempre com caminho relativo à raiz do projeto e linha ou intervalo **conferidos**. Vários locais separados por vírgula; vários arquivos separados por ` | `.
- `Description:` o que está errado, com um trecho curto do código entre crases.
- `Impact:` a consequência concreta (o que pode acontecer), não uma repetição da descrição.
- `Recommendation:` a correção, citando a transformação do playbook (`T-xx`).
- `Catalog:` o ID do anti-pattern (`AP-xx`).
- Findings de APIs deprecated levam `[DEPRECATED]` no título e o equivalente moderno na recomendação.
- Os números do `Summary` precisam bater com a lista de findings.

## Estrutura

````markdown
# Architecture Audit Report

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <linguagem> + <framework e versão>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <AAAA-MM-DD>
================================
```

## Summary

CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| Severity | Count | Findings |
|---|---|---|
| CRITICAL | <n> | F-01, F-02, ... |
| HIGH | <n> | ... |
| MEDIUM | <n> | ... |
| LOW | <n> | ... |

## Findings

### F-01 [CRITICAL] <título curto>
File: <arquivo>:<linha(s)>
Catalog: AP-xx
Description: <o que está errado, com um trecho do código>
Impact: <consequência concreta>
Recommendation: <correção> (T-xx)

### F-02 [CRITICAL] ...

<... demais findings, na ordem de severidade ...>

## Deprecated APIs

| API | Onde | Equivalente moderno |
|---|---|---|
| <api> | <arquivo:linha> | <substituição> |

(Se não houver, escreva: "Nenhuma API deprecated encontrada para as versões instaladas." e cite as versões verificadas.)

## Architecture Overview

- **Current:** <classificação da Fase 1 e o principal motivo>
- **Target:** <estrutura MVC proposta, em uma ou duas linhas>

```
================================
Total: <N> findings
================================
```
````

## Exemplo de finding bem escrito

```markdown
### F-03 [CRITICAL] SQL Injection na autenticação
File: data/accounts.py:57, 81-82
Catalog: AP-02
Description: A query de autenticação concatena os valores recebidos: `"SELECT * FROM accounts WHERE login = '" + login + "' AND pwd = '" + pwd + "'"`.
Impact: Um login como `root' --` autentica sem senha; qualquer apóstrofo no input quebra a query com erro 500.
Recommendation: Usar query parametrizada (`WHERE email = ?`) e comparar a senha com hash (T-02, T-06).
```

## Exemplo de finding mal escrito (não faça)

```markdown
### [HIGH] Código ruim
File: data/accounts.py
Description: O arquivo tem problemas de qualidade.
```

Falta linha, a severidade não segue o catálogo, a descrição é vaga e não há impacto nem recomendação.
