---
name: git-conventional-commit
description: >
  Use when the user asks to commit changes or prepare a commit message.
  Generates structured commit messages with sections (feat, fix, docs, chore,
  test, refactor) using bullet lists. Follows the user's preferred format:
  short title line, blank line, sections with dash-prefixed items.
  Trigger keywords: commit, commitar, git commit, preparar commit, mensagem de commit.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, commit, conventional-commits, changelog]
    category: github
    related_skills: [wiki-query]
    created: "2026-06-12"
---

# Git Conventional Commit (formato squad)

Gera mensagens de commit no formato preferido do squad 42_chat:
título curto + seções com bullet lists.

## Propósito

Padronizar commits com seções semânticas, facilitando navegação no log
e geração de changelogs. O formato é:

```
<tipo>: <título curto>

<tipo>:
 - <item 1>
 - <item 2>

<outro-tipo>:
 - <item 3>
```

## Tipos de seção (em ordem de prioridade)

| Prefixo | Quando usar |
|---------|------------|
| `feat` | Nova feature, spec, skill, agente, funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação (README, AGENTS.md, comentários) |
| `refactor` | Refatoração sem mudança de comportamento |
| `test` | Testes (unitários, smoke, cenários) |
| `chore` | Tarefas mecânicas (deps, config, symlinks, CI, cleanup) |
| `style` | Formatação, lint, whitespace |

## Fluxo

### Passo 1: Analisar mudanças

```bash
git status --short
git diff --stat HEAD
```

Identifique o que mudou e agrupe por tipo semântico:
- Arquivos novos em `specs/features/` → `feat`
- Mudanças em `README.md`, `AGENTS.md` → `docs`
- Remoção de arquivos obsoletos, ajustes de CI → `chore`
- Scripts, symlinks, config → `chore`

### Passo 2: Montar mensagem

Use `git add -A` (ou `git add <paths>` se o usuário especificar) e:

```bash
git commit -m "<tipo>: <título curto>

<seção>:
 - <item>
 - <item>

<seção>:
 - <item>"
```

### Passo 3: Verificar

```bash
git log --oneline -1
```

## Referências

- `references/tier-system.md` — Tier system (1/2/3) que ajusta o formato da mensagem conforme a criticalidade do commit
- `references/forbidden-patterns.md` — Padrões bloqueados (mensagens vagas, atribuição a tools, secrets)

## Regras

- **Título:** max 72 chars, lowercase, sem ponto final
- **Seções:** só inclua seções que têm itens. Não gere seções vazias
- **Itens:** dash + espaço, lowercase, sem ponto final
- **Ordem:** feat → fix → docs → refactor → test → chore → style
- **Nunca commite sem o usuário pedir**
- **Nunca faça push sem o usuário pedir**
- **Sempre use `git add -A` a menos que o usuário especifique paths**

## Exemplo

```
feat: adiciona pipeline SDD com brainstorm interativo

feat:
 - adiciona sdd-brainstorm com entrevista via clarify()
 - gera spec.md a partir de template canônico
 - adiciona referências de dimensões da entrevista

docs:
 - atualiza AGENTS.md com seção SDD Workflow
 - documenta fluxo de 8 passos no README

chore:
 - remove diretório .opencode/ obsoleto
 - ajusta symlinks para ~/.hermes/skills/
```
