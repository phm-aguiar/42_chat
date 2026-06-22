---
title: "LangGraph vs LangChain: Which We Deploy in Production (2026)"
tags: [paper, langgraph, langchain, framework-comparison, production, decision-matrix]
status: analyzed
created: 2026-06-20
rag_score: 0.5
source: "https://www.kalviumlabs.ai/blog/langgraph-vs-langchain-production/"
authors: "Anil Gulecha (Kalvium Labs, ex-HackerRank, ex-Google)"
feature: "[[projects/42_Framework/features/005-latte-hardening|Feature 005: LATTE Hardening]]"
base_confidence: 0.9
provenance:
  extracted: 0.85
  inferred: 0.1
  ambiguous: 0.05
summary: "8 de 12 projetos começaram LangChain, 4 migraram pra LangGraph. Decision matrix: quando cada um, padrões de produção, e quando custom loop é superior. Valida LATTE como custom loop."
---

# LangGraph vs LangChain in Production

> 12 projetos. 4 rewrites. O que quebrou, o que LangGraph resolve, e quando custom loop é melhor que ambos.

## O Que Cada Um Faz Bem

| Framework | Bom pra | Ruim pra |
|-----------|---------|----------|
| **LangChain (LCEL)** | RAG pipelines, document Q&A, chains lineares | Branching condicional, state management, human-in-the-loop |
| **LangGraph** | Stateful agents, conditional routing, persistência, approval gates | Debugging ainda pior que custom loop, serialização frágil |
| **Custom Loop** | Fine-grained observability, cost tracking, error handling explícito | Rápido de build (mais código boilerplate) |

## Decision Matrix (do paper)

| Situação | Usar |
|----------|------|
| RAG pipeline, document Q&A | LangChain |
| Tool-calling agent linear, 1-2 tools | LangChain |
| Protótipo | LangChain |
| Conditional branching baseado em tool results | LangGraph |
| Human-in-the-loop approval | LangGraph |
| State persistence across sessions | LangGraph |
| Multi-step com parallel sub-tasks | LangGraph |
| **Fine-grained error handling e observability** | **Custom loop** ← LATTE |
| **Tight latency + debugging complexo** | **Custom loop** ← LATTE |

## Validação do LATTE

Nossa escolha de **custom loop** (orchestrator.py) é validada pelo paper:
- "Custom loop is ~100 lines of Python with no framework magic"
- "Every state transition is explicit. Error handling is exactly what you wrote"
- "When something breaks at 2 AM, the stack trace points to your code"

O paper confirma: LangGraph é overkill quando você precisa de controle fino sobre observabilidade — exatamente o caso do LATTE com métricas customizadas (overwrite rate, wasted chars, idle rounds, straggler p95).

## Onde LangGraph Ainda Ganharia

1. **Checkpointing** — LangGraph faz `interrupt_before` + resume com `invoke(None, config)` em 1 linha. Nosso ADR-002 (grafo só em memória) significa que crash perde tudo.
2. **Human-in-the-loop** — Approval gates compilados no grafo, não bolted-on.
3. **Cross-graph state sharing** — LangGraph tem padrão emergente; nosso multi-graph ainda é manual.

Mas o paper é claro: *"Only migrate if the current system is actively causing problems."*

## Lições de Migração

- "Migration cost: 2-5 days for a mid-sized agent. Not worth it unless you need a specific LangGraph feature."
- "LangGraph v0.2+ is significantly more stable than earlier versions."
- "Design the TypedDict before writing any node code — saves a day of rework."
- "Testing the full graph is tedious. Write node-level unit tests + 2-3 integration tests."

## Relacionado

- [[references/papers/Multi-Agent-Systems-in-Production|Multi-Agent in Production]] — orquestração
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — checkpointing, state pruning
- [[references/papers/LATTE|LATTE]] — coordination graph (nossa implementação)
- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — LATTE custom loop
- [[projects/42_Framework/features/005-latte-hardening|Feature 005]] — hardening do LATTE
