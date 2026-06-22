# Tutorial — Feature 005: LATTE Hardening

> **Status:** ✅ 7 patches implementados em `.hermes/skills/sdd/latte_coordination/`
> **Testes de hardening:** ⚠️ Não criados ainda (6 novos testes)
> **Benchmark:** ⚠️ Script existe, relatório vazio

A Feature 005 adiciona **7 melhorias de produção** no LATTE Coordination Graph,
extraídas de papers de multi-agent systems em produção (Kalvium Labs, 8 projetos).

---

## O que são os 7 hardening patches?

### 1. Budget Tracking (crítico)
Antes: runs problemáticos queimavam 60–120 LLM calls até abortar no `max_rounds`.
Depois: `max_llm_calls` (default 25). Se estourar, `force_finalize()` salva o que
já foi feito.

### 2. Timeout por Operador com Fallback (alto)
Antes: heartbeat detectava straggler após 48s, mas workers downstream ficavam
bloqueados. Depois: timeout preventivo de 45s por task. Se estourar, fallback
retorna valor sentinela e a execução continua.

### 3. Partial Failure Propagation (alto)
Antes: se 1 worker falhava, todo o pipeline downstream parava.
Depois: erros são registrados em `errors[]`, workers downstream recebem
`upstream_errors` e decidem: continuar com fallback ou pular.

### 4. Verify Determinístico (médio)
Antes: LLM-as-judge aprovava tudo (leniente com o mesmo modelo).
Depois: 5 checks determinísticos primeiro — formato, artefato existe,
exit code, tamanho mínimo, anti-padrões. Só escala pra LLM se falhar.

### 5. Context Summarization (médio)
Antes: após round 8, o Lead decidia baseado no que leu por último (context
saturation). Depois: a cada 4 rounds, as tasks concluídas são sumarizadas em
1–2 linhas. Lead vê sumário + últimos 4 rounds apenas.

### 6. Equal-Weight Merge (baixo)
Antes: merge over-indexava no output mais detalhado (ex: financeiro 800 palavras
dominava técnico 200 palavras). Depois: prompt de merge instrui peso igual
independente do tamanho + sinaliza domínios sub-pesquisados.

### 7. Tool Ceiling (baixo)
Antes: workers herdavam 20+ ferramentas quando precisavam de 4–6.
Depois: mapeamento por tipo de worker (Dev → `[terminal, file, patch]`,
QA → `[terminal, file]`, DevOps → `[terminal, file]`).

---

## Como usar

### Ativação automática

O hardening é ativado por default quando o `tasks.md` tem `graph-operators: enabled`.
Os parâmetros são configuráveis no frontmatter:

```yaml
---
feature_id: "010"
title: "SDD Templates"
graph-operators: enabled
max-llm-calls: 25          # budget de LLM calls (default)
operator-timeout: 45        # timeout por task em segundos
verify-mode: deterministic  # "deterministic" ou "llm"
---
```

Se quiser comportamento **exatamente igual ao anterior** (pré-hardening):

```yaml
max-llm-calls: 0      # 0 = sem limite
operator-timeout: 0   # 0 = sem timeout
verify-mode: llm      # pula checks determinísticos
```

### Cenários

#### Cenário 1: Run normal (5 tasks, sem falhas)
Budget não atingido, nenhum timeout, verify determinístico aprova tudo.
→ Comportamento idêntico ao atual, sem overhead perceptível.

#### Cenário 2: Worker com timeout
```
T003 estoura 45s. Timeout dispara fallback.
T004 e T005 verificam `errors`, encontram "T003: timeout",
prosseguem com fallback.
```
→ Antes: pipeline aborta. Depois: resultado parcial em -50% wall-clock.

#### Cenário 3: Budget estourado (loop)
```
Coordenador em loop chama mesmo worker 25 vezes.
Cap aciona → force_finalize com o que tem.
```
→ Antes: 40 rounds × 3 workers = 120 calls. Depois: 25 calls, -79% tokens.

