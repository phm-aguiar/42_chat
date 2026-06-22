---
feature_id: "005"
tasks_for: "LATTE Hardening — Budget, Timeout, Failure Propagation & Quality Gates"
spec: "specs/features/005-latte-hardening/spec.md"
plan: "specs/features/005-latte-hardening/plan.md"
created: "2026-06-20"
author: phm-aguiar
graph-operators: enabled
heartbeat-threshold: 4
max-rounds: 20
max-llm-calls: 25
operator-timeout: 45
verify-mode: deterministic
---

# Tasks — LATTE Hardening

> **Status geral:** Fase 1-2 ✅ (T001-T009 implementados) | Fase 3 ⚠️ (T010-T016 pendentes) | Fase 4 ⚠️ (T018-T020 pendentes)

## Fase 1: Fundação (State Schema + Config)

### T001 — Extend CoordinationGraph State `[x]`
- **Papel:** Dev
- **Dependências:** ~
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/orchestrator.py` (class CoordinationGraph)
- **Descrição:** Adicionar 7 novos campos ao CoordinationGraph state: `llm_calls_made` (int=0), `max_llm_calls` (int=25), `errors` (list[dict]=[]), `completed_summary` (str=""), `round_since_summary` (int=0), `operator_timeout` (int=45), `verify_mode` (str="deterministic"). Campos com defaults preservam comportamento atual.

### T002 — Add CLI/Config Parameters to Orchestrator `[x]`
- **Papel:** Dev
- **Dependências:** T001
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/orchestrator.py` (`__init__` signature + `run()`)
- **Descrição:** Adicionar `--max-llm-calls`, `--operator-timeout`, `--verify-mode` como parâmetros do `CoordinationGraph.__init__()`. Ler de `tasks.md` frontmatter se disponível (ex: `max-llm-calls: 25`). Expor no `run()`.

## Fase 2: Implementação (Core Changes)

### T003 — Budget Tracking `[x]`
- **Papel:** Dev
- **Dependências:** T001
- **Paralelizável:** true (arquivos disjuntos com T004-T009? Não — T003-T009 tocam orchestrator.py e dispatcher.py que são compartilhados)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/orchestrator.py` (loop principal, force_finalize)
  - `.hermes/skills/sdd/latte_coordination/dispatcher.py` (incrementar llm_calls_made por spawn)
- **Descrição:** No orchestrator: antes de cada round, `check_budget()` — se `llm_calls_made >= max_llm_calls` → `force_finalize()` (marca todas tasks pending como `done` com note "budget exhausted"). No dispatcher: incrementar `llm_calls_made` a cada spawn + calls reportadas pelo worker.

### T004 — Timeout + Fallback `[x]`
- **Papel:** Dev
- **Dependências:** T001
- **Paralelizável:** false (compartilha dispatcher.py com T003, T005, T008, T009)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/dispatcher.py` (dispatch com timeout)
- **Descrição:** Envolver `delegate_task` call em `asyncio.wait_for(timeout=operator_timeout)`. Se `TimeoutError`: executar `fallback_fn` da task (default: retorna `{"status": "timeout", "output": "Task exceeded time limit"}`) + registrar em `errors`. Timeout é preventivo — heartbeat (reativo) permanece como safety net.

### T005 — Partial Failure Propagation `[x]`
- **Papel:** Dev
- **Dependências:** T001, T004
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/dispatcher.py` (context scoping com upstream_errors)
  - `.hermes/skills/sdd/latte_coordination/frontier.py` (compute_frontier considera erro)
- **Descrição:** Dispatcher injeta `upstream_errors` no context scoping. Worker decide: continuar com fallback ou skip. Frontier: nós com upstream errors são marcados `ready_with_degraded_input`. G_final reporta `errors` por task.

### T006 — Verify Determinístico `[x]`
- **Papel:** Dev
- **Dependências:** T001
- **Paralelizável:** false (compartilha lead_operators.py com T007? Não — lead_operators não é alvo de T007)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/lead_operators.py` (Verify operator)
- **Descrição:** Adicionar `_deterministic_checks(output)` com 5 checks: (1) formato válido, (2) artefato existe, (3) exit code=0, (4) tamanho mínimo, (5) anti-padrões. Se `verify_mode == "deterministic"`: roda checks primeiro, só escala pra LLM se falhar. Se `verify_mode == "llm"`: comportamento atual.

