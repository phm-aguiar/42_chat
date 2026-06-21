---
feature_id: "005"
title: "LATTE Hardening — Budget, Timeout, Failure Propagation & Quality Gates"
status: draft
created: "2026-06-20"
author: phm-aguiar
tags: [sdd, latte, hardening, budget, timeout, failure-propagation, verify, merge, tool-ceiling]
based_on:
  - "specs/features/001-latte-coordination/ (LATTE base)"
  - "wiki/references/papers/Multi-Agent-Systems-in-Production.md (gaps 1-7)"
  - "wiki/references/papers/LangGraph-vs-LangChain.md (validação custom loop)"
  - "wiki/references/papers/LangGraph-in-Production.md (state pruning patterns)"
depends_on:
  - "001-latte-coordination (módulos orchestrator, dispatcher, heartbeat, lead_operators, worker_operators, metrics, graph_persistence)"
---

**Aprovado:** true

# LATTE Hardening — Budget, Timeout, Failure Propagation & Quality Gates

> 7 melhorias de produção no LATTE Coordination Graph, extraídas de papers de multi-agent systems em produção (Kalvium Labs, 8 projetos).

## Propósito

O LATTE (Feature 001) funciona para coordenação multi-agente mas tem 7 gaps de produção identificados por papers de engenharia real:

1. **Sem budget tracking**: runs problemáticos queimam 60-120 LLM calls até abortar no max_rounds
2. **Sem timeout por operador**: heartbeat detecta straggler após 48s, mas workers downstream ficam bloqueados
3. **Sem partial failure propagation**: se 1 worker falha, todo o pipeline downstream para
4. **Verify cosmético**: LLM-as-judge é leniente consigo mesmo (mesmo modelo), raramente reprova
5. **Coordinator context saturation**: após round 8, Lead decide baseado no que leu por último
6. **Merge quality degradation**: síntese pós fan-out over-indexa no output mais detalhado
7. **Tool count ceiling**: workers herdam 20+ ferramentas quando precisam de 4-6

**Esta feature entrega:** os 7 hardening patches no LATTE, com benchmark comparativo (antes × depois).

## Escopo

### Mudança 1: Budget Tracking (CRÍTICO)
- Adicionar `max_llm_calls` (default 25) e `llm_calls_made` ao CoordinationGraph state
- Enforce no orchestrator: se `llm_calls_made >= max_llm_calls` → force_finalize
- Incrementar contador no dispatcher (cada spawn de worker conta como 1 call + calls internas reportadas)
- Expor `--max-llm-calls` no CLI do orchestrator

### Mudança 2: Timeout por Operador com Fallback (ALTO)
- Adicionar timeout por task no dispatcher (configurável, default 45s)
- Adicionar `fallback_fn` por task: função que retorna valor sentinela se timeout
- Fallback padrão: `{"status": "timeout", "output": "Task exceeded time limit"}`
- Integrar com heartbeat: timeout é preventivo (corta antes dos 4 rounds); heartbeat é reativo (detecta após)
- Expor `--operator-timeout` no CLI

### Mudança 3: Partial Failure Propagation (ALTO)
- Adicionar `errors: Annotated[list, add]` ao CoordinationGraph state
- Workers downstream verificam `state["errors"]` antes de executar
- Se upstream tem erro, worker decide: continuar com fallback ou pular
- Conditional routing baseado em `has_upstream_errors()`
- Modificar `compute_frontier()` para considerar nós com upstream errors como "ready with degraded input"

### Mudança 4: Verify Determinístico (MÉDIO)
- Adicionar `verify_mode` ao CoordinationGraph: `"llm"` (atual) ou `"deterministic"` (novo)
- Modo deterministic: checks estruturais antes do LLM
  - Output format validation (JSON válido? campos esperados?)
  - Artefact existence (arquivo criado? não vazio?)
  - Exit code check (`exit_code == 0`)
  - Minimum output size (≥ N chars)
  - Anti-pattern detection ("I will create", "Let me plan" sem ação)
- Só escala pra LLM se checks determinísticos falharem
- Modo padrão: `"deterministic"` (LLM só como fallback)