#### Cenário 4: Verify pega falha real
```
Worker gera output truncado (arquivo vazio).
Check determinístico detecta `size == 0`.
Não escala pra LLM.
```
→ Antes: LLM aprovaria (falso positivo). Depois: reprova em 0.1s.

#### Cenário 5: Merge com domínio sub-pesquisado
```
3 workers: financeiro (800 palavras), técnico (200), mercado (200).
Merge pesa igualmente e sinaliza sub-pesquisa.
```
→ Antes: merge puxava pro financeiro. Depois: balanceado + alerta.

---

## Tasks implementadas (20, 60% paralelizáveis)

| T | Patch | Status | Arquivo |
|---|-------|--------|---------|
| T001 | State estendido | ✅ | `orchestrator.py` |
| T002 | CLI/config params | ✅ | `orchestrator.py` |
| T003 | Budget tracking | ✅ | `orchestrator.py`, `dispatcher.py` |
| T004 | Timeout + fallback | ✅ | `dispatcher.py` |
| T005 | Partial failure prop. | ✅ | `dispatcher.py`, `frontier.py` |
| T006 | Verify determinístico | ✅ | `lead_operators.py` |
| T007 | Context summarization | ✅ | `orchestrator.py` |
| T008 | Equal-weight merge | ✅ | `dispatcher.py` |
| T009 | Tool ceiling | ✅ | `dispatcher.py` |
| T010 | Test budget | ⚠️ | `test_budget.py` |
| T011 | Test timeout | ⚠️ | `test_timeout.py` |
| T012 | Test partial failure | ⚠️ | `test_partial_failure.py` |
| T013 | Test verify det. | ⚠️ | `test_verify_deterministic.py` |
| T014 | Test summarization | ⚠️ | `test_summarization.py` |
| T015 | Test merge | ⚠️ | `test_merge.py` |
| T016 | Test tool ceiling | ⚠️ | `test_tool_ceiling.py` |
| T017 | Regressão (39 testes) | ✅ | Todos existentes |
| T018 | Benchmark | ⚠️ | Script existe, relatório vazio |
| T019 | Docs wiki | ⚠️ | Pendente |
| T020 | Reindex wiki | ⚠️ | Pendente |

---

## Rodar os testes atuais (verificar regressão)

```bash
cd /home/zeenyt__/Projetos/42_chat
PYTHONPATH=.hermes/skills/sdd python3 -m pytest \
  .hermes/skills/sdd/latte_coordination/tests/ -v
```

Devem passar 39 testes. Se algum falhar, alguma mudança quebrou
retrocompatibilidade.

---

## Benchmark

O benchmark roda um cenário de stress com DAG de 5 tasks, 1 worker com timeout
forçado. Métricas comparativas: LLM calls, wall-clock, resultado parcial vs
abort, verify accuracy.

```bash
cd /home/zeenyt__/Projetos/42_chat
PYTHONPATH=.hermes/skills/sdd/latte_coordination \
  python3 specs/features/005-latte-hardening/benchmark/run_benchmark.py
```

---

## ADRs

| ADR | Decisão | Por quê |
|---|---|---|
| ADR-006 | Budget no state, não em config global | Budget por feature (simples=15, complexa=40) |
| ADR-007 | Timeout no dispatcher, heartbeat como safety net | 2 camadas: preventivo (45s) + reativo (H rounds) |
| ADR-008 | Partial failure em `errors[]`, não como exceção | Grafo absorve falhas, não aborta |
| ADR-009 | Verify determinístico 1º, LLM como fallback | Zero tokens pra checks estruturais |
| ADR-010 | Summarization a cada 4 rounds | Sweet spot do paper Kalvium |
| ADR-011 | Toolsets via `delegate_task` | API nativa, ~2K tokens economizados |
| ADR-012 | Equal-weight como prompt engineering | 20 tokens de prompt, zero complexidade |
