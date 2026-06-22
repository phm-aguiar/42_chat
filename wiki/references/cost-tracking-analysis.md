---
title: Análise de Custo de Tokens — Hermes + 42_Framework
tags:
  - cost-tracking
  - tokens
  - observability
  - metrics
  - latte
  - hardening
summary: >-
  Análise de como o Hermes Agent já implementa custo de tokens em USD e como
  o 42_Framework (LATTE) pode integrar com esse sistema existente ao invés
  de duplicar lógica de pricing.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
sources:
  - /home/zeenyt__/.hermes/hermes-agent/agent/usage_pricing.py
  - /home/zeenyt__/.hermes/hermes-agent/hermes_state.py
  - /home/zeenyt__/.hermes/hermes-agent/agent/codex_runtime.py
  - /home/zeenyt__/Projetos/42_Framework/.hermes/skills/sdd/latte_coordination/metrics.py
  - /home/zeenyt__/Projetos/42_Framework/.hermes/skills/sdd/latte_coordination/orchestrator.py
  - https://github.com/AgentOps-AI/agentops
---

# Análise de Custo de Tokens — Hermes + 42_Framework

## Descoberta 1: Hermes Já Tem Cost Tracking Embutido

O Hermes Agent (versão atual) **já implementa custo de tokens em USD** completo:

### `agent/usage_pricing.py`

| Componente | Descrição |
|-----------|-----------|
| `PricingEntry` | input/output/cache/reasoning cost **per million tokens** + request cost |
| `CanonicalUsage` | input_tokens, output_tokens, cache_read/write, reasoning_tokens, request_count |
| `estimate_usage_cost()` | Calcula USD real: `tokens * cost_per_million / 1_000_000` |
| `BillingRoute` | Resolve billing model por provider (subscription, pay-per-token) |
| `CostResult` | amount_usd (Decimal), status (actual/estimated/included/unknown) |

### `hermes_state.py`

```sql
estimated_cost_usd REAL,
cost_status TEXT,       -- actual | estimated | included | unknown
cost_source TEXT,       -- provider_cost_api | official_docs | user_override ...
pricing_version TEXT,
billing_provider TEXT,
billing_base_url TEXT,
billing_mode TEXT,
```

### `agent/codex_runtime.py`

A cada chamada LLM:
1. Extrai `input_tokens`, `output_tokens`, `cache_*`, `reasoning_tokens` da resposta
2. Chama `estimate_usage_cost(model, usage, provider, base_url)`
3. Acumula `agent.session_estimated_cost_usd += cost_result.amount_usd`
4. Persiste no session DB via `update_token_counts()`

### Fontes de Pricing

| Fonte | Origem | Exemplo |
|-------|--------|---------|
| `provider_cost_api` | API real do provider | OpenRouter /models endpoint |
| `provider_models_api` | Models API | OpenAI list models |
| `official_docs_snapshot` | Docs estáticos | Tabela embutida no código |
| `user_override` | Config do usuário | Preços customizados |
| `custom_contract` | Contrato especial | Enterprise pricing |

### Display

`hermes config set display.show_cost true` → status bar mostra `~$0.05` por sessão.
Slash command `/usage` → breakdown detalhado.

---

## Descoberta 2: LATTE Tem Budget por Calls, Não por Custo Real

O 42_Framework (LATTE Hardening, Feature 005) tem:

| Mecanismo | O que faz |
|-----------|-----------|
| `max_llm_calls` | Budget por **número de chamadas** |
| `is_budget_exhausted()` | Força finalização quando excede |
| `metrics._compute_tokens_consumed()` | **Heurística**: ~2000 tokens/entrada |
| `force_finalize()` | Marca tasks como `done` com `reason: budget_exhausted` |

**Gap:** Não há tracking de:
- Custo real em USD por sessão
- Preço por modelo (GPT-4o vs GPT-4o-mini têm fator 33x de diferença)
- Cache/reasoning tokens
- Breakdown por modelo no G_final

---

## Descoberta 3: AgentOps Complementa com Self-Host Dashboard

