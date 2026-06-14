---
title: "005: Agent Orchestrator"
category: projects
tags: [sdd, orchestrator, delegate-task, paralelismo]
summary: "Agente supervisor que lê DAG de tasks e spawna subagentes Dev/QA/Test em paralelo com retry e escalação."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:specs/features/005-runtime-orchestrator/
lifecycle: in-progress
lifecycle_changed: "2026-06-13"
base_confidence: 0.8
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
---

# 005: Agent Orchestrator

> Agente Hermes que lê `tasks.md` com DAG e spawna subagentes especializados (Dev, QA, Test) em paralelo via `delegate_task`.

## Status

**Em implementação.** Spec ✓ Plan ✓ Tasks ✓ (16 tasks, 4 fases).

## Artefatos

- `spec.md` — Especificação funcional completa
- `plan.md` — 5 ADRs documentadas
- `tasks.md` — 16 tasks em 4 fases (Estrutura, Orquestração, Validação, Documentação)
- `.hermes/agents/agent-orchestrator/AGENT.md` — Agente implementado
- `.hermes/agents/agent-orchestrator/context.yaml` — Receita de contexto

## Comportamento

1. Lê `tasks.md` com DAG (formato da feature 004)
2. Verifica `Aprovado: true` no spec.md (approval gate)
3. Spawna subagentes em janela deslizante de 3 simultâneos
4. Política de retry: máx 3 tentativas com contexto enriquecido
5. Valida evidência de DONE antes de marcar `[x]`
6. Escala bloqueios para humano após 3 falhas

## Como invocar

```bash
agent-run agent-orchestrator "orquestra a feature 005"
```

## Dependências

- **Feature 004 (sdd-tasks-dag):** formato DAG no tasks.md

## Relacionado

- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Dependência direta
- [[projects/42_chat/agents/agent-onboard|onboard]] — Agente de inicialização (complementar)
- [[sdd]] — Metodologia
