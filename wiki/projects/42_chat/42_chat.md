---
title: "42_chat — Framework SDD Autônomo"
category: project
tags: [sdd, framework, agents, ai]
source_path: /home/zeenyt__/Projetos/42_chat
summary: Framework SDD autônomo com agentes IA e humanos in loop. Pipeline: brainstorm → spec → plan → tasks (DAG) → orchestrator → subagentes.
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# 42_chat — Framework SDD Autônomo

> **Produto:** Framework SDD autônomo com agentes IA.
> **42_chat app:** Smoke-test futuro pra validar o framework — **não é o produto.**

## Pipeline

```
sdd-brainstorm → spec.md → Aprovado: true
     ↓
sdd-generate-plan → plan.md
     ↓
sdd-generate-tasks (DAG) → tasks.md
     ↓
agent-orchestrator
  ├─ spawna agent-dev   (implementa código)
  ├─ spawna agent-qa    (testa)
  ├─ spawna agent-devops (CI/CD, deploy)
  └─ spawna agent-pentester (security scan)
```

## Agentes

| Agente | Status | Feature |
|---|---|---|
| [[projects/42_chat/agents/agent-onboard|onboard]] | ✅ Implementado | Inicialização SDD |
| [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]] | ✅ Implementado | 005 — Runtime executor |
| agent-dev | ✅ Implementado | 006 — Persona implementadora |
| agent-qa | ❌ Pendente | 007 |
| agent-devops | ❌ Pendente | 008 |
| agent-pentester | ❌ Pendente | 009 |

## Features

- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] ✅
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Orchestrator]] ✅
- [[projects/42_chat/features/feature-006-agent-dev|006: Agent Dev]] ✅
- 007: Agent QA ❌
- 008: Agent DevOps ❌
- 009: Agent Pentester ❌

## Skills

- [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]]
- [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]]
- [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]]

## Conceitos

- [[concepts/sdd|SDD]] — Metodologia
- [[concepts/constitution|Constituição]] — Regras
- [[concepts/tech|Stack]] — Tecnologias

## Repositório

- `specs/features/` — Specs SDD
- `.hermes/agents/` — Agentes versionados
- `.hermes/skills/` — Skills versionadas
- `.github/memory/` — Constitution + tech.md
