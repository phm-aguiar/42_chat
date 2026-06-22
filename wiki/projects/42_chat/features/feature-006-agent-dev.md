---
title: "006: Agent Dev"
category: projects
tags: [sdd, agent, dev, implementacao]
summary: "Persona implementadora do framework SDD. Braço executor spawnado pelo orchestrator como subagente leaf. Skills plugáveis por stack."
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
sources:
  - repo:specs/features/006-agent-dev/spec.md
lifecycle: verified
---

# Feature 006: Agent Dev

> Persona implementadora do framework SDD. Braço executor — spawnado pelo orchestrator.

## Status
✅ **Implementado** — 2026-06-13

## Artefatos
- **Spec:** `specs/features/006-agent-dev/spec.md`
- **Plan:** `specs/features/006-agent-dev/plan.md`
- **Tasks:** `specs/features/006-agent-dev/tasks.md` (6 tasks, 3 fases)
- **Agente:** `.hermes/agents/agent-dev/AGENT.md` + `context.yaml`

## Arquitetura
- **Tipo:** Agente Hermes nativo (AGENT.md + context.yaml)
- **Runtime:** Subagente leaf via `delegate_task` (não delega)
- **Toolsets:** `terminal` + `file`
- **Timeout:** 30 minutos (gerenciado pelo orchestrator)

## Contrato com Orchestrator
- **Entrada:** Contexto compilado (spec, plan, task, skills, tentativa N/3)
- **DONE:** Evidência rastreável (função X → requisito Y, seção Z) + smoke-test output
- **FAIL:** Stack trace + arquivo + linha + possível causa
- **BLOCKED:** Pergunta específica sobre ambiguidade na spec (nunca infere)

## Skills
- **Plugáveis por stack:** Injetadas pelo orchestrator conforme `tech.md`
- **Trilhos, não jaulas:** Usa templates como guia, adapta criativamente se necessário
- **Modo força bruta:** Funciona sem skills (qualidade pode ser menor)

## Regras de Ouro
1. Nunca infere — ambiguidade = BLOCKED
2. Rastreabilidade sempre — todo DONE linka código → spec
3. Smoke-test obrigatório — sem exit code 0, sem DONE
4. Cirúrgico — modifica apenas o necessário
5. Aceita re-spawn — lê erro anterior e ajusta abordagem

## Decisões Arquiteturais (ADRs)
- **ADR-1:** Agente Hermes nativo (mesmo padrão do onboard e orchestrator)
- **ADR-2:** Skills como parâmetro de entrada, não hardcoded (multi-stack)
- **ADR-3:** Comunicação via relatório textual (DONE/FAIL/BLOCKED)
- **ADR-4:** Nunca inferir — reportar BLOCKED

## Dependências
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Orchestrator]] — Orchestrator spawna o agent-dev
- Skills de stack (futuro): `go-implement`, `python-implement`, `smoke-check`

## Relacionado
- [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]] — Quem invoca
- `agent-qa` (007) — QA futuro pode rejeitar e forçar re-spawn