### T007 — Context Summarization `[x]`
- **Papel:** Dev
- **Dependências:** T001
- **Paralelizável:** true (lead_operators.py é disjunto de dispatcher.py? Sim, T006 toca lead_operators.py, T007 toca orchestrator.py)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/orchestrator.py` (summarization trigger)
- **Descrição:** A cada 4 rounds (`round_since_summary >= 4`), sumarizar `completed_tasks` em 1-2 linhas no campo `completed_summary`. Template: "Resumo (rounds 1-4): [T001, T002] concluídas. [T001] implementou X, [T002] configurou Y." Lead recebe `completed_summary` + últimos 4 rounds. Reset `round_since_summary` após sumarização.

### T008 — Equal-Weight Merge `[x]`
- **Papel:** Dev
- **Dependências:** ~
- **Paralelizável:** true (prompt engineering, não toca lógica de estado)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/dispatcher.py` (prompt de merge)
- **Descrição:** Adicionar constraint no prompt de merge: "Weight each input equally regardless of length. Note when a domain was under-researched (< 100 words)."

### T009 — Tool Ceiling `[x]`
- **Papel:** Dev
- **Dependências:** ~
- **Paralelizável:** true (usa API existente do delegate_task)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/dispatcher.py` (mapeamento task type → toolsets)
- **Descrição:** Adicionar `TOOLSET_MAP` no dispatcher: Dev → `[terminal, file, patch]`, QA → `[terminal, file]`, DevOps → `[terminal, file]`. Passar `toolsets` no `delegate_task` spawn. Configurável por task no `tasks.md` (campo `toolsets:`).

## Fase 3: Validação (Testes) — ⚠️ Pendente

> Nenhum dos 6 arquivos de teste existe ainda. T017 (regressão 39 testes) é o único verificado.

### T010 — Test Budget Tracking `[ ]`
- **Papel:** QA
- **Dependências:** T003
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_budget.py` (novo)
- **Descrição:** Testes: (a) budget não atingido → execução normal, (b) budget atingido → force_finalize, (c) llm_calls_made incrementa corretamente, (d) G_final reporta budget info.

### T011 — Test Timeout + Fallback `[ ]`
- **Papel:** QA
- **Dependências:** T004
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_timeout.py` (novo)
- **Descrição:** Testes: (a) timeout dispara fallback_fn, (b) fallback produz valor sentinela, (c) errors registra timeout, (d) heartbeat NÃO dispara se timeout já tratou.

### T012 — Test Partial Failure Propagation `[ ]`
- **Papel:** QA
- **Dependências:** T005
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_partial_failure.py` (novo)
- **Descrição:** Testes: (a) upstream error → downstream recebe `upstream_errors`, (b) downstream decide continuar com fallback, (c) downstream decide skip, (d) G_final reporta errors por task, (e) cascata: 1 falha não bloqueia 4 outras tasks.

### T013 — Test Verify Determinístico `[ ]`
- **Papel:** QA
- **Dependências:** T006
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_verify_deterministic.py` (novo)
- **Descrição:** Testes: (a) output válido → checks passam, sem LLM call, (b) output truncado → checks falham, escala pra LLM, (c) anti-padrão "I will create" → reprovado, (d) verify_mode=llm → comportamento atual.

### T014 — Test Context Summarization `[ ]`
- **Papel:** QA
- **Dependências:** T007
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_summarization.py` (novo)
- **Descrição:** Testes: (a) sumarização dispara a cada 4 rounds, (b) completed_summary contém tasks concluídas, (c) round_since_summary reseta, (d) < 5 completed_tasks → não sumariza.

### T015 — Test Equal-Weight Merge `[ ]`
- **Papel:** QA
- **Dependências:** T008
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_merge.py` (novo)
- **Descrição:** Testes: (a) prompt de merge contém constraint de equal-weight, (b) merge com outputs de tamanhos diferentes não over-indexa no maior (validação estrutural, não semântica).

### T016 — Test Tool Ceiling `[ ]`
- **Papel:** QA
- **Dependências:** T009
- **Paralelizável:** true
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/test_tool_ceiling.py` (novo)
- **Descrição:** Testes: (a) worker Dev recebe toolsets `[terminal, file, patch]`, (b) worker QA recebe `[terminal, file]`, (c) toolsets custom no tasks.md sobrepõe default, (d) delegate_task é chamado com toolsets correto.

