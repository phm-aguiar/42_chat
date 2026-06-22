---
title: "A-MapReduce — Executing Wide Search via Agentic MapReduce"
tags: [paper, multi-agent, mapreduce, memory, retrieval, cross-task, sdd]
status: analyzed
created: 2026-06-19
rag_score: 0.5091
source: "https://arxiv.org/html/2602.01331v1"
authors: "Chen et al., 2026"
feature: "[[projects/42_Framework/features/002-experiential-memory|Feature 002: Wiki Experiential Memory]]"
---

# A-MapReduce — Executing Wide Search via Agentic MapReduce

> Framework MapReduce com memória experiencial. Base para Feature 002.

## Resumo

Framework multi-agente inspirado em MapReduce para tarefas de **wide search** (busca horizontal). Manager agent decompõe tasks em matrix + template + batching strategy. Search agents executam batches em paralelo. O diferencial é a **experiential memory**: hints acumulados de execuções passadas, com retrieval por similaridade, scoring com feedback, e distillation periódica.

## Componentes Centrais

| Componente | Função | Aplicação no 42_Framework |
|---|---|---|
| **Task matrix + batching** | Decomposição adaptativa de queries | Não aplicável diretamente (domínio de web search) |
| **Experiential memory** | Hints cross-task com scores | Feature 002: índice semântico da wiki |
| **Hint scoring** | Utility signal → score update | Feature 002 M2.3: feedback loop com métricas LATTE |
| **Distillation Fψ** | Consolida hints, remove redundância | Feature 002 M2.4: clusterização + chunks canônicos |
| **Query-conditioned retrieval** | Embedding da query → top-k hints | Feature 002 M2.2: search_similar() por cosseno |

## Resultados Reportados

- **+5.15pp Item F1** vs baselines (OpenAI o3, Gemini 2.5 Pro)
- **-34.7% runtime** vs variante sem memória
- **-42.8% custo** ($1.05 → $0.60)
- Pareto frontier em cost-performance

## Aplicação no 42_Framework

Implementado como **[[projects/42_Framework/features/002-experiential-memory|Feature 002: Wiki Experiential Memory]]** — indexação semântica da wiki com embeddings (all-MiniLM-L6-v2), retrieval contextual, hint scoring com feedback loop, e distillation periódica.

### Módulos

| Módulo | Função |
|---|---|
| `chunker.py` | Quebra docs em seções por ## headings |
| `store.py` | SQLite schema (chunks + embeddings BLOB) |
| `search.py` | Cosine similarity top-k |
| `scoring.py` | update_score, get_top_hints |
| `feedback.py` | Utility signal → delta |
| `decay.py` | Score decay por inatividade |
| `cluster.py` | KMeans/fallback guloso |
| `distill.py` | Geração de chunks canônicos via LLM |
| `summarizer.py` | Auto-sumário de papers em _raw/ |

### Métricas Reais

- **234 docs, 1918 chunks, 7.2 MB**
- **Query: 312ms, Index: 86s**
- **Cobertura: 100%**
- **Scores: 0.10 ~ 0.81**

## Relacionado

- [[projects/42_Framework/features/002-experiential-memory|Feature 002]] — implementação no 42_Framework
- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — fornece métricas de coordenação como utility signal
- [[references/papers/LATTE|LATTE]] — coordination graph dinâmico (dependência para feedback loop)
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — checkpointing e state pruning
- [[concepts/obsidian-flow|Fluxo Obsidian]] — integração wiki ↔ pipeline
- [[skills/wiki-query|wiki-query]] — retrieval semântico (modo --semantic)
- [[skills/sdd-generate-tasks|sdd-generate-tasks]] — consome hints no prompt do G₀
- [[skills/sdd-validate|sdd-validate]] — métricas que alimentam o feedback loop
- [[skills/brain|brain toolkit]] — wiki-query, wiki-ingest, wiki-distill
