---
title: "LangGraph in Production — StateGraph, Checkpointing e Human-in-the-Loop"
tags: [paper, langgraph, stateful-agents, checkpointing, human-in-the-loop, production-patterns]
status: analyzed
created: 2026-06-19
rag_score: 0.5
source: "https://www.kalviumlabs.ai/blog/langgraph-in-production-stateful-multi-step-agents/"
authors: "Anil Gulecha (Kalvium Labs, ex-HackerRank, ex-Google)"
feature: "nenhuma ainda — candidato a Feature 003"
---

# LangGraph in Production

> Padrões de produção para agentes stateful: StateGraph, checkpointing, human-in-the-loop e state pruning. 6 agentes em produção, lições reais.

## Resumo

Artigo de engenharia do Kalvium Labs documentando 6 agentes LangGraph em produção. Foco em: design de state schema (acumuladores vs overwrites, manter state enxuto), checkpointing (MemorySaver → SqliteSaver → PostgresSaver), human-in-the-loop (interrupt_before + update_state + resume), e armadilhas reais (state crescendo a 3MB, re-invocações duplicando acumuladores, loops infinitos sem iteration limit).

## Padrões Extraídos

| Padrão | Descrição | Gap no 42_Framework |
|---|---|---|
| **StateGraph** | Agente como DAG tipado com reducers | ✅ LATTE Coordination Graph |
| **Checkpointing** | Persistência automática por thread ID | ❌ G_t só em memória (ADR-002) |
| **Human-in-the-loop** | interrupt_before + update_state + resume | ⚠️ Gates manuais, não integrados ao grafo |
| **State pruning** | "Keep state lean — 10KB max" | ❌ Histórico I8 cresce sem limite |
| **Accumulator vs overwrite** | Annotated[list, add] vs plain types | ✅ Status transitions no grafo |
| **Iteration limits** | iteration_count >= 15 → force_finalize | ⚠️ Só max-rounds=40, sem force finalize |
| **Error recovery** | error_count + conditional routing | ⚠️ Só heartbeat (detecta inatividade) |
| **Thread IDs** | Sessões isoladas por thread_id | ✅ Feature ID como namespace |

## Lições de Produção

1. **"State grew to 3MB per checkpoint"** — resolvido com state pruning agressivo (só IDs, não conteúdo)
2. **"Re-invocações duplicavam accumulator fields"** — resolvido passando `None` no resume
3. **"80 iterações em documento malformado"** — resolvido com `iteration_count` + force_finalize
4. **"interrupt_after vs interrupt_before"** — usar interrupt_before quando a ação precisa de aprovação
5. **"Checkpointing: 45min com LangGraph, 1 semana sem"** — persistência como diferencial competitivo

## Aplicação Potencial no 42_Framework

### Candidato a Feature 003: LangGraph Patterns

1. **Checkpointing do G_t**: persistir a cada round (SQLite, ~10KB/snapshot). Recovery de crash, resume de onde parou.
2. **Force-finalize**: em vez de abortar no max-rounds, força Close nas tasks restantes e sintetiza resultado parcial.
3. **State pruning**: histórico I8 mantém só últimos 10 rounds ativos, arquiva o resto.
4. **Human-in-the-loop formal**: modelar gates de aprovação como nós `approval_gate` no coordination graph.

### Decisão

Adiado — consolidar features 001+002 primeiro com feature real (003 de domínio), depois avaliar checkpointing/force-finalize como patches na 001.

## Relacionado

- [[references/papers/LATTE|LATTE]] — coordination graph dinâmico (referência principal)
- [[references/papers/A-MapReduce|A-MapReduce]] — memória experiencial e feedback loop
- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — LATTE implementado
- [[projects/42_Framework/features/002-experiential-memory|Feature 002]] — Wiki Experiential Memory
- [[concepts/sdd-workflow|SDD Workflow]] — pipeline com agentes stateful
- [[concepts/sdd|SDD]] — metodologia base
- [[skills/agent-run|agent-run]] — runtime alvo para checkpointing
