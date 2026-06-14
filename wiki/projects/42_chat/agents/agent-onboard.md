---
title: "onboard — Agente de Inicialização SDD"
category: projects
tags: [sdd, agent, onboard, init]
summary: "Agente que inicializa projetos no framework SDD: estrutura, stack, brainstorm."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:.hermes/agents/onboard/
lifecycle: implemented
lifecycle_changed: "2026-06-13"
base_confidence: 0.9
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
---

# onboard

> Agente de entrada do framework SDD. Inicializa a estrutura, mapeia a stack e conduz brainstorms de features.

## Responsabilidades

1. **Inicializar projeto:** `sdd-init-repo` + `sdd-explore-tech`
2. **Brainstorm de features:** `sdd-brainstorm` → spec.md interativo
3. **Encaminhar para execução:** orienta invocação do `agent-orchestrator`

## Skills que carrega

| Skill | Quando |
|---|---|
| `sdd-init-repo` | Criar `.github/memory/` e `specs/` |
| `sdd-explore-tech` | Preencher `tech.md` |
| `sdd-brainstorm` | Entrevista interativa para spec.md |
| `sdd-validate` | Auditar estrutura SDD |

## Como invocar

```bash
agent-run onboard "inicializa o projeto 42_chat"
```

## O que NÃO faz

- Não implementa código
- Não toma decisões técnicas do plan.md
- Não modifica constitution.md sem permissão
- Não executa tasks — isso é o [[projects/42_chat/agents/agent-orchestrator]]

## Relacionado

- [[projects/42_chat/agents/agent-orchestrator]] — Executor runtime (complementar)
- [[sdd]] — Metodologia
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Agent Orchestrator]] — Feature que implementa o executor
