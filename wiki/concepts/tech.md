---
title: "Stack Tecnológica"
category: concepts
tags: [tech, stack, go, postgresql, docker]
aliases: [tech, tecnologia]
summary: "Stack tecnológica homologada do 42_chat: Go, PostgreSQL, Docker, GitHub Actions."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:.github/memory/tech.md
lifecycle: draft
lifecycle_changed: "2026-06-13"
base_confidence: 0.6
provenance:
  extracted: 0.4
  inferred: 0.6
  ambiguous: 0.0
---

# Stack Tecnológica

> Arquivo canônico: `../.github/memory/tech.md` (repo)
> Stack homologada para o projeto 42_chat.

## Linguagens

| Linguagem | Versão | Status |
|---|---|---|
| Go | a definir | go.mod pendente |
| JavaScript/TypeScript | a definir | package.json pendente |

## Backend

| Lib | Propósito |
|---|---|
| Gorilla WebSocket | WebSocket server |
| pgx | Driver PostgreSQL |

## Frontend (planejado)

| Lib | Propósito |
|---|---|
| Vite | Build tool / dev server |
| Chatscope | Componentes de chat |
| Tailwind CSS | Estilização |

## Banco de Dados

| Componente | Propósito |
|---|---|
| PostgreSQL | Banco principal |
| pgx | Driver Go |

## CI/CD

| Workflow | Gatilho |
|---|---|
| go-ci.yml | PRs → develop, main |
| enforce-branch-flow.yml | PRs → main, develop |
| auto-pr-feature-to-develop.yml | push → feature/* |
| auto-pr-to-main.yml | push → develop |

## Infraestrutura (planejado)

- Docker + Docker Compose (Dockerfile pendente)

## Relacionado

- [[constitution]] — Regras arquiteturais
- [[sdd]] — Metodologia de desenvolvimento
- [[projects/42_chat|42_chat]] — Projeto principal
