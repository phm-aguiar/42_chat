---
feature_id: "005"
title: "LATTE Hardening Benchmark"
created: "2026-06-20"
---

# Benchmark — LATTE Hardening

## Cenário

DAG com 5 tasks, 1 worker (T003) com timeout forçado + output contendo anti-padrões.

## Resultados

| Métrica | Before | After | Delta |
|---------|--------|-------|-------|
| **LLM calls** | 60/999 | 27/25 | **-55%** |
| **Rounds** | 20 | 10 | **-50%** |
| **Budget exhausted** | False | True | ✓ |
| **Wall-clock** | 2ms | 1ms | -50%* |
| **Verify checks** | 3/5 pass | 3/5 pass | — |

*Wall-clock é baixo porque workers são stubs. Em produção com delegate_task real, a redução seria proporcional ao número de rounds economizados.

## Verify Deterministic Checks (T003 output)

T003 output: `"I will create the computation pipeline. Let me plan the architecture first. Error: connection timeout after 30s"`

| Check | Result |
|-------|--------|
| non_empty_output | ✓ PASS (101 chars) |
| no_planning_anti_pattern | ✗ FAIL ("I will create") |
| minimum_output_size | ✓ PASS (101 chars) |
| no_error_traceback | ✗ FAIL ("Error: connection timeout") |
| artifact_exists | ✓ PASS (no file references) |

**2/5 checks falharam** — Verify escalaria pra LLM (comportamento correto).

## Validações

- [✓] Budget enforcement acionou (`budget_exhausted=True`)
- [✓] Verify detecta anti-padrões e tracebacks
- [✓] Context summarization tracking ativo
- [✓] TOOLSET_MAP populado (4 roles)
- [✓] MERGE_EQUAL_WEIGHT_INSTRUCTION presente
- [✓] 39 testes existentes passam (sem regressão)