AgentOps (https://github.com/AgentOps-AI/agentops) oferece:

| Funcionalidade | AgentOps | Hermes Nativo | LATTE |
|---------------|----------|---------------|-------|
| Token counting real | ✅ SDK intercepta | ✅ Via responses | ❌ Heurística |
| Custo USD por modelo | ✅ Tabela 400+ modelos | ✅ `usage_pricing.py` | ❌ Ausente |
| Cached tokens | ✅ | ✅ | ❌ |
| Dashboard visual | ✅ SaaS + self-host | ❌ CLI-only | ❌ |
| Session replays | ✅ | ❌ | ❌ |
| Multi-session metrics | ✅ | ✅ `/insights` | ❌ |
| Budget enforcement | ❌ (monitoring only) | ❌ | ✅ `max_llm_calls` |
| Integration LiteLLM | ✅ 100+ providers | ✅ Provider-agnostic | ❌ |

AgentOps usa a biblioteca **tokencost** (`model_prices.json`) como fonte de pricing,
o Hermes usa seu próprio sistema com múltiplas fontes (API cost, docs, override).

---

## Recomendação de Integração

## Fase 1: LATTE Consumir Hermes Cost Tracking ✓ (Implementado)

O LATTE roda **dentro do Hermes** — toda chamada LLM já passa por `estimate_usage_cost()`.
O G_final agora tem `cost_*` fields no metadata propagados do Hermes.

**O que foi implementado:**

### `orchestrator.py` — CoordinationGraph
- Metadados com `cost_estimated_usd`, `cost_status`, `cost_source`, `cost_pricing_version`
- Tokens reais: `cost_total_tokens`, `cost_input_tokens`, `cost_output_tokens`, `cost_cache_tokens`
- Breakdown por modelo: `cost_by_model`
- Propriedades typesafe + setter para cada campo
- Método `update_cost_data()` para propagar do Hermes Agent
- `_force_finalize()` agora inclui cost data nas entries de histórico

### `metrics.py` — `_compute_tokens_consumed()`
- **Prioriza dados reais** se `metadata["cost_total_tokens"] > 0`
- **Fallback** para heurística de ~2000 tokens/entrada se não houver dados reais
- Retorna: `cost_estimated_usd`, `cost_status`, `cost_source`, `cost_input_tokens`, `cost_output_tokens`, `cost_cache_tokens`, `cost_by_model`
- `tokens_per_entry` é `None` quando dados reais (vs inteiro na heurística)
- Docstring atualizada

### Uso
```python
# No orchestrator, após o run() — propagar custo do Hermes:
graph.update_cost_data(
    estimated_usd=agent.session_estimated_cost_usd,
    status=agent.session_cost_status or "estimated",
    source=agent.session_cost_source or "official_docs",
    total_tokens=agent.session_input_tokens + agent.session_output_tokens,
    input_tokens=agent.session_input_tokens,
    output_tokens=agent.session_output_tokens,
    cache_tokens=agent.session_cache_read_tokens,
    by_model={"deepseek/deepseek-v4-flash": {"cost": 0.12, "tokens": 62100}},
    pricing_version=agent.session_cost_pricing_version,
)

# Métricas refletem automaticamente:
metrics = compute_coordination_metrics(G_final)
print(metrics["tokens"]["cost_estimated_usd"])  # 0.15 (real)
print(metrics["tokens"]["cost_source"])          # "official_docs"
```

### Fase 2: Budget Inteligente (Calls + Custo)

```python
# budget pode ser por calls OU por USD:
max_cost_usd: Decimal = Decimal("0.50")  # $0.50 por execução
if agent.session_estimated_cost_usd > max_cost_usd:
    force_finalize(reason="cost_budget_exhausted")
```

### Fase 3: Relatório no G_final

```python
G_final["cost_analysis"] = {
    "estimated_cost_usd": "0.15",
    "tokens_total": 75420,
    "by_model": {
        "deepseek/deepseek-v4-flash": {
            "calls": 12,
            "cost_usd": "0.12",
            "tokens": 62100,
        },
        "deepseek/deepseek-v4-pro": {
            "calls": 3,
            "cost_usd": "0.03",
            "tokens": 13320,
        },
    },
    "cost_status": "estimated",  # actual | estimated | included
    "budget_usd": "0.50",
    "budget_remaining": "0.35",
}
```

---

## Conclusão

1. **Hermes já resolve tracking de custo** — `usage_pricing.py` calcula USD real por modelo, com cache, reasoning, e múltiplas fontes de pricing

2. **LATTE não precisa duplicar pricing** — apenas consumir os valores já disponíveis no `agent.session_estimated_cost_usd`

3. **Budget atual (`max_llm_calls`) é complementar** — pode ser estendido com `max_cost_usd` sem substituir o existente

4. **AgentOps é útil como dashboard self-host** para visualização — não substitui o budget enforcement do LATTE

5. **Heurística de ~2000 tokens/entrada em `metrics.py`** deve ser substituída pelos valores reais do Hermes

## Referências

- [[agentops-observability-platform]] — Wiki do AgentOps
- `agent/usage_pricing.py` — Hermes cost estimation engine
- `hermes_state.py` — SQLite session store com cost columns
- `latte_coordination/metrics.py` — LATTE metrics (heuristic)
- `latte_coordination/orchestrator.py` — LATTE budget enforcement
