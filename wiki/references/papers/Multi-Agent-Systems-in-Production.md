---
title: "Multi-Agent AI Systems in Production (2026)"
tags: [paper, multi-agent, orchestration, failure-propagation, budget, timeout, production-patterns]
status: analyzed
created: 2026-06-20
rag_score: 0.5
source: "https://www.kalviumlabs.ai/blog/multi-agent-ai-systems-when-one-agent-isnt-enough/"
authors: "Anil Gulecha (Kalvium Labs, ex-HackerRank, ex-Google)"
feature: "[[projects/42_Framework/features/005-latte-hardening|Feature 005: LATTE Hardening]]"
base_confidence: 0.95
provenance:
  extracted: 0.9
  inferred: 0.05
  ambiguous: 0.05
summary: "8 projetos multi-agent em produção. 3 padrões de orquestração (pipeline, supervisor, parallel fan-out), failure propagation, cost explosion, e quando NÃO usar multi-agent. Fonte dos gaps 1-7 da Feature 005."
---

# Multi-Agent AI Systems: When One Agent Isn't Enough

> 8 projetos em produção. Quando single agents falham e multi-agent resolve — mas com custos que ninguém documenta.

## Failure Patterns que Forçam Multi-Agent

1. **Context overflow**: 80K tokens de source + message history → esgota contexto antes de completar leitura
2. **Sequential bottlenecks**: 3 análises independentes rodando em série quando poderiam paralelizar
3. **Role conflicts**: Planejar + recuperar + executar no mesmo contexto → decisões piores
4. **Tool count ceiling**: Degradação entre 15-20 ferramentas por agente

## 3 Padrões de Orquestração

| Padrão | Quando usar | Failure mode |
|--------|-------------|--------------|
| **Pipeline** (sequential hand-offs) | Step N depende de N-1 | Um passo falha → pipeline para |
| **Supervisor** (coordinator + specialists) | Roteamento dinâmico entre especialistas | Loop: coordinator chama mesmo agente repetidamente |
| **Parallel Fan-Out** (concurrent + merge) | Tarefas independentes | Race condition em state keys compartilhadas |

## Lições de Produção Relevantes pro LATTE

### 1. Failure Propagation (gap #3)
"Timeout no agente 3 de 5 deixa os outros 4 esperando." Solução: `agent_errors: list` no state + downstream agents verificam antes de executar + fallback_fn por nó.

### 2. Cost Explosion (gap #1)
"Supervisor + 3 specialists × 10 iterações = 40+ LLM calls." Solução: `llm_call_limit` no state, enforce no routing.

### 3. Coordinator Context Saturation (gap #5)
"By turn 8, coordinator decides based on what it read recently." Solução: sumarizar completed tasks a cada 4 turns.

### 4. Agent-to-Agent Evaluation (gap #4)
"LLM-as-judge is inconsistently calibrated — lenient on same model family." Solução: deterministic checks (output format, citations, length) em vez de LLM evaluation.

### 5. Merge Quality (gap #6)
"Synthesis over-indexes on the more detailed input." Solução: instruir explicitamente equal weighting + sinalizar domínios sub-pesquisados.

### 6. Código: Timeout Decorator (gap #2)
```python
def with_timeout(timeout_seconds: int, fallback_fn=None):
    def decorator(node_fn):
        @wraps(node_fn)
        async def wrapper(state):
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(node_fn, state),
                    timeout=timeout_seconds
                )
                return result
            except asyncio.TimeoutError:
                if fallback_fn:
                    return fallback_fn(state)
                return {"agent_errors": [f"{node_fn.__name__} timed out"]}
        return wrapper
    return decorator
```

### 7. Budget Enforcement
```python
class BudgetedState(TypedDict):
    llm_calls_made: int
    llm_call_limit: int

def check_budget(state: BudgetedState) -> str:
    if state["llm_calls_made"] >= state["llm_call_limit"]:
        return "finalize_early"
    return "continue"
```

## Quando NÃO Usar Multi-Agent

"Single agents with well-scoped tool calling handle 70-80% of what startups actually need."
Multi-agent adiciona: debugging complexity, cost (3-10x), latency, state management surface area.
Teste antes de splitar: "Can a single agent with all tools and a good system prompt do this adequately?"

## Problemas Abertos (relevantes pra Feature 002)

- **Shared memory across long-running sessions**: "We've tried embedding-based retrieval of relevant past context, but choosing what's 'relevant' without knowing the current task is hard." → Nossa wiki experiential memory ataca isso.

## Relacionado

- [[references/papers/LangGraph-vs-LangChain|LangGraph vs LangChain]] — decision matrix
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — state pruning, checkpointing
- [[references/papers/LATTE|LATTE]] — coordination graph (referência principal)
- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — alvo dos gaps
- [[projects/42_Framework/features/005-latte-hardening|Feature 005]] — implementação dos gaps 1-7
