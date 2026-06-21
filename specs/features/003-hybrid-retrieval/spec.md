---
feature_id: "003"
title: "Wiki Hybrid Retrieval & Normalization"
status: draft
created: "2026-06-20"
author: phm-aguiar
tags: [sdd, wiki, retrieval, bm25, hybrid-search, frontmatter, thresholds]
based_on:
  - "Otimização de Obsidian para IA (relatório compilado, 2026)"
  - "Feature 002: Wiki Experiential Memory"
depends_on: "002-experiential-memory"
---

**Aprovado:** true

# Wiki Hybrid Retrieval & Normalization

> Pesquisa híbrida (BM25 + cosine), normalização de frontmatter (34 docs),
> e thresholds adaptativos. Baseado no relatório "Otimização de Obsidian para IA".

## Propósito

A Feature 002 implementou indexação semântica com busca por similaridade de cosseno.
Funciona bem para consultas conceituais, mas falha em consultas com termos exatos:
códigos, stack traces, identificadores hexadecimais.

O relatório "Otimização de Obsidian para IA" (2026) identifica a pesquisa híbrida
(BM25 lexical + embeddings semântico) como "a arquitetura suprema para vaults densos".
Recomenda também thresholds adaptativos (0.50 consultas, 0.70 cross-links) e
frontmatter padronizado em todos os documentos.

**Esta feature implementa as 3 recomendações.**

## Escopo

- **BM25 + Cosine Fusion:** rank_bm25 (Python puro), weighted sum com α=0.7
- **Thresholds adaptativos:** 0.50 query mode, 0.70 cross-link mode
- **Frontmatter normalization:** 34 docs sem YAML recebem title+tags+created
- **Integração:** search_similar(hybrid=True), wiki-query --hybrid

Fora do escopo: nomic-embed-text, sqlite-vec, normalização completa dos 238 docs.

## Constraints

- rank_bm25 Python puro (sem C extensions)
- Frontmatter mínimo (só title, tags, created)
- Thresholds configuráveis por chamada
- Compatível com Feature 002 (search_similar sem params = comportamento idêntico)

## Critérios de Sucesso

1. Ganho lexical ≥20% em queries exatas vs cosine-only
2. Retrieval quality ≥85% top-3 (LLM-judge)
3. Query híbrida <500ms
4. Frontmatter coverage 238/238 (100%)
5. 34 docs normalizados com title+tags+created
6. Thresholds 0.50/0.70 funcionais
7. Compatibilidade reversa

## Edge Cases

- BM25 em índice vazio, termo não encontrado, threshold=0 ou 1.0, α extremo,
  conflito de título, encoding quebrado, doc já com frontmatter parcial.
