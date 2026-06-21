# 42 Framework

Meta-framework para Spec-Driven Development (SDD) com orquestração multi-agente,
wiki semântica e retrieval híbrido.

## Pipeline SDD

```
brainstorm → spec → plan → tasks (G₀ + hints)
                 ↑              │
            [wiki-query]   ┌────↓─────────┐
            busca hints    │ orchestrator  │
            cross-feature  │ LATTE rounds  │
                 ↑         │ com heartbeat │
            ┌────┴──────┐  └──────┬────────┘
            │ experiential│       │
            │ memory      │←──────┘
            │ (wiki +     │  G_final + métricas
            │  SQLite)    │  overwrites, idle rounds
            └─────────────┘
```

## Features

| ID | Nome | Status | Tasks | Descrição |
|----|------|--------|-------|-----------|
| 001 | LATTE Coordination | ✅ | 23 | Coordination graph dinâmico com heartbeat, 7 operadores, context scoping |
| 002 | Wiki Experiential Memory | ✅ | 30 | Indexação semântica (embeddings), retrieval, hint scoring, feedback loop, distillation |
| 003 | Hybrid Retrieval & Normalization | ✅ | 15 | Pesquisa híbrida BM25+cosine, normalização de frontmatter (34 docs), thresholds adaptativos |

**Total: 68 tasks implementadas.**

### Progressão

```
001 ──→ 002 ──→ 003
 │       │       │
 │       │       └── depende da 002 (search.py, índice SQLite)
 │       └── depende da 001 (métricas LATTE → utility signal)
 └── independente (orquestração pura)
```

| # | Feature | Dependência | Stack adicionada | Por que |
|---|---------|-------------|------------------|---------|
| 001 | LATTE Coordination | — | `delegate_task`, CoordinationGraph, heartbeat H=4, 7 operadores (Discover/Assign/Claim/Complete/Release/Close/Verify) | Orquestração dinâmica substitui DAG estático. Rounds discretos, straggler detection, context scoping |
| 002 | Wiki Experiential Memory | 001 (métricas) | `sentence-transformers` + `all-MiniLM-L6-v2` (384d, 23MB), SQLite com embeddings BLOB, `search_similar()` cosine, `scoring.py` (update_score), `feedback.py` (utility signal → delta), `decay.py`, `cluster.py` (KMeans), `distill.py` (chunks canônicos), `summarizer.py` | Wiki vira memória experiencial indexada. Hints cross-feature, retrieval semântico, scoring com feedback loop |
| 003 | Hybrid Retrieval | 002 (search.py, índice) | `rank_bm25` (BM25Okapi, Python puro), fusão α=0.7, `--hybrid` mode, `normalize_frontmatter.py` (34 docs), thresholds adaptativos (0.50 query, 0.70 cross-link) | BM25 cobre termos exatos que cosine perde (+99% ganho lexical). Frontmatter 100% coverage. Pesquisa híbrida = "arquitetura suprema para vaults densos" |

### Papers ingeridos

| Paper | Status | Feature relacionada |
|-------|--------|---------------------|
| LATTE (Mieczkowski et al., 2026) | ✅ implemented | 001 |
| A-MapReduce (Chen et al., 2026) | ✅ implemented | 002 |
| LangGraph in Production (Gulecha, 2026) | ✅ analyzed | Candidato 004 |
| Otimização de Obsidian para IA (2026) | ✅ implemented | 003 |

## Wiki

- **244 documentos** (5.5 MB)
- **2.053 chunks** indexados no SQLite (7.8 MB)
- **100% cobertura** de frontmatter
- **4 papers** ingeridos e cross-linkados

### Retrieval

| Modo | Algoritmo | Tempo | Uso |
|------|-----------|-------|-----|
| `--semantic` | Cosine similarity (all-MiniLM-L6-v2, 384d) | 283ms | Consultas conceituais |
| `--hybrid` | BM25 + Cosine fusion (α=0.7) | 313ms | Termos exatos + conceituais |

### Benchmark Hybrid vs Cosine-only (15 queries)

| Tipo | Cosine | Hybrid | Ganho |
|------|--------|--------|-------|
| Lexical (termos exatos) | 0.412 | 0.801 | **+99%** |
| Conceitual (semântico) | 0.541 | 0.928 | **+73%** |
| Misto | 0.614 | 0.966 | **+59%** |
| **Total** | **0.522** | **0.898** | **+77%** |

## Estrutura

```
42_Framework/
├── specs/features/           # Pipeline SDD (spec + plan + tasks)
│   ├── 001-latte-coordination/
│   ├── 002-experiential-memory/
│   └── 003-hybrid-retrieval/
├── .hermes/skills/           # Implementação (Python + SKILL.md)
│   ├── sdd/latte_coordination/   # Feature 001
│   ├── wiki/experiential_memory/ # Features 002+003
│   └── wiki/brain/               # Brain toolkit
├── wiki/                     # Vault Obsidian (source of truth)
│   ├── concepts/             # SDD, Obsidian flow
│   ├── references/papers/    # LATTE, A-MapReduce, LangGraph, Obsidian IA
│   ├── references/toolkits/  # sdd, wiki, go, obsidian, qa, github
│   ├── projects/42_Framework/features/
│   ├── projects/42_chat/
│   └── _raw/                 # Papers originais
└── ~/.hermes/wiki_index.db   # Índice SQLite (derivado da wiki)
```

## Stack

| Camada | Tecnologia | Feature | Detalhe |
|--------|-----------|---------|---------|
| **Runtime** | Hermes Agent | — | Python, subagentes via `delegate_task` |
| **Orquestração** | LATTE Algorithm A4.5 | 001 | CoordinationGraph, rounds discretos, heartbeat H=4 |
| **Operadores** | Discover, Assign, Claim, Complete, Release, Close, Verify | 001 | 7 operadores com pre/post conditions formais |
| **Embeddings** | `all-MiniLM-L6-v2` | 002 | 384 dimensões, 23 MB, CPU-only, sentence-transformers |
| **Store** | SQLite (WAL mode) | 002 | `~/.hermes/wiki_index.db`, 2053 chunks, 7.8 MB |
| **Retrieval** | Cosine similarity + rank_bm25 | 002+003 | α=0.7 fusion, thresholds adaptativos, 313ms |
| **Scoring** | `scoring.py` + `feedback.py` | 002 | update_score, utility signal → delta, decay |
| **Distillation** | `cluster.py` (KMeans) + `distill.py` | 002 | Agrupamento por similaridade, chunks canônicos via LLM |
| **Frontmatter** | `normalize_frontmatter.py` | 003 | 34 docs normalizados, 100% coverage |
| **Wiki** | Obsidian-compatible Markdown vault | — | 244 docs, 5.5 MB, YAML frontmatter |
| **Papers** | 4 papers ingeridos e cross-linkados | — | `wiki/references/papers/` |

## Princípios

1. **Wiki como source of truth** — índice é derivado, nunca modifica `.md` originais
2. **Hermes nativo** — zero dependências externas (sem APIs, sem cloud)
3. **Context scoping** — Workers recebem só task + outputs de dependências
4. **Compatibilidade reversa** — novos parâmetros têm defaults que preservam comportamento anterior
