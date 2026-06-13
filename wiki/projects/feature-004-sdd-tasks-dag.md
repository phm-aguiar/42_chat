---
title: "004: Tasks com DAG"
category: projects
tags: [sdd, tasks, dag, paralelismo]
summary: "Upgrade do sdd-generate-tasks: formato DAG com dependências, paralelismo e isolamento de arquivos."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:specs/features/004-sdd-tasks-dag/spec.md
lifecycle: draft
lifecycle_changed: "2026-06-13"
base_confidence: 0.7
provenance:
  extracted: 0.7
  inferred: 0.3
  ambiguous: 0.0
---

# 004: Tasks com DAG

> Upgrade do `sdd-generate-tasks`: formato DAG no `tasks.md` com fases, dependências explícitas, paralelismo e isolamento de arquivos.

## Status

**Draft.** Spec escrita e revisada. `Aprovado: false`. Aguardando aprovação humana.

## Por que DAG?

O formato atual é flat (fases sequenciais com "Depende de Tnnn" simples). Não modela paralelismo explícito nem garante isolamento de arquivos entre tasks concorrentes.

O Runtime Orchestrator (feature 005) **não funciona** sem este formato.

## Formato DAG

Cada task ganha metadados estruturados:
- `Papel:` Dev, QA, Test
- `Dependências:` T001, T002
- `Paralelizável: true|false`
- `Arquivos:` paths que a task modifica

Paralelismo seguro: tasks da mesma fase com `Arquivos` disjuntos e sem dependência entre si.

## Approval Gate

1. Usuário altera `Aprovado: false` → `Aprovado: true` no spec.md
2. Invoca `sdd-generate-tasks`
3. Skill verifica o gate → gera tasks.md com DAG

## Dependências

- **Nenhuma.** Feature independente (upgrade de skill existente)
- **Consumida por:** [[feature-005-agent-orchestrator|005: Runtime Orchestrator]]

## Relacionado
- [[feature-003-forge-skill|003: Forge Skill]] — Feature anterior
- [[feature-005-agent-orchestrator|005: Orchestrator]] — Consumidora do DAG
- [[sdd]] — Metodologia