### Mudança 5: Coordinator Context Summarization (MÉDIO)
- Adicionar `completed_summary: str` ao CoordinationGraph state
- A cada 4 rounds, sumarizar `completed_tasks` em 1-2 linhas
- Template: "summarized: [task1] e [task2] concluídas, [key_finding]"
- Lead recebe sumário + últimos 4 rounds, não histórico completo
- Opcional (não ativa se `completed_tasks` < 5)

### Mudança 6: Equal-Weight Merge (BAIXO)
- Modificar prompt de merge no dispatcher para instruir equal weighting
- Adicionar constraint: "Weight each input equally regardless of length"
- Sinalizar domínios sub-pesquisados: "Note: [domain] was under-researched"

### Mudança 7: Tool Ceiling (BAIXO)
- Adicionar `toolsets` por task no dispatcher (já suportado pelo delegate_task)
- Mapear tipos de task → toolsets recomendados:
  - Dev: terminal, file, patch, read_file, search_files
  - QA: terminal, file, read_file, search_files
  - DevOps: terminal, file, docker, process
- Expor no tasks.md: `toolsets: [terminal, file]`

### Benchmark (OBRIGATÓRIO)
- Rodar suíte de testes atual (39 testes) como baseline
- Rodar após cada mudança implementada
- Cenário de stress: DAG com 5 tasks, 1 worker com timeout forçado, coordinator loop
- Métricas comparativas:
  - LLM calls total
  - Wall-clock time
  - Runs que produzem resultado parcial vs abort
  - Verify accuracy (falsos positivos/negativos)

Fora do escopo:
- Migração para LangGraph (ADR-002 confirmado: grafo em memória é suficiente)
- Checkpointing do G_t (postergado — ver LangGraph-in-Production.md)
- Human-in-the-loop formal (postergado)
- State pruning (G_t já é efêmero por ADR-002)

## Constraints

- Retrocompatibilidade: modo legacy (tasks.md sem `graph-operators: enabled`) não é afetado
- Todos os 39 testes existentes devem continuar passando
- Novas funcionalidades são configuráveis (flags/parâmetros com defaults que preservam comportamento atual)
- Mudanças no `orchestrator.py` (1383 linhas) são as mais sensíveis — preferir patches cirúrgicos
- `delegate_task` já suporta `toolsets` — usar API existente, não reinventar
- Benchmark deve usar infra real (não mock), com `delegate_task` chamando workers reais
- Python 3.10+, sem novas dependências externas

## Cenários de Uso

### Cenário 1: Run normal (5 tasks, sem falhas)
Budget não atingido, nenhum timeout, verify determinístico aprova tudo.
→ Comportamento idêntico ao atual, sem overhead perceptível.

### Cenário 2: Worker com timeout
T003 estoura 45s. Timeout dispara fallback. T004 e T005 verificam `errors`, encontram "T003: timeout", prosseguem com fallback.
→ Antes: pipeline aborta. Depois: resultado parcial em -50% wall-clock.

### Cenário 3: Budget estourado (loop)
Coordenador em loop chama mesmo worker 25 vezes. Cap aciona → force_finalize com o que tem.
→ Antes: 40 rounds × 3 workers = 120 calls. Depois: 25 calls, -79% tokens.

### Cenário 4: Verify pega falha real
Worker gera output truncado (arquivo vazio). Check determinístico detecta `size == 0`. Não escala pra LLM.
→ Antes: LLM aprovaria (falso positivo). Depois: reprova em 0.1s.

### Cenário 5: Merge com domínio sub-pesquisado
3 workers: financeiro (800 palavras), técnico (200), mercado (200). Merge pesa igualmente e sinaliza.
→ Antes: merge puxava pro financeiro. Depois: balanceado + alerta de sub-pesquisa.

## Critérios de Sucesso

- [ ] 39 testes existentes passam (sem regressão)
- [ ] Novos testes: budget, timeout, failure propagation, verify deterministic, context summary, merge, tool ceiling
- [ ] Benchmark: -60% tokens, -50% wall-clock em cenário com 1 straggler
- [ ] Benchmark: -79% tokens em cenário de loop (budget cap)
- [ ] Verify determinístico: < 5% falsos positivos em cenário com falha real
- [ ] Modo legacy inalterado (test T018)
