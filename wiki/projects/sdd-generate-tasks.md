---
title: "sdd-generate-tasks"
category: projects
tags: [sdd, skill, tasks, DAG, execution]
sources: []
summary: Skill SDD v2.0.0 que gera tasks.md com DAG (dependências, paralelismo, isolamento de arquivos)
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# sdd-generate-tasks

> Gera `tasks.md` com formato DAG (Directed Acyclic Graph) para execução paralela segura.

## Localização
Skill Hermes: `.hermes/skills/sdd/generate-tasks/SKILL.md` (v2.0.0)

## Função
- Approval gate: verifica `Aprovado: true` no spec.md
- Deriva tarefas atômicas com metadados DAG (Papel, Dependências, Paralelizável, Arquivos)
- Interação fase por fase via `clarify()`
- Validação de DAG: ciclos, dependências quebradas, tasks órfãs
- Isolamento de arquivos: tasks paralelas NUNCA compartilham paths

## Pipeline
`sdd-generate-plan` → `plan.md` → **`sdd-generate-tasks`** → `tasks.md` → `agent-orchestrator`

## Relacionado
- [[sdd-generate-plan]] — Passo anterior
- [[projects/feature-004-sdd-tasks-dag]] — Feature que implementou o formato DAG
- [[projects/agent-orchestrator]] — Consumidor do tasks.md
