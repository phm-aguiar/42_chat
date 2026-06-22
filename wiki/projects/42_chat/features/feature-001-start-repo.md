---
title: "001: Estrutura do Repositório"
category: projects
tags: [sdd, infra, github-actions, ci]
summary: "Inicialização do repo 42_chat: estrutura SDD, CI/CD, templates base."
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
sources:
  - repo:specs/features/001-start-repo/
lifecycle: verified
lifecycle_changed: "2026-06-13"
base_confidence: 0.9
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
---

# 001: Estrutura do Repositório

> Feature fundadora. Estabelece a estrutura SDD e CI/CD do projeto.

## Status

**Implementada.** Tasks concluídas: 6/8.

## O que entregou

- `.github/memory/` com `constitution.md` e `tech.md` (templates)
- Árvore `specs/` (domain-events, features, infra)
- `AGENTS.md` com seção SDD Workflow
- 4 workflows GitHub Actions: CI, enforce-branch-flow, auto-PR feature→develop, auto-PR develop→main
- Script `check-sdd.sh` e template de `constitution.md`

## Tasks pendentes

- **T006:** Criar `llms.txt` na raiz
- **T007:** Documentar fluxo SDD no README.md

## Relacionado

- [[concepts/sdd]] — Template criado nesta feature
- [[concepts/sdd]] — Stack mapeada nesta feature
- [[projects/42_chat/42_chat]] — Projeto principal
- [[sdd]] — Metodologia
