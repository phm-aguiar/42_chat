---
title: "42_chat — Projeto"
category: projects
tags: [sdd, 42_chat, go, websocket, chat]
summary: "Chat app em Go com WebSocket. Laboratório para framework SDD autônomo com agentes IA."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:AGENTS.md
  - repo:specs/
lifecycle: draft
lifecycle_changed: "2026-06-13"
base_confidence: 0.8
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
---

# 42_chat

> Chat application em Go. Projeto laboratório para o framework SDD autônomo com agentes IA.

## Stack

- **Linguagem:** Go
- **Frontend:** React + Vite + Tailwind (planejado)
- **Banco:** PostgreSQL + pgx
- **WebSocket:** Gorilla WebSocket
- **CI/CD:** GitHub Actions (4 workflows)

## Agentes do Framework

- [[projects/agent-onboard|onboard]] — Inicializa projetos no SDD (init, explore, brainstorm)
- [[projects/agent-orchestrator|agent-orchestrator]] — Executor runtime: lê DAG, spawna subagentes

## Pipeline SDD Ativo

1. `onboard` inicializa → spec.md, constitution.md, tech.md
2. `sdd-generate-plan` → plan.md com ADRs
3. `sdd-generate-tasks` (formato DAG) → tasks.md com paralelismo
4. `agent-orchestrator` executa → spawna Dev, QA, Test em paralelo

## Features Ativas

- [[feature-004-sdd-tasks-dag|004: Tasks com DAG]] — Em implementação
- [[feature-005-agent-orchestrator|005: Agent Orchestrator]] — Em implementação

## Features Experimentais (001-003)

Criadas como laboratório SDD. Geraram templates canônicos e validaram o fluxo spec→plan→tasks.

## Agentes Futuros

- 006: Agent Dev — código, smoke-test
- 007: Agent QA — testes, Gherkin, lint
- 008: Agent DevOps — CI/CD, Docker
- 009: Agent Pentester — segurança, OWASP

## Relacionado

- [[constitution]] — Regras arquiteturais
- [[tech]] — Stack tecnológica
- [[sdd]] — Metodologia
