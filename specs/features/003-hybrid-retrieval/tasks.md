---
feature_id: "003"
title: "Wiki Hybrid Retrieval & Normalization"
spec: "specs/features/003-hybrid-retrieval/spec.md"
plan: "specs/features/003-hybrid-retrieval/plan.md"
created: "2026-06-20"
author: phm-aguiar
depends_on: "002-experiential-memory"
---

# Tasks — Wiki Hybrid Retrieval & Normalization

> DAG de 15 tasks em 3 fases. Feature enxuta: BM25 + frontmatter + thresholds.

## Fase 1: Implementação (BM25 + Fusão)

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T001 | Instalar rank_bm25. Verificar import | Dev | — | — | requirements.txt |
| T002 | BM25 scoring: tokenizar, TF-IDF, bm25_score() | Dev | T001 | — | bm25.py |
| T003 | Fusão híbrida: hybrid_score = α*cosine + (1-α)*bm25. Estender search_similar() | Dev | T002 | — | search.py (patch) |
| T004 | Integrar cli_query.py com --hybrid | Dev | T003 | — | cli_query.py (patch) |
| T005 | Integrar wiki-query SKILL.md com --hybrid | Dev | T004 | — | query/SKILL.md (patch) |

## Fase 2: Normalização (Frontmatter)

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T006 | normalize_frontmatter.py: detectar, extrair title+tags+created, --dry-run | Dev | — | true | normalize_frontmatter.py |
| T007 | Executar normalização nos 34 docs, verificar 0 erros | QA | T006 | — | — |
| T008 | Reindexar wiki, verificar 238 fontes | QA | T007 | — | — |

## Fase 3: Validação + Documentação

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T009 | Smoke: ganho lexical (10 queries exatas, hybrid vs cosine, ≥20%) | QA | T005 | true | test_hybrid_lexical.py |
| T010 | Smoke: threshold (0.50 vs 0.70, contagem de resultados) | QA | T003 | true | test_threshold.py |
| T011 | Smoke: compatibilidade (search_similar sem params = mesmo resultado) | QA | T003 | true | test_hybrid_compat.py |
| T012 | Smoke: frontmatter 238/238 com title | QA | T008 | true | test_frontmatter_coverage.py |
| T013 | Atualizar Obsidian-Otimizacao-IA.md com status=implemented | Dev | T008 | true | wiki/references/papers/ |
| T014 | Atualizar experiential-memory.md com pesquisa híbrida | Dev | T005 | true | wiki/references/toolkits/wiki/ |
| T015 | Atualizar 42_Framework.md com feature 003 | Dev | T014 | true | wiki/projects/42_Framework/ |

## Validação do DAG

✅ Sem ciclos. 15 tasks, 9 paralelizáveis (60%), 0 conflitos de arquivo.
