---
title: "003: Hybrid Retrieval & Normalization"
category: projects
tags:
  - hybrid-search
  - bm25
  - embeddings
  - frontmatter
  - retrieval
  - sdd
summary: "Pesquisa híbrida (BM25 + cosine), normalização de frontmatter (34 docs) e thresholds adaptativos. Baseado no relatório Otimização de Obsidian para IA."
created: "2026-06-20"
rag_score: 0.5
updated: "2026-06-20"
status: implemented
sources:
  - repo:specs/features/003-hybrid-retrieval/
lifecycle: verified
lifecycle_changed: "2026-06-20"
base_confidence: 0.95
provenance:
  extracted: 0.9
  inferred: 0.05
  ambiguous: 0.05
---

# 003: Hybrid Retrieval & Normalization

> Pesquisa híbrida (BM25 + cosine), normalização de frontmatter (34 docs) e thresholds adaptativos.
> Baseado no relatório **"Otimização de Obsidian para IA"** (2026).

## Status

**Implementada.** Fecha os 3 gaps principais identificados no relatório "Otimização de Obsidian para IA".

## O que foi implementado

### 1. Pesquisa Híbrida (BM25 + Cosine)

Combina busca lexical (BM25) para termos exatos — códigos, stack traces, nomes de arquivos — com busca semântica (cosine similarity) para conceitos abstratos. Resultados são fundidos com pesos configuráveis, priorizando correspondências que pontuam alto em ambas as modalidades.

### 2. Normalização de Frontmatter

34 docs estavam sem YAML frontmatter padronizado, tornando-os invisíveis para busca por tags e sem tier de relevância. A normalização aplica:
- **snake_case** padronizado em todas as chaves
- Sem aninhamento profundo (máx. 1 nível)
- `title`, `tags`, `created`, `status` como campos mínimos obrigatórios
- Adição automática de frontmatter em docs sem metadata

### 3. Thresholds Adaptativos

Substitui thresholds fixos por valores adaptativos contextuais:
- **0.50** para consultas (mais permissivo, evita false negatives)
- **0.70** para cross-links (mais rigoroso, evita links espúrios entre notas)

## Gaps Fechados (do relatório Otimização de Obsidian para IA)

| # | Gap Original | Solução |
|---|-------------|---------|
| 1 | Pesquisa híbrida — só cosine, sem BM25 | BM25 integrado com merge ponderado |
| 2 | 34 docs sem frontmatter | Normalização automática com snake_case |
| 3 | Thresholds fixos | 0.50 queries / 0.70 cross-links |

## Relacionado

- **Paper base:** [[references/papers/Obsidian-Otimizacao-IA|Otimização de Obsidian para IA]]
- [[projects/42_Framework/features/002-experiential-memory|Feature 002]] — Wiki Experiential Memory (dependência)
- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — LATTE Coordination
- [[projects/42_Framework/42_Framework|42 Framework]] — Meta-framework
- [[specs/features/003-hybrid-retrieval/spec|Spec]]
- [[specs/features/003-hybrid-retrieval/plan|Plan]]
- [[specs/features/003-hybrid-retrieval/tasks|Tasks]]
