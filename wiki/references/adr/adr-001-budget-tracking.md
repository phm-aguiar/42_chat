---
title: "ADR-001: Budget Tracking"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
rag_score: 0.5
---

# ADR-001: Budget Tracking — Limites de custo por sessão multi-agente

## Status
Accepted

## Contexto

No LATTE Coordination Graph (Feature 001), não havia mecanismo de controle de custo por sessão. Runs problemáticos podiam queimar 60-120 LLM calls até abortar no `max_rounds`, sem visibilidade ou enforcement proativo. O paper *Multi-Agent Systems in Production* (Kalvium Labs) identifica budget tracking como gap crítico e recomenda o padrão `BudgetedState`: *"Set the limit before each run based on task complexity. Cap LLM calls at the state level."*

Features têm complexidade heterogênea — uma feature simples pode ter cap=15, uma complexa cap=40. Um budget global no `config.yaml` seria muito restritivo para features complexas ou muito permissivo para simples.

## Decisão

Implementar budget tracking no estado do `CoordinationGraph`, não em sistema separado:

- `llm_calls_made: int = 0` — contador incremental a cada spawn de worker + calls reportadas
- `max_llm_calls: int = 25` — limite configurável por feature (default 25)
- Enforcement no orchestrator: se `llm_calls_made >= max_llm_calls` → `force_finalize()` (marca todas tasks pending como `done` com nota "budget exhausted")
- Exposição via `--max-llm-calls` no CLI e campo `max-llm-calls` no frontmatter do `tasks.md`

## Consequências

### Positive
- Prevenção proativa de runaway loops (antes: 120 calls; depois: cap em 25, -79% tokens)
- Visibilidade completa no `G_final` — budget consumido é reportado como métrica
- Granularidade por feature — cada feature define seu próprio limite baseado em complexidade
- Zero overhead em runs normais (só incrementa contador)

### Negative
- Features complexas podem precisar de `max_llm_calls` maior (requer estimativa prévia do Lead)
- `force_finalize()` pode produzir artefatos incompletos se o cap for muito restritivo
- Workers não têm visibilidade do budget restante (só o orchestrator sabe)

### Neutral
- Budget é tracked no state, não em métricas externas — consistente com ADR-002 original (grafo em memória)
- Não substitui `max_rounds` — são duas camadas independentes de proteção

## Alternativas Consideradas

**Budget global no `config.yaml` do Hermes**
- Rejeitado: features têm complexidade heterogênea — um cap fixo seria muito restritivo para features complexas ou muito permissivo para simples. Budget por feature no `tasks.md` é mais granular.

**Budget como métrica pós-execução (sem enforcement)**
- Rejeitado: não previne runaway loops. O enforcement ativo (`force_finalize`) é necessário para cortar execuções problemáticas.

**Budget baseado em tokens (não em LLM calls)**
- Rejeitado: contar tokens é frágil (depende do tokenizer do modelo) e menos previsível que LLM calls. O paper recomenda LLM calls como unidade.

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — BudgetedState pattern
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-006 original)
- Coordenação LATTE: [[projects/42_Framework/features/001-latte-coordination|Feature 001: LATTE Coordination]]
