---
title: "Spec-Driven Development (SDD)"
category: concepts
tags: [sdd, metodologia]
summary: "Metodologia onde specs são a fonte primária; código deriva delas."
created: "2026-06-13"
updated: "2026-06-13"
sources: []
---

# Spec-Driven Development (SDD)

> Specs deixam de servir ao código; código passa a servir às specs.

## Pipeline no 42_chat

1. [[projects/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
2. [[projects/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
3. [[projects/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md
4. Aprovação humana (`Aprovado: true`)
5. [[projects/agent-orchestrator]] — Execução paralela com subagentes

## Regras

- Nunca implementar sem spec.md + plan.md aprovados
- Consultar [[constitution]] antes de qualquer código
- Validar estrutura periodicamente