### T017 — Regression: 39 Existing Tests Pass `[x]`
- **Papel:** QA
- **Dependências:** T001, T002, T003, T004, T005, T006, T007, T008, T009
- **Paralelizável:** false (depende de todas as mudanças)
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/` (todos existentes)
- **Descrição:** Rodar `PYTHONPATH=.hermes/skills/sdd python3 -m pytest .hermes/skills/sdd/latte_coordination/tests/ -q`. Todos os 39 testes devem passar.

## Fase 4: Benchmark & Documentação — ⚠️ Pendente

> Script run_benchmark.py existe mas benchmark.md está vazio. T019-T020 não iniciados.

### T018 — Benchmark Comparativo `[ ]`
- **Papel:** DevOps
- **Dependências:** T017
- **Paralelizável:** false
- **Arquivos:**
  - `.hermes/skills/sdd/latte_coordination/tests/benchmark/` (novo)
  - `specs/features/005-latte-hardening/benchmark.md` (atualizar — vazio)
- **Descrição:** Cenário de stress: DAG com 5 tasks, 1 worker com timeout forçado. Métricas: LLM calls, wall-clock, runs com resultado parcial vs abort, verify accuracy. Rodar com e sem hardening. Reportar delta.

### T019 — Update Wiki Docs `[ ]`
- **Papel:** Dev
- **Dependências:** T017
- **Paralelizável:** true
- **Arquivos:**
  - `wiki/projects/42_Framework/features/001-latte-coordination.md` (novos campos)
  - `wiki/references/papers/LangGraph-in-Production.md` (status → partially_addressed)
- **Descrição:** Atualizar página da Feature 001 com novos campos do CoordinationGraph. Atualizar status do paper LangGraph-in-Production.

### T020 — Reindex Wiki `[ ]`
- **Papel:** DevOps
- **Dependências:** T019
- **Paralelizável:** false
- **Arquivos:**
  - `~/.hermes/wiki_index.db` (índice SQLite)
- **Descrição:** `python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full --wiki-dir wiki/`

---

## Coordination Graph (G₀)

```
T001 ──→ T002 ──→ T003 ──→ T010
  │                │
  ├──→ T004 ──→ T011
  │      │
  │      └──→ T005 ──→ T012
  │
  ├──→ T006 ──→ T013
  │
  ├──→ T007 ──→ T014
  │
  ├──→ T008 ──→ T015
  │
  └──→ T009 ──→ T016

T003 ─┐
T004 ─┤
T005 ─┤
T006 ─┼──→ T017 ──→ T018
T007 ─┤              │
T008 ─┤              ├──→ T019 ──→ T020
T009 ─┘              │
                     └──→ benchmark.md
```

## Paralelismo

| Batch | Tasks | Razão |
|-------|-------|-------|
| Batch 1 (sequencial) | T001 | Fundação — todos dependem |
| Batch 2 (sequencial) | T002 | Depende de T001 |
| Batch 3 (paralelo) | T003, T004, T006, T007, T008, T009 | T003/T004/T005 tocam dispatcher.py — NÃO podem paralelizar entre si. Mas T006 (lead_operators.py) é disjunto de T007 (orchestrator.py) e T008/T009 (dispatcher.py). Na prática: T006 ∥ T007 ∥ T008 ∥ T009 podem rodar juntos. T003/T004/T005 são sequenciais entre si (compartilham dispatcher.py). |
| Batch 4 (sequencial) | T005 | Depende de T004 + T001 |
| Batch 5 (paralelo) | T010, T011, T012, T013, T014, T015, T016 | Testes são disjuntos (arquivos .py diferentes) |
| Batch 6 (sequencial) | T017 | Depende de todos os testes |
| Batch 7 (sequencial) | T018 | Depende de T017 |
| Batch 8 (paralelo) | T019 ∥ benchmark.md | Disjuntos |
| Batch 9 (sequencial) | T020 | Depende de T019 |

**Resumo:** 20 tasks, 9 batches. ~60% das tasks são paralelizáveis nos batches 3, 5, 8.

**Progresso:** 9/20 implementados (T001-T009) | 1/20 verificado (T017 regressão) | 10/20 pendentes (T010-T016 + T018-T020)
