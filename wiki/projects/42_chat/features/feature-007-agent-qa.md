---
title: "007: Agent QA"
category: projects
tags: [sdd, agent, qa, qualidade, teste]
summary: "Guardiao da qualidade do framework SDD. Spawnado pelo orchestrator como subagente leaf. Ciclo: le spec, escreve Gherkin, executa testes, lint, cobertura, reporta DONE/REJECTED/BLOCKED."
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
sources:
  - repo:specs/features/007-agent-qa/spec.md
lifecycle: verified
---

# Feature 007: Agent QA

> Guardiao da qualidade. Valida implementacoes do Dev contra a spec.

## Status
✅ **Implementado** — 2026-06-13

## Artefatos
- **Spec:** `specs/features/007-agent-qa/spec.md`
- **Plan:** `specs/features/007-agent-qa/plan.md` (6 ADRs)
- **Tasks:** `specs/features/007-agent-qa/tasks.md` (7 tasks, 3 fases)
- **Agente:** `.hermes/agents/agent-qa/AGENT.md` + `context.yaml`

## Arquitetura
- **Tipo:** Agente Hermes nativo (AGENT.md + context.yaml)
- **Runtime:** Subagente leaf via `delegate_task`
- **Toolsets:** `terminal` + `file` (sem acesso web)
- **Timeout:** 30 minutos

## Ciclo de Validacao
```
Le spec → Escreve Gherkin → Testes unitarios → go test → go vet → Cobertura → Reporta
```

## Contrato com Orchestrator
- **DONE:** Todos os testes passam + lint limpo + cobertura OK + evidencias
- **REJECTED:** Teste quebrado, lint warning ou cobertura baixa — com output completo
- **BLOCKED:** Spec ambigua ou skill nao cobre (nunca infere, nunca busca web)

## Tipos de Teste Cobertos
| Tipo | Responsabilidade |
|---|---|
| Unitario | QA (007) |
| Gherkin/BDD | QA (007) |
| Lint/Vet | QA (007) |
| Cobertura | QA (007) |
| E2E | QA (007) |
| Regressao | QA (007) |
| Integracao | DevOps (008) — standby |
| Performance | DevOps (008) — standby |
| Seguranca | Pentester (009) — futuro distante |

## Decisoes Arquiteturais (ADRs)
- **ADR-1:** Agente Hermes nativo
- **ADR-2:** Skills de teste como parametro (plugaveis por stack)
- **ADR-3:** Tres status: DONE, REJECTED, BLOCKED
- **ADR-4:** Sem acesso web (terminal + file apenas)
- **ADR-5:** Nao julga causa de falha
- **ADR-6:** Persona molde — skills de teste sao features separadas

## Smoke-test
- DONE: 5/5 testes passam, 100% cobertura, vet limpo ✅
- REJECTED: codigo ausente → QA rejeitou com evidencia ✅
- BLOCKED: fixture criado, QA nunca infere ✅

## Dependencias
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Orchestrator]] — Quem spawna
- [[projects/42_chat/features/feature-006-agent-dev|006: Agent Dev]] — Quem o QA valida
- Skills de teste (futuro): `gherkin-scenarios`, `go-unit-tests`, `local-test-runner`

## Documentacao de QA (qafiles/)
Materiais coletados da comunidade para fundamentar as futuras skills de teste:
- `bdd-spec/` — Especificacao BDD e Gherkin expert
- `cucumber/` — Fundamentos, melhores praticas, step definitions
- `gherkin-syntax/` — Referencia de sintaxe e organizacao
- `gherkin-practices/` — Anti-patterns e melhores praticas
- `gherkin-examples/` — Exemplos reais
- `tdd/` — TDD workflow, anti-patterns
- `playwright-bdd/` — Playwright + BDD config e sintaxe
- `code/` — Scripts de exemplo (recipe_step_executor.py)

## Relacionado
- [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]]
- `agent-dev` (006) — Quem o QA valida
- `agent-devops` (008) — Standby
- `agent-pentester` (009) — Standby
