---
title: "agent-orchestrator — Executor Runtime SDD"
category: projects
tags: [sdd, agent, orchestrator, delegate-task]
summary: "Agente que lê DAG de tasks e spawna subagentes Dev/QA/Test em paralelo."
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
sources:
  - repo:.hermes/agents/agent-orchestrator/
lifecycle: draft
lifecycle_changed: "2026-06-13"
base_confidence: 0.8
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
---

# agent-orchestrator

> O capataz. Lê o plano (`tasks.md` com DAG), spawna subagentes (Dev, QA, Test), verifica entregas, escala bloqueios.

## Funcionamento

1. **Approval gate:** verifica `Aprovado: true` no spec.md
2. **Carrega DAG:** lê `tasks.md`, valida (sem ciclos, sem órfãs)
3. **Janela deslizante:** até 3 subagentes simultâneos via `delegate_task`
4. **Retry:** 3 tentativas com contexto enriquecido
5. **Validação:** verifica arquivos criados, smoke-test, exit code
6. **Escalação:** 3 falhas → pausa sub-árvore → input humano

## Toolsets por papel

| Papel | Toolsets |
|---|---|
| Dev | `terminal`, `file` |
| QA | `terminal`, `file`, `web` |
| Test | `terminal`, `file` |

## Como invocar

```bash
agent-run agent-orchestrator "orquestra a feature 005"
```

## Relacionado

- [[projects/42_chat/agents/agent-onboard|onboard]] — Inicialização (complementar)
- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Formato que o orchestrator consome
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Feature]] — Spec, plan e tasks
