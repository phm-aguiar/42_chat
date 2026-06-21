---
title: "ADR-003: Failure Propagation"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
---

# ADR-003: Failure Propagation — Como falhas em subagentes propagam para o orchestrator

## Status
Accepted

## Contexto

No LATTE original, quando um worker falhava, não havia mecanismo de propagação de falha para workers downstream. O pipeline simplesmente parava ou produzia resultados inconsistentes sem indicação de degradação. O paper *Multi-Agent Systems in Production* é taxativo: *"Never silently drop a failure and continue, because the final output will look complete but the user has no way to know that a step was skipped."*

O LangGraph-in-Production reporta padrão similar com `error_count` no state. A abordagem correta é: (a) downstream workers sabem que input é degradado, (b) `G_final` mostra quais tasks falharam, (c) o usuário vê os erros no output final.

## Decisão

Partial failure como state field (`errors`), não como exceção:

- `errors: list[dict]` no `CoordinationGraph` (campo com reducer `add` — acumula, não sobrescreve)
- Workers downstream recebem `upstream_errors` no context scoping e decidem: continuar com fallback ou pular
- Nenhuma exceção é lançada no orchestrator — o grafo absorve falhas
- `compute_frontier()` marca nós com upstream errors como `ready_with_degraded_input`
- `G_final` reporta `errors` por task no formato: `[{"task": "T003", "error": "timeout", "timestamp": "..."}]`

## Consequências

### Positive
- Resiliência: 1 falha não bloqueia o restante do DAG (ex: T003 falha, T004-T010 continuam)
- Transparência: usuário vê exatamente quais tasks falharam e por quê
- Workers downstream podem tomar decisões informadas (continuar com dados degradados vs pular)
- Padrão consistente com LangGraph `error_count` e recomendações do paper

### Negative
- Workers precisam de lógica adicional para lidar com `upstream_errors` (complexidade extra no agent prompt)
- Resultado parcial pode dar falsa sensação de completude se o usuário não verificar `errors`
- Cascata de degradação: se T003 falha e T004 depende de T003, T004 também pode produzir output degradado

### Neutral
- Comportamento padrão (sem `errors`) preserva execução original
- Operadores `Release` e `Close` agora registram em `errors` quando acionados

## Alternativas Consideradas

**Lançar exceção e abortar pipeline**
- Rejeitado: (a) perde trabalho já feito, (b) viola o princípio de resiliência do paper, (c) DAGs com 5+ tasks raramente justificam abort completo por 1 falha.

**Silent failure (ignorar e continuar)**
- Rejeitado: viola recomendação explícita do paper. O usuário precisa saber que uma step foi pulada — output que parece completo mas tem gaps é pior que output explicitamente parcial.

**Retry automático antes de propagar falha**
- Rejeitado: retry já existe como política separada (máx 3 tentativas no orchestrator original). Falha após retry deve ser propagada, não retentada indefinidamente.

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — failure propagation pattern
- Paper: *LangGraph in Production* — error_count state pattern
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-008 original)
- Frontier module: `.hermes/skills/sdd/latte_coordination/frontier.py`
