---
title: "ADR-002: Timeout Enforcement"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
rag_score: 0.5
---

# ADR-002: Timeout Enforcement — Timeouts por agente, fallback, graceful degradation

## Status
Accepted

## Contexto

O LATTE original dependia exclusivamente do heartbeat (H=4 rounds, ~48s) para detectar workers travados. Isso criava dois problemas: (a) workers downstream ficavam bloqueados esperando o heartbeat detectar o straggler, (b) não havia graceful degradation — o pipeline simplesmente parava.

O paper *Multi-Agent Systems in Production* recomenda timeout preventivo com fallback: *"For some agents, a timeout means 'skip this step and continue with partial results.' For others, it means 'abort the entire workflow.'"* A combinação de timeout preventivo + heartbeat reativo forma duas camadas de proteção com responsabilidades distintas.

## Decisão

Timeout como decorator no dispatcher, heartbeat como safety net:

- Timeout aplicado no `dispatcher.py` via `asyncio.wait_for` com `operator_timeout` segundos (default 45s)
- Se timeout: executa `fallback_fn` registrado por task (default: `{"status": "timeout", "output": "Task exceeded time limit"}`)
- Timeout dispara antes do heartbeat (45s vs 48s), mas heartbeat permanece como safety net para workers que respondem mas não produzem (ex: loop infinito sem timeout de rede)
- Exposição via `--operator-timeout` no CLI e campo `operator-timeout` no frontmatter do `tasks.md`

## Consequências

### Positive
- Workers downstream não ficam bloqueados — recebem fallback imediatamente após timeout
- Graceful degradation: pipeline produz resultado parcial em vez de abortar
- Duas camadas de proteção: timeout (preventivo, 45s) + heartbeat (reativo, 48s)
- Configurável por feature — tasks críticas podem ter timeout maior

### Negative
- Timeout muito agressivo pode cortar tasks legítimas que precisam de mais tempo
- Fallback padrão é genérico — tasks específicas precisam de `fallback_fn` customizado para produzir valor sentinela útil
- `asyncio.wait_for` não captura workers em loop infinito sem await (caso raro com delegate_task)

### Neutral
- Heartbeat mantido como safety net — não substituído, complementado
- Comportamento padrão (sem timeout configurado) preserva comportamento original

## Alternativas Consideradas

**Timeout via `signal.SIGALRM`**
- Rejeitado: (a) SIGALRM é Unix-only, (b) não funciona com `asyncio`, (c) `delegate_task` já é async-compatible. `asyncio.wait_for` é cross-platform e testável.

**Timeout sem fallback (abort completo)**
- Rejeitado: perde trabalho já feito e viola o princípio de resiliência do paper. DAGs com 5+ tasks raramente justificam abort completo por 1 falha.

**Aumentar heartbeat threshold (H=2 em vez de timeout separado)**
- Rejeitado: heartbeat é reativo (detecta após o fato), não preventivo. Workers downstream ainda ficariam bloqueados por 2 rounds (~24s).

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — with_timeout decorator pattern
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-007 original)
- Heartbeat original: `.hermes/skills/sdd/latte_coordination/heartbeat.py`
