---
title: "42_chat — Knowledge Base"
category: index
tags: [meta]
created: "2026-06-13"
updated: "2026-06-13"
---

# 42_chat Knowledge Base

> Vault do framework SDD autônomo. Agentes: `onboard` + `agent-orchestrator` + `agent-dev`.
> Estrutura segue taxonomia `llm-wiki`: concepts/ globais + projects/42_chat/ aninhado.

## Estrutura

- [[concepts/]] — Padrões, arquitetura, decisões de design (cross-project)
- [[projects/42_chat/42_chat|42_chat]] — Overview do framework SDD
- [[projects/42_chat/features/]] — Features do framework
- [[projects/42_chat/agents/]] — Agentes Hermes
- [[projects/42_chat/skills/]] — Skills SDD

## Concepts (globais)

- [[concepts/sdd|SDD]] — Spec-Driven Development: metodologia e pipeline
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo explicado
- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero
- [[concepts/constitution|Constituição]] — Regras arquiteturais do framework
- [[concepts/tech|Stack Tecnológica]] — Stack homologada

## Projeto: 42_chat (Framework SDD)

### Agentes

- [[projects/42_chat/agents/agent-onboard|onboard]] ✅ — Inicializa projetos no SDD
- [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]] ✅ — Executor runtime com DAG
- `agent-dev` ✅ — Implementado (006). Persona fixa com skills plugáveis.

### Features

**Ativas (004-006):**
- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks com DAG]] ✅ — `sdd-generate-tasks` v2.0.0
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Agent Orchestrator]] ✅ — Runtime de execução paralela
- [[projects/42_chat/features/feature-006-agent-dev|006: Agent Dev]] ✅ — Persona implementadora

**Pendentes (007-009):**
- 007: Agent QA — Testes, Gherkin, lint
- 008: Agent DevOps — CI/CD, Docker, deploy
- 009: Agent Pentester — Segurança, OWASP, secrets

**Experimentais (001-003):**
> Laboratório de aprendizado SDD. Não fazem parte do pipeline ativo.

- [[projects/42_chat/features/feature-001-start-repo|001: Estrutura]] ✅ — Templates base, CI/CD
- [[projects/42_chat/features/feature-002-sdd-templates|002: Templates SDD]] ✅ — Formatos canônicos
- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] 🔄 — Scaffold de skills

### Skills SDD

- [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
- [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
- [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md (v2.0.0)
