---
title: "Wiki Experiential Memory — Features 002 & 003"
created: "2026-06-19"
rag_score: 0.5
updated: "2026-06-20"
author: phm-aguiar
tags:
  - wiki
  - embeddings
  - experiential-memory
  - feature-002
  - feature-003
  - hybrid-search
  - bm25
summary: "Documentação completa das Features 002 e 003: memória experiencial com indexação semântica de chunks da wiki, retrieval contextual (cosine + BM25 híbrido), hint scoring com feedback loop, distillation periódica, e normalização de frontmatter. Inspirado no Experiential Memory do A-MapReduce."
based_on:
  - "A-MapReduce: Executing Wide Search via Agentic MapReduce"
  - "LATTE: Language Agent Teams for Task Evolution"
depends_on: "001-latte-coordination"
---

# Wiki Experiential Memory — Features 002 & 003

> Transforma a wiki Obsidian de documentação estática em **memória experiencial viva**: indexação semântica de chunks, retrieval contextual (cosine-only + híbrido BM25+cosine), hint scoring automático com feedback loop, normalização de frontmatter, e distillation periódica. Inspirado no Experiential Memory do A-MapReduce (Chen et al., 2026).

---

## 1. Arquitetura

```
wiki/*.md                          metrics.json (LATTE)
    │                                    │
    ▼                                    ▼
┌─────────┐    ┌──────────┐    ┌──────────────┐
│ Chunker │───▶│ Embedder │───▶│  SQLite Index │
│ (## h2) │    │ (MiniLM) │    │ chunks + emb  │
└─────────┘    └──────────┘    │ + scores      │
                               └──────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                  ▼
            ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
            │ wiki-query   │  │ generate-   │  │ wiki-distill  │
            │ --semantic   │  │ tasks (G₀)  │  │ (Fψ operator) │
            └─────────────┘  └─────────────┘  └──────────────┘
```

### 1.1 Fluxo de Dados

| Etapa | Componente | Descrição |
|---|---|---|
| **1. Chunking** | `chunker.py` | Documentos `.md` são quebrados em chunks por headings `##`, com fallback para parágrafos. Chunks > 4096 caracteres são subdivididos; chunks < 50 caracteres são ignorados. |
| **2. Embedding** | `cli_index.py` + `SentenceTransformer` | Cada chunk é embeddado via `all-MiniLM-L6-v2` (384 dimensões, float32). Embedding serializado como BLOB (384 × 4 = 1.5KB por chunk). |
| **3. Armazenamento** | `store.py` | Chunks + embeddings + metadados persistidos em SQLite (`~/.hermes/wiki_index.db`). Schema: `chunks(id, source, heading, content, embedding BLOB, score REAL, content_hash TEXT UNIQUE, tags, char_count, created_at, last_updated)`. |
| **4. Retrieval** | `search.py`, `bm25.py` | Consulta é embeddada e comparada via cosine similarity contra todos os chunks. Modo híbrido (`--hybrid`) combina cosine + BM25 (α=0.7). Retorna top-k ordenados por `similarity` ou `hybrid_score` decrescente. |
| **5. Scoring** | `scoring.py`, `feedback.py`, `decay.py` | Scores inicializados como 0.5 (neutro). Métricas LATTE atualizam scores via feedback loop. Decay reduz scores de chunks inativos. |
| **6. Distillation** | `cluster.py`, `distill.py`, `cli_distill.py` | Clusterização (KMeans com sklearn ou guloso fallback) agrupa chunks similares. LLM sintetiza chunks canônicos; originais têm score zerado (não deletados). |

### 1.2 Componentes e Arquivos

``` 
.hermes/skills/wiki/experiential-memory/
├── __init__.py                  # Feature 002 & 003 — Embedding + Hybrid retrieval
├── chunker.py                   # T002: Chunking por headings ## com fallback parágrafos
├── store.py                     # T003: SQLite schema, insert_chunk, get_stats, get_by_hash
├── search.py                    # T005: Cosine similarity + hybrid search (BM25+cosine)
├── bm25.py                      # Feature 003: BM25 lexical retrieval via rank_bm25
├── normalize_frontmatter.py     # Feature 003: Normalização de frontmatter YAML mínimo
├── scoring.py                   # T010: Score update, get_top_hints, get_low_score_hints
├── feedback.py                  # T011: Utility signal → score update (LATTE metrics)
├── decay.py                     # T012: Score decay por inatividade
├── cluster.py                   # T013: KMeans / greedy clustering
├── distill.py                   # T014: Geração de chunks canônicos via LLM
├── summarizer.py                # T016: Sumarização automática de _raw/
├── cli_index.py                 # T004: hermes wiki index --full
├── cli_query.py                 # T006: hermes wiki query --semantic "..." [--hybrid]
├── cli_distill.py               # T015: hermes wiki distill
└── tests/
    ├── test_index_coverage.py              # T017: 100% coverage smoke test
    ├── test_reindex_idempotent.py          # T023: Score preservation on re-index
    ├── test_retrieval_quality.py           # T018: LLM-judge retrieval quality
    ├── test_hybrid_retrieval.py            # Feature 003: Hybrid vs semantic quality
    ├── test_token_reduction.py             # T019: Token reduction validation
    ├── test_score_convergence.py           # T020: Score convergence after N features
    ├── test_distill_efficacy.py            # T021: Chunk reduction post-distillation
    ├── test_speed.py                       # T022: Index < 30s, query < 1s
    └── test_cold_start.py                  # T024: Cold start resilience
```

---

## 2. API de Índice

### 2.1 `index` — Indexação Completa

```bash
hermes wiki index --full [--dry-run] [--wiki-dir PATH]
```

**Fluxo interno:**

```python
from chunker import chunk_markdown
from store import create_tables, insert_chunk
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

for md_path in wiki_dir.rglob("*.md"):
    content = md_path.read_text()
    chunks = chunk_markdown(content, str(md_path.relative_to(wiki_dir)))
    for chunk in chunks:
        embedding_bytes = model.encode(chunk["content"]).tobytes()
        insert_chunk(chunk, embedding_bytes)
```

**Relatório de saída esperado:**
```
Carregando modelo 'all-MiniLM-L6-v2' ... OK
Indexando 84 arquivo(s) .md em /home/user/Projetos/42_Framework/wiki
------------------------------------------------------------
[1/84] concepts/sdd.md ... 8 chunks (8 embeddados)
[2/84] concepts/vault-taxonomy.md ... 5 chunks (5 embeddados)
...
------------------------------------------------------------
============================================================
RELATÓRIO DE INDEXAÇÃO
============================================================
  Documentos processados : 84
  Chunks criados         : 312
  Chunks com embedding   : 312
  Documentos pulados     : 0
  Erros                  : 0
  Tempo total            : 18.3s
  Total chunks no banco  : 312
  Fontes distintas       : 84
  Tamanho médio (chars)  : 1847.3
  Tamanho do banco       : 2.1 MB
============================================================
```

### 2.2 `query` — Retrieval Semântico

```bash
hermes wiki query --semantic "texto da consulta" [--top-k N]
```

**Fluxo interno:**

```python
from search import search_similar
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
results = search_similar(query_text="feature de autenticação com OAuth2", model=model, k=5)
# Retorna: [{chunk_id, source, heading, content, similarity, score, content_hash, tags}, ...]
```

**Formato de resposta JSON (consumidores via stdout):**
```json
[
  {
    "chunk_id": 42,
    "source": "references/oauth2-42-pitfalls.md",
    "heading": "Pitfall 1: redirect_uri",
    "content": "O erro mais comum na integração OAuth2 da 42...",
    "similarity": 0.8723,
    "score": 0.78,
    "content_hash": "a3f2b9c1...",
    "tags": ["oauth2", "debug"]
  }
]
```

**Ordenação:** Por `similarity` decrescente. O `score` (feedback acumulado) é disponibilizado como metadado — consumidores podem combiná-lo com similarity para ranking próprio (`combined_score = score × similarity`).

### 2.3 `score` — Atualização de Score

```python
from scoring import update_score, get_score, get_top_hints, get_low_score_hints

# Atualização individual
update_score(content_hash="a3f2b9c1...", delta=+0.08)  # retorna True/False
get_score(content_hash="a3f2b9c1...")                   # retorna float [0, 1]

# Consultas agregadas
get_top_hints(k=10)                                      # top-k por score DESC
get_low_score_hints(threshold=0.3)                       # candidatos a pruning
reset_all_scores()                                       # volta todos para 0.5
```

**Regras de score:**
- Inicialização: `0.5` (neutro)
- Range: `[0.0, 1.0]` — clamp via `MAX(0.0, MIN(1.0, score + delta))`
- Preservação: Scores são atrelados a `content_hash` (SHA256), sobrevivem a re-indexações
- Feedback positivo: `+0.04` a `+0.10` por feature bem-sucedida
- Feedback negativo: `-0.04` a `-0.10` por feature problemática
- Decay: `-0.01` por inatividade (N features sem uso), floor = `0.1`

### 2.4 `distill` — Destilação de Padrões Canônicos

```bash
hermes wiki distill [--threshold 0.85] [--dry-run]
```

**Fluxo interno:**

```python
from cluster import cluster_chunks
from distill import distill_clusters

# 1. Clusterização
clusters = cluster_chunks(similarity_threshold=0.85)
# Retorna: [[chunk, chunk, ...], [chunk, ...], ...]

# 2. Destilação (LLM)
canonicals = distill_clusters(clusters)
# Retorna: [{source: "_distilled/", heading: "Canonical Pattern 1", content: "...", ...}, ...]

# 3. Cada canônico é embeddado e inserido no índice
# 4. Chunks originais do cluster têm score zerado (não deletados)
```

**Relatório de saída esperado:**
```
Clusterizando chunks (threshold=0.85)...
  8 clusters formados (200 chunks total)
Destilando padrões canônicos via LLM...
  8 padrões canônicos gerados
  8 chunks canônicos inseridos no índice
  200 chunks originais marcados com score=0

============================================================
RELATÓRIO DE DESTILAÇÃO
============================================================
  Clusters formados       : 8
  Chunks antes            : 200
  Padrões canônicos       : 8
  Chunks no banco (total) : 208
  Chunks com score=0      : 200
  % de redução            : 96.0%
  Tempo total             : 45.2s
============================================================
```

### 2.5 `reindex` — Re-indexação Idempotente

```bash
hermes wiki index --full  # re-executar o mesmo comando
```

**Comportamento:** `INSERT OR REPLACE` baseado na constraint `UNIQUE(content_hash)`. Scores existentes são preservados via `COALESCE((SELECT score FROM chunks WHERE content_hash = ?), 0.5)`. O índice é sempre reconstruível a partir da wiki — se corromper, basta re-executar `index --full`.

### 2.6 `query --hybrid` — Pesquisa Híbrida (BM25 + Cosine)

> **Feature 003 — Hybrid Retrieval.** Estende o retrieval semântico da Feature 002 combinando **cosine similarity** (embedding semântico) com **BM25** (relevância lexical) para capturar tanto similaridade conceitual quanto correspondência exata de termos.

```bash
hermes wiki query --semantic "texto da consulta" --hybrid [--top-k N]
```

#### 2.6.1 Motivação

O retrieval puramente semântico (cosine-only) é excelente para consultas conceituais ("como funciona o pipeline SDD"), mas pode falhar quando a consulta contém **termos técnicos exatos** que precisam aparecer literalmente nos chunks — siglas (`OAuth2`, `k8s`), códigos (`O(n)`, `SQL`), nomes de funções, ou tokens específicos de domínio.

A **pesquisa híbrida** resolve isso combinando dois sinais complementares:

| Sinal | Componente | O que captura |
|---|---|---|
| **Semântico** | Cosine similarity (`all-MiniLM-L6-v2`) | Similaridade conceitual, paráfrases, documentos sobre o mesmo tópico em palavras diferentes |
| **Lexical** | BM25 (`rank_bm25.BM25Okapi`) | Frequência de termos exatos, correspondência de tokens específicos, raridade de termos (IDF) |

#### 2.6.2 Arquitetura

```
consulta: "Redis TTL expiração pub/sub"
        │
        ├──▶ SentenceTransformer ──▶ query_embedding (384d)
        │         │
        │         ▼
        │    cosine_similarity(query_embedding, chunk_embeddings)
        │         │
        │         ▼
        │    cosine_scores [0.82, 0.45, 0.91, ...]
        │
        └──▶ BM25Retriever ──▶ BM25Okapi.get_scores(tokenized_query)
                  │
                  ▼
             bm25_scores [4.21, 0.00, 3.87, ...]

     ┌────────────────────────────────────────────────────┐
     │  Normalização min-max: ambos scores → [0, 1]       │
     │                                                    │
     │  hybrid_score = α × cosine_norm + (1−α) × bm25_norm │
     │              = 0.7 × cosine + 0.3 × bm25           │
     └───────────────────────┬────────────────────────────┘
                             │
                             ▼
              Ordena por hybrid_score DESC
                             │
                             ▼
              Filtra threshold adaptativo (se definido)
                             │
                             ▼
                   Retorna top-k
```

#### 2.6.3 Componentes

| Arquivo | Responsabilidade |
|---|---|
| `bm25.py` | **BM25Retriever**: tokeniza o conteúdo de cada chunk (split por whitespace, lowercase) e constrói índice BM25 clássico via `rank_bm25.BM25Okapi`. Expõe método `search(query, k)` que retorna lista de `(chunk_index, bm25_score)`. |
| `search.py` | **Modo híbrido** (parâmetro `hybrid=True`): calcula cosine similarity para todos os chunks, obtém BM25 scores via `BM25Retriever`, normaliza ambos por min-max, combina com peso `α=0.7`, ordena por `hybrid_score`. |
| `cli_query.py` | Flag `--hybrid`: ativa o modo híbrido na CLI. Exibe scores individuais (`cos`, `bm25`) e combinado (`hybrid`). |
| `normalize_frontmatter.py` | Adiciona YAML frontmatter mínimo (`title`, `tags`, `created`) a documentos wiki que não possuem bloco `---`. Essencial para que o BM25 tenha metadados relevantes para tokenização lexical. |

#### 2.6.4 Fórmula e Parâmetros

**Fórmula de combinação:**

```
hybrid_score = α × cosine_norm + (1 − α) × bm25_norm
```

Onde:
- `cosine_norm` = cosine score normalizado via min-max para [0, 1]
- `bm25_norm` = BM25 score normalizado via min-max para [0, 1]
- **α = 0.7** — peso maior para similaridade semântica (ADR-007)

**Justificativa do α=0.7:** A wiki 42 Framework é predominantemente conceitual (arquitetura, patterns, ADRs). O sinal semântico é mais informativo para a maioria das consultas. O BM25 (α−1 = 0.3) atua como *tiebreaker* e *boost* quando a consulta contém termos técnicos exatos presentes nos chunks.

**Threshold adaptativo (`threshold`):**

```python
results = search_similar(
    query_text="consulta...",
    model=model,
    k=10,
    hybrid=True,
    threshold=0.15,  # Filtra resultados com hybrid_score < 0.15
)
```

Quando definido, o threshold filtra resultados com `hybrid_score` abaixo do valor especificado. Isso é útil para descartar ruído quando o índice é grande e muitos chunks têm baixa relevância combinada.

**Regra prática de thresholds por contexto:**

| Contexto | Threshold sugerido | Efeito |
|---|---|---|
| `sdd-brainstorm` (feature context) | `None` (sem filtro) | Maximiza recall, evita perder contexto relevante |
| `sdd-generate-tasks` (G₀ hints) | `0.10` | Filtra ruído, mantém hints de qualidade |
| Consulta manual (`wiki-query`) | `0.15` | Bom equilíbrio precisão/recall para uso interativo |

#### 2.6.5 Exemplo de Uso

```bash
# Consulta com termos técnicos exatos — ideal para --hybrid
$ hermes wiki query --semantic "Redis TTL expiração pub/sub pattern" --hybrid --top-k 5

Carregando modelo 'all-MiniLM-L6-v2' ... OK
Buscando: "Redis TTL expiração pub/sub pattern" (modo híbrido)

======================================================================
RESULTADOS DA BUSCA HÍBRIDA  (5 encontrado(s) em 312ms)
======================================================================

[0.823 cos + 4.210 bm25 = 0.639 hybrid] references/redis-patterns.md > Pub/Sub com TTL
    O padrão pub/sub do Redis combinado com TTL permite expiração automática de canais...

[0.756 cos + 3.870 bm25 = 0.582 hybrid] references/go-redis.md > Configuração de TTL
    Biblioteca go-redis v9: configuração de TTL por chave e padrões de expiração...

[0.891 cos + 1.200 bm25 = 0.567 hybrid] concepts/caching-strategies.md > Cache Invalidation
    Estratégias de invalidação de cache: TTL-based, event-driven, write-through...

[0.612 cos + 2.950 bm25 = 0.473 hybrid] references/system-design.md > Message Brokers
    Comparação entre message brokers: Redis pub/sub, RabbitMQ, Kafka...

[0.701 cos + 1.540 bm25 = 0.336 hybrid] references/api-patterns.md > Event-Driven
    Padrões event-driven com Redis streams e notificações em tempo real...
======================================================================
```

Note como o chunk `references/redis-patterns.md` tem cosine=0.823 (bom, mas não o melhor) mas BM25=4.210 (excelente — contém os tokens exatos "Redis", "TTL", "pub/sub") — o score híbrido de 0.639 o coloca em #1, superando `caching-strategies.md` que tem cosine=0.891 (o melhor semântico) mas BM25=1.200 (fraco — não contém os tokens exatos da consulta).

#### 2.6.6 Normalização de Frontmatter

A Feature 003 também inclui `normalize_frontmatter.py`, que garante que todos os documentos da wiki tenham um bloco YAML frontmatter mínimo. Isso é importante porque:

1. **BM25 tokeniza o conteúdo completo** de cada chunk — frontmatter fornece metadados estruturados que melhoram a relevância lexical
2. **Tags inferidas automaticamente** a partir do diretório (ex: `references/toolkits/wiki/` → tags: `[wiki, reference]`)
3. **Cold start**: docs criados manualmente podem não ter frontmatter, prejudicando a busca lexical

```bash
# Adiciona frontmatter mínimo a docs sem bloco '---'
$ python -m experiential_memory.normalize_frontmatter --wiki-root wiki/

Encontrados 12 docs sem frontmatter.
[OK] wiki/concepts/sdd.md
[OK] wiki/concepts/vault-taxonomy.md
[OK] wiki/references/go-jwt.md
...

12 docs processados, 0 erros
```

**Regras de inferência:**

| Diretório | Tags inferidas | Exemplo de title |
|---|---|---|
| `references/toolkits/<name>/` | `[<name>, reference]` | `"Oauth2 42 Pitfalls"` |
| `skills/` | `[skill]` | `"Sdd Validate"` |
| `concepts/` | `[concept]` | `"Sdd"` |
| `references/` (fora de toolkits) | `[reference]` | `"Go Jwt"` |
| `projects/` | `[project]` | `"42 Framework"` |
| `_raw/` | `[raw]` | `"Latte Paper"` |
| Raiz da wiki | `[wiki]` | `"Index"` |

#### 2.6.7 Quando Usar `--hybrid` vs `--semantic`

| Cenário | Modo recomendado |
|---|---|
| Consulta conceitual ampla ("como funciona o pipeline SDD") | `--semantic` |
| Consulta com termos técnicos exatos ("Redis TTL expiração pub/sub") | `--hybrid` |
| Cosine-only trouxe resultados ruins/irrelevantes | Reexecute com `--hybrid` |
| Consulta contém siglas, códigos ou símbolos (`O(n)`, `SQL`, `k8s`) | `--hybrid` (BM25 captura tokens exatos) |
| Primeira consulta exploratória | `--semantic` (mais rápido, sem custo BM25) |
| Debug: "por que esse chunk apareceu?" | `--hybrid` (expõe scores individuais) |

**Regra prática:** comece com `--semantic`. Se os resultados forem insatisfatórios ou a consulta contiver termos técnicos específicos que devem aparecer literalmente nos chunks, reexecute com `--hybrid`.

#### 2.6.8 API Programática (Python)

```python
from search import search_similar
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Modo híbrido com threshold adaptativo
results = search_similar(
    query_text="estratégias de caching em Go com Redis TTL",
    model=model,
    k=10,
    hybrid=True,
    alpha=0.7,          # peso semântico (default)
    threshold=0.15,     # filtra hybrid_score < 0.15
)

for r in results:
    print(f"[cos={r['similarity']:.3f} + bm25={r['bm25_score']:.3f} "
          f"= hybrid={r['hybrid_score']:.3f}] {r['source']} > {r['heading']}")
    print(f"    {r['content'][:120]}...")
    print()
```

---

## 3. Modelo de Embedding: `all-MiniLM-L6-v2`

### 3.1 Especificações Técnicas

| Propriedade | Valor |
|---|---|
| **Nome** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Dimensões** | 384 |
| **Tamanho em disco** | ~23 MB |
| **Hardware** | CPU (sem GPU necessária) |
| **Dependência** | `pip install sentence-transformers` |
| **API Key** | Nenhuma (modelo local) |
| **Armazenamento por chunk** | 384 × 4 bytes (float32) = 1.5 KB |
| **500 chunks** | ~750 KB de embeddings |
| **2000 chunks** | ~3 MB de embeddings |

### 3.2 Justificativa (ADR-001)

| Critério | all-MiniLM-L6-v2 | Alternativa rejeitada (multilingual-e5-small) |
|---|---|---|
| **Validação prévia** | ✅ Mesmo modelo usado no A-MapReduce | ❌ Não validado no contexto de wide search |
| **Tamanho** | 23 MB | 118 MB (5× maior) |
| **Setup** | Zero configuração | Requer prefixos `"query:"` / `"passage:"` |
| **Dimensões** | 384d → 1.5 KB/chunk | 384d também, mas download 5× maior |
| **Cobertura pt-BR** | Razoável via transfer learning (línguas indo-europeias) | Nativa, mas sobrekill para wiki bilíngue |

### 3.3 Carregamento e Uso

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Embedding de um chunk
embedding = model.encode("texto do chunk", convert_to_numpy=True)
# Retorna: numpy.ndarray de shape (384,) dtype=float32

# Serialização para SQLite
embedding_bytes = embedding.tobytes()  # 1536 bytes

# Desserialização
import numpy as np
embedding_restored = np.frombuffer(embedding_bytes, dtype=np.float32)
```

### 3.4 Fallback sem NumPy

Se `numpy` não estiver disponível, `search.py` e `cluster.py` implementam fallback em Python puro:

```python
# Deserialização manual (4 bytes por float32)
import struct
floats = [struct.unpack('f', blob[i:i+4])[0] for i in range(0, len(blob), 4)]

# Cosine similarity manual
dot = sum(x * y for x, y in zip(a, b))
norm_a = math.sqrt(sum(x * x for x in a))
norm_b = math.sqrt(sum(y * y for y in b))
similarity = dot / (norm_a * norm_b)
```

---

## 4. Integração com o Pipeline SDD

### 4.1 Visão Geral

As Features 002 e 003 são consumidas por múltiplos pontos do pipeline SDD:

```
┌────────────────────────────────────────────────────────────────────┐
│                        PIPELINE SDD                                │
│                                                                    │
│  brainstorm ──▶ spec.md ──▶ plan.md ──▶ tasks.md ──▶ exec LATTE   │
│       │              │           │            │            │       │
│       ▼              ▼           ▼            ▼            ▼       │
│  ┌─────────┐   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────┐  │
│  │FEATURE  │   │FEATURE  │  │FEATURE  │  │FEATURE  │  │VALID. │  │
│  │CONTEXT  │   │PRIORS   │  │PRIORS   │  │HINTS    │  │FEEDBK │  │
│  └─────────┘   └─────────┘  └─────────┘  └─────────┘  └───────┘  │
│       │              │           │            │            │       │
│       └──────────────┴───────────┴────────────┴────────────┘       │
│                                 │                                   │
│                    ┌────────────┴────────────┐                     │
│                    │  Wiki Experiential      │                     │
│                    │  Memory Index (SQLite)  │                     │
│                    └─────────────────────────┘                     │
└────────────────────────────────────────────────────────────────────┘
```

### 4.2 Pontos de Integração

#### 4.2.1 `sdd-brainstorm` — Contexto de Features Similares

**Quando:** Durante a entrevista de brainstorm, ao iniciar uma nova feature.

**O que faz:** Consulta o índice semântico pela descrição inicial da feature. Injeta chunks de features similares como contexto adicional na entrevista.

```bash
# Internamente:
hermes wiki query --semantic "feature de autenticação OAuth2 para API"
# → Top-5 chunks sobre auth, OAuth2 pitfalls, rate limits da API 42
```

#### 4.2.2 `sdd-generate-tasks` — Hints no G₀ (experiential_prior)

**Quando:** Antes de gerar o grafo de tasks inicial (G₀).

**O que faz:** Embedda a spec completa e consulta o índice. Injeta os top-5 chunks como `experiential_prior` no prompt do `generate-tasks`, permitindo que o Lead _reuse_ padrões de decomposição bem-sucedidos em features anteriores.

**Feature flag:** `--with-memory`

```bash
# Exemplo de fluxo:
# 1. Spec da feature 005 é embeddada
# 2. Top-5 chunks similares recuperados:
#    - "features de auth precisam de migration task"
#    - "QA em handler HTTP usa .feature BDD"
#    - "OAuth2 redirect_uri deve ser validado no handler"
# 3. Chunks injetados como experiential_prior:
#    "Based on previous similar features, consider these patterns: ..."
# 4. G₀ gerado inclui tasks que o Lead teria que Discover (adiantando trabalho)
```

**Impacto esperado:** -30% tokens na geração de G₀ (menos Discover necessário).

#### 4.2.3 `sdd-validate` — Feedback Loop (Utility Signal)

**Quando:** Após execução LATTE, quando `sdd-validate` gera métricas de coordenação.

**O que faz:** Converte métricas LATTE em utility signal e atualiza scores dos chunks usados como hints na feature executada.

```python
from feedback import compute_utility_signal, apply_feedback

# Métricas do LATTE (feature 001)
metrics = {
    "overwrite": {"overwrite_rate": 0.0},    # 0 tasks sobrescritas
    "waste": {"waste_ratio": 0.15},           # 15% chars descartados
    "idle": {"idle_ratio": 0.10},             # 10% rounds ociosos
}

# Computa utility signal
u = compute_utility_signal(metrics)
# u = 1.0 - (0.0×0.4 + 0.15×0.3 + 0.10×0.3) = 0.925

# Classificação
classify_utility(u)  # → "good"

# Delta a aplicar
utility_to_delta(u)  # → (0.925 - 0.5) × 0.2 = 0.085

# Aplica feedback aos chunks usados como hints
result = apply_feedback(u, chunk_hashes=["abc123...", "def456..."])
# → {"utility": 0.925, "classification": "good", "delta": 0.085, "updated": 2, ...}
```

**Fórmula do Utility Signal:**

```
u = 1.0 - (overwrite_rate × 0.4 + waste_ratio × 0.3 + idle_ratio × 0.3)
```

| Peso | Métrica | Significado |
|---|---|---|
| **0.4** | `overwrite_rate` | Retrabalho → output menos confiável |
| **0.3** | `waste_ratio` | Esforço mal direcionado → ineficiência |
| **0.3** | `idle_ratio` | Workers ociosos → DAG mal particionado |

**Mapeamento qualitativo:**

| u | Classificação | Delta | Significado |
|---|---|---|---|
| > 0.7 | `good` | +0.04 a +0.10 | Execução eficiente, hints contribuíram positivamente |
| 0.4–0.7 | `neutral` | 0.0 | Execução padrão, hints sem impacto detectável |
| < 0.4 | `poor` | -0.04 a -0.10 | Execução problemática, hints possivelmente prejudiciais |

#### 4.2.4 `wiki-query` — Modos Semântico e Híbrido

**Quando:** Consultas manuais à wiki.

**O que faz:** Estende a skill `wiki-query` existente com dois modos de retrieval:

- `--semantic` (Feature 002): cosine similarity pura contra embeddings dos chunks
- `--hybrid` (Feature 003): combina cosine similarity + BM25 lexical com α=0.7

Fallback para modo textual (grep-like) se o índice não existir ou estiver vazio.

```bash
# Modo semântico (Feature 002)
hermes wiki query --semantic "como fazer deploy com Docker"

# Modo híbrido (Feature 003) — ideal para termos técnicos exatos
hermes wiki query --semantic "Redis TTL expiração pub/sub" --hybrid

# Modo textual (comportamento original, fallback)
hermes wiki query "deploy Docker"
```

#### 4.2.5 `wiki-ingest` — Auto-Sumarização de `_raw/`

**Quando:** Ao ingerir documentos longos (papers, artigos) em `wiki/_raw/`.

**O que faz:** Detecta arquivos em `_raw/`, extrai YAML frontmatter (title, description), abstract, contribuições e métricas-chave para gerar um chunk de sumário automático indexável.

```python
from summarizer import summarize_raw_doc

chunk = summarize_raw_doc("wiki/_raw/LATTE_Paper.md")
# Retorna:
# {
#     "content": "## Propósito\nLATTE: coordination graph dinâmico...\n\n
#                 ## Principais Contribuições / Achados\n  • Elaboration-based...\n\n
#                 ## Métricas-Chave\n  • 30.8%~80.7% improvement...",
#     "heading_path": "Summary",
#     "source": "wiki/_raw/LATTE_Paper.md",
#     "content_hash": "f3a1b2...",
#     "char_count": 1523,
#     "tags": ["summary", "auto-generated"],
# }
```

---

## 5. Métricas e Thresholds

### 5.1 Critérios de Sucesso (Spec)

| # | Métrica | Baseline | Alvo | Método |
|---|---|---|---|---|
| 1 | **Retrieval quality** | N/A | ≥ 80% top-3 chunks relevantes | LLM-judge em 20 consultas |
| 2 | **Index coverage** | 0% | 100% docs `wiki/` indexados | `COUNT(DISTINCT source)` vs `find wiki/ -name '*.md' \| wc -l` |
| 3 | **Token reduction** | generate-tasks sem hints | -30% tokens na geração de G₀ | Contar tokens antes/depois em 5 features |
| 4 | **Score convergence** | Scores neutros (0.5) | Top-5 hints estáveis após 5 features (σ < 0.1) | Track scores ao longo de features |
| 5 | **Distillation efficacy** | Pré-distillation | -30% chunks pós-distillation | `COUNT(*)` antes/depois |
| 6 | **Index speed** | N/A | Index completo < 30s | `time hermes wiki index --full` |
| 7 | **Query speed** | N/A | Retrieval top-5 < 1s | `time hermes wiki query --semantic "..."` |

### 5.2 Thresholds Operacionais

| Parâmetro | Valor | Descrição |
|---|---|---|
| `MAX_CHUNK_SIZE` | 4096 chars | Chunks maiores são subdivididos por parágrafos |
| `MIN_CHUNK_SIZE` | 50 chars | Chunks menores são ignorados (títulos soltos, linhas em branco) |
| `MIN_CHUNKS_FOR_DISTILL` | 30 | Abaixo disso, distillation é no-op com warning |
| `COSINE_DUPLICATE_THRESHOLD` | 0.95 | Chunks com cosine > threshold são considerados redundantes |
| `SCORE_INITIAL` | 0.5 | Score neutro para novos chunks |
| `SCORE_FLOOR` | 0.1 | Score mínimo (decay nunca zera) |
| `SCORE_CEILING` | 1.0 | Score máximo (capped) |
| `DECAY_AMOUNT` | 0.01 | Penalidade por inatividade (N features sem uso) |
| `INACTIVITY_THRESHOLD` | 5 | Quantos chunks mais recentes são imunes ao decay |
| `FEEDBACK_DELTA_SCALE` | 0.2 | Fator de ajuste fino: delta = (u - 0.5) × 0.2 (máx ±0.10) |
| `LLM_MAX_TOKENS_DISTILL` | 500 | Tokens máximos na síntese de chunk canônico |
| `DISTILL_CONTENT_LIMIT` | 3000 chars | Limite de conteúdo concatenado enviado ao LLM por cluster |
| `MAX_SUMMARY_SIZE` | 2000 chars | Tamanho máximo do sumário automático de `_raw/` |
| `KMEANS_MAX_K` | min(10, n-1) | Número máximo de clusters testados no elbow method |
| `HYBRID_ALPHA` | 0.7 | Peso da similaridade semântica na combinação híbrida (BM25 = 1 − α = 0.3) |
| `HYBRID_THRESHOLD_DEFAULT` | `None` | Threshold adaptativo padrão (sem filtro). Consumidores definem por contexto: brainstorm=0.0, generate-tasks=0.10, query=0.15 |
| `HYBRID_MINMAX_FLOOR` | 0.0 | Floor da normalização min-max: quando todos os scores são idênticos, retorna 0.0 para evitar divisão por zero |

### 5.3 Pesos do Utility Signal

| Peso | Métrica LATTE | Justificativa |
|---|---|---|
| **0.4** | `overwrite_rate` | Overwrites indicam conflitos de dependência — hints podem ter sugerido dependências erradas |
| **0.3** | `waste_ratio` | Chars desperdiçados indicam esforço mal direcionado — hints podem ter sido irrelevantes |
| **0.3** | `idle_ratio` | Workers ociosos indicam paralelismo mal planejado — hints podem ter sugerido decomposição inadequada |

### 5.4 Modelo de Decay

```python
from decay import apply_decay

# Após cada feature, aplicar decay a chunks inativos:
affected = apply_decay(
    inactivity_threshold=5,  # top-5 mais recentes são imunes
    decay_amount=0.01,       # perde 0.01 por ciclo de inatividade
    floor=0.1,               # nunca abaixo de 0.1
)
```

**Exemplo de evolução de scores:**
```
Feature 003: Chunk usado → score 0.5 + 0.08 = 0.58
Feature 004: Chunk NÃO usado → sem update
Feature 005: Chunk NÃO usado → sem update
Feature 006: Chunk NÃO usado → sem update
Feature 007: Chunk NÃO usado → sem update
Feature 008: Chunk NÃO usado → decay: 0.58 - 0.01 = 0.57
Feature 009: Chunk NÃO usado → decay: 0.57 - 0.01 = 0.56
... continua até floor 0.1
```

---

## 6. Exemplos de Uso

### 6.1 Primeira Indexação

```bash
# Indexar toda a wiki
$ hermes wiki index --full

Carregando modelo 'all-MiniLM-L6-v2' ... OK

[1/84] concepts/sdd.md ... 8 chunks (8 embeddados)
[2/84] concepts/sdd-workflow.md ... 12 chunks (12 embeddados)
[3/84] concepts/obsidian-flow.md ... 5 chunks (5 embeddados)
...
[84/84] skills/sdd-validate.md ... 3 chunks (3 embeddados)
------------------------------------------------------------
============================================================
RELATÓRIO DE INDEXAÇÃO
============================================================
  Documentos processados : 84
  Chunks criados         : 312
  Chunks com embedding   : 312
  Erros                  : 0
  Tempo total            : 18.3s
============================================================
```

### 6.2 Consulta Semântica

```bash
# Buscar conteúdo relevante sobre OAuth2 e rate limits
$ hermes wiki query --semantic "OAuth2 rate limits na API da 42" --top-k 5

Carregando modelo 'all-MiniLM-L6-v2' ... OK
Buscando: "OAuth2 rate limits na API da 42"

======================================================================
RESULTADOS DA BUSCA  (5 encontrado(s) em 234ms)
======================================================================

[0.784] references/42-api-specification.md > Rate Limits
    A API da 42 impõe rate limits de 2 requisições por segundo e 1200 por hora...

[0.756] references/oauth2-42-pitfalls.md > Pitfall 1: redirect_uri
    O erro mais comum na integração OAuth2 da 42 é o redirect_uri não...

[0.721] references/42-api-endpoints.md > /v2/me
    GET /v2/me retorna dados do usuário autenticado. Requer token OAuth2...

[0.693] references/go-jwt.md > Setup
    Biblioteca golang-jwt v5 configurada com signing method RS256...

[0.667] references/system-design.md > API Rate Limiting
    Estratégias de rate limiting: token bucket, sliding window...
======================================================================
```

### 6.3 Feedback Loop após Execução LATTE

```python
from feedback import compute_utility_signal, apply_feedback

# 1. Métricas do LATTE após execução da Feature 005
metrics = {
    "overwrite": {"overwrite_rate": 0.0},     # 0% overwrites
    "waste": {"waste_ratio": 0.08},            # 8% chars descartados
    "idle": {"idle_ratio": 0.05},              # 5% rounds ociosos
}

# 2. Computa utility signal
u = compute_utility_signal(metrics)
# u = 1.0 - (0.0×0.4 + 0.08×0.3 + 0.05×0.3) = 0.961
# Classificação: "good"

# 3. Chunks que foram usados como hints na Feature 005
chunk_hashes = [
    "a3f2b9c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
    "b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
]

# 4. Aplica feedback
result = apply_feedback(u, chunk_hashes)
# {
#     "utility": 0.961,
#     "classification": "good",
#     "delta": 0.0922,
#     "updated": 3,
#     "not_found": 0,
#     "total": 3,
# }

# 5. Cada chunk recebe +0.09 de score
# Chunk A: 0.50 → 0.59 (primeira feature, saiu do neutro)
# Chunk B: 0.65 → 0.74 (já tinha bom score, agora sobe mais)
# Chunk C: 0.50 → 0.59
```

### 6.4 Destilação Periódica

```bash
# Após 15 features, o hint pool tem 200+ chunks
$ hermes wiki distill --threshold 0.85

Carregando modelo 'all-MiniLM-L6-v2' ... OK

Clusterizando chunks (threshold=0.85)...
  8 clusters formados (200 chunks total)
Destilando padrões canônicos via LLM...
  8 padrões canônicos gerados
  8 chunks canônicos inseridos no índice
  200 chunks originais marcados com score=0

============================================================
RELATÓRIO DE DESTILAÇÃO
============================================================
  Clusters formados       : 8
  Chunks antes            : 200
  Padrões canônicos       : 8
  Chunks no banco (total) : 208
  Chunks com score=0      : 200
  % de redução            : 96.0%
  Tempo total             : 45.2s
  Total chunks no banco   : 208
  Chunks com embedding    : 208
  Tamanho do banco        : 2.4 MB
============================================================
```

### 6.5 Consulta Programática (Python)

```python
from search import search_similar
from scoring import update_score, get_top_hints
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Busca semântica
results = search_similar(
    query_text="estratégias de caching em Go com Redis",
    model=model,
    k=10,
)

for r in results:
    combined = r["score"] * r["similarity"]
    print(f"[{combined:.3f}] {r['source']} > {r['heading']}")
    print(f"    {r['content'][:120]}...")
    print()

# Feedback manual
for r in results[:3]:  # top-3 foram usados como hints
    update_score(r["content_hash"], delta=+0.05)

# Top hints atuais
top = get_top_hints(k=5)
for hint in top:
    print(f"  score={hint['score']:.3f} | {hint['source']} > {hint['heading']}")
```

### 6.6 Verificação de Cobertura (CI)

```python
from store import get_stats
from pathlib import Path

wiki_count = sum(1 for _ in Path("wiki").rglob("*.md"))
stats = get_stats()
indexed_count = stats["total_sources"]

assert wiki_count == indexed_count, (
    f"Cobertura: {indexed_count}/{wiki_count}. Esperado: 100%."
)

print(f"✅ Cobertura completa: {indexed_count} docs indexados.")
```

---

## 7. Constraints e Edge Cases

### 7.1 Constraints

1. **Hermes nativo:** Tudo roda localmente — embeddings via `all-MiniLM-L6-v2` (23MB, CPU), índice em SQLite. Sem APIs externas, sem GPU.
2. **Wiki como source of truth:** O índice SQLite é sempre reconstruível a partir da wiki. Nenhuma operação modifica arquivos `.md` originais.
3. **Chunking por seção:** Documentos quebrados em headings `##`, com metadados (source, heading_path, tags). Chunks > 4096 chars são subdivididos; < 50 chars são ignorados.
4. **Scores persistem:** Atrelados a `content_hash` (SHA256), sobrevivem a re-indexações. Novo conteúdo = novo hash = score resetado para 0.5.
5. **Distillation não destrutiva:** Nunca deleta conteúdo original da wiki. Chunks sintéticos marcados como `source=_distilled/`. Chunks originais têm score zerado, não removidos.
6. **Cold start resiliente:** Scores neutros (0.5), sistema funciona como retrieval sem feedback até acumular 3+ features.
7. **Modelo de embedding fixo:** Trocar modelo = re-indexação completa (aceitável, index < 30s).

### 7.2 Edge Cases

| # | Edge Case | Comportamento |
|---|---|---|
| 1 | **Wiki vazia** | Índice vazio, retrieval retorna lista vazia. G₀ gerado sem hints (fallback gracioso). |
| 2 | **Documento muito grande (> 1M tokens)** | Chunking em seções, limite de 4096 chars por chunk. Excedente truncado com warning. |
| 3 | **Re-indexação** | Scores preservados por `content_hash`. Chunks removidos da wiki têm scores arquivados (não perdidos). |
| 4 | **Modelo de embedding não instalado** | `pip install sentence-transformers` automático no primeiro uso. Se falhar, indexing aborta com mensagem clara. |
| 5 | **Colisão de hash** | Dois chunks idênticos em docs diferentes → tratados como entradas separadas (metadados diferentes), scores shared via `INSERT OR REPLACE`. |
| 6 | **Cold start (< 3 features)** | Scores neutros (0.5), todos os chunks têm peso igual. Sistema funciona como retrieval sem feedback. |
| 7 | **Distillation sem massa crítica (< 30 chunks)** | No-op com warning: "insufficient data for distillation". |
| 8 | **Chunk muito curto (< 50 chars)** | Ignorado na indexação (títulos soltos, linhas em branco). |
| 9 | **Encoding quebrado** | Documento com caracteres inválidos → chunk ignorado, warning logado, indexação continua. |

---

## 8. ADRs (Architecture Decision Records)

| ADR | Decisão | Justificativa |
|---|---|---|
| **ADR-001** | `all-MiniLM-L6-v2` como modelo fixo | Mesmo modelo do A-MapReduce. 23MB, CPU-only, 384d. 1.5KB/chunk. |
| **ADR-002** | SQLite como store de embeddings | Embedded, zero infra, já usado no Hermes. Scan sequencial de 500 chunks < 10ms — não justifica pgvector/FAISS/Chroma. |
| **ADR-003** | Chunking por headings `##` com fallback parágrafos | Headings são estrutura natural do Markdown. Cada seção tende a ser autocontida → chunks semanticamente coerentes. |
| **ADR-004** | Scores por `content_hash` (SHA256) | Sobrevivem a re-indexações. Conteúdo mudou → hash diferente → score resetado (nova evidência necessária). |
| **ADR-005** | Distillation como operação explícita (não contínua) | Clusterização + síntese LLM é cara. Rodar a cada feature seria desperdício. Usuário revisa chunks canônicos antes de commitá-los. |
| **ADR-006** | Índice derivado, wiki como source of truth | Índice sempre reconstruível. Corrompeu? `reindex()`. Distillation gerou bobagem? Chunks `_distilled/` podem ser dropados sem afetar a wiki. |
| **ADR-007** | Pesquisa híbrida cosine+BM25 com α=0.7 | Cosine captura similaridade conceitual (paráfrases, tópicos), BM25 captura tokens exatos (siglas, código). α=0.7 privilegia semântica na wiki conceitual do 42 Framework. Normalização min-max evita dominância de escala. |

Plan completo em: `specs/features/002-experiential-memory/plan.md`

---

## 9. Dependências

### 9.1 Feature 001 (LATTE Coordination)

A Feature 002 **depende** da Feature 001 especificamente para o **M2.3 (Hint Scoring + Feedback Loop)**. O feedback loop consome métricas de coordenação geradas pelo `sdd-validate` pós-execução LATTE:

- `overwrite_rate` — tasks que tiveram output sobrescrito por outro worker
- `waste_ratio` — caracteres produzidos e descartados
- `idle_ratio` — % de rounds sem progresso

**Sem a Feature 001**, os milestones M2.1 (Indexação), M2.2 (Retrieval) e M2.4 (Distillation) funcionam independentemente. Apenas o feedback loop (M2.3) fica inoperante — scores permanecem neutros (0.5) e o sistema opera como retrieval semântico puro, ainda útil mas sem o ciclo de melhoria contínua.

### 9.2 Feature 003 (Hybrid Retrieval)

A Feature 003 **depende** da Feature 002 para o índice semântico (SQLite + embeddings) e para o pipeline de chunking. Ela **não depende** da Feature 001 (LATTE), pois o retrieval híbrido opera exclusivamente no plano de busca, sem consumir métricas de coordenação.

**Dependências externas adicionais da Feature 003:**
- `rank-bm25` (pip) — implementação BM25Okapi para scoring lexical

---

## 10. Schema SQLite

```sql
CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY,
    source      TEXT,
    heading     TEXT,
    content     TEXT,
    embedding   BLOB,
    score       REAL DEFAULT 0.5,
    content_hash TEXT UNIQUE,
    tags        TEXT,          -- JSON array: ["tag1", "tag2"]
    char_count  INTEGER,
    created_at  TEXT,          -- ISO 8601 UTC
    last_updated TEXT          -- ISO 8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_content_hash ON chunks(content_hash);
CREATE INDEX IF NOT EXISTS idx_source ON chunks(source);
CREATE INDEX IF NOT EXISTS idx_score ON chunks(score);
```

**Localização:** `~/.hermes/wiki_index.db`
**Journal mode:** WAL (Write-Ahead Logging)
**Encoding:** UTF-8
**Embedding:** BLOB de 1536 bytes (384 × float32)

---

## 11. Tasks (Resumo do DAG)

### Feature 002 (Experiential Memory)
- **Total:** 30 tasks atômicas em 4 fases canônicas
- **Fase 1 — Fundação:** T001–T004 (indexação semântica)
- **Fase 2 — Implementação:** T005–T016 (retrieval + scoring + distillation)
- **Fase 3 — Validação:** T017–T024 (8 smoke tests, 53% paralelizáveis)
- **Fase 4 — Documentação:** T025–T030 (atualização de 6 páginas wiki)
- **Paralelismo:** 16/30 tasks (53%)
- **Ciclos:** 0
- **Dependências quebradas:** 0

DAG completo em: `specs/features/002-experiential-memory/tasks.md`

### Feature 003 (Hybrid Retrieval)
- **Total:** 14 tasks atômicas em 3 fases
- **Fase 1 — BM25 + Hybrid Search:** T001–T006 (bm25.py, search.py híbrido, cli_query.py --hybrid, normalize_frontmatter.py, integração wiki-query SKILL.md)
- **Fase 2 — Validação:** T007–T010 (test_hybrid_retrieval, smoke tests de qualidade híbrida vs semântica)
- **Fase 3 — Documentação:** T011–T014 (atualização de docs wiki, incluindo esta página)
- **Dependência:** Feature 002 (índice + chunker)

---

## 12. Relacionado

- **Spec 002:** `specs/features/002-experiential-memory/spec.md`
- **Plan 002 (ADRs):** `specs/features/002-experiential-memory/plan.md`
- **Tasks 002 (DAG):** `specs/features/002-experiential-memory/tasks.md`
- **Spec 003:** `specs/features/003-hybrid-retrieval/spec.md`
- **Plan 003:** `specs/features/003-hybrid-retrieval/plan.md`
- **Tasks 003:** `specs/features/003-hybrid-retrieval/tasks.md`
- **Paper A-MapReduce:** `wiki/_raw/A-MapReduce_ExecutingWideSearchviaAgenticMapReduce.md`
- **Paper LATTE:** `wiki/_raw/ImprovingtheEfficiencyofLanguageAgentTeamswithAdaptiveTaskGraphs.md`
- **Feature 001:** `specs/features/001-latte-coordination/spec.md` — dependência para feedback loop
- **Feature doc:** `wiki/projects/42_Framework/features/002-experiential-memory.md`
- **Dependência pip:** `rank-bm25` — BM25 lexical scoring para modo híbrido
- **Conceitos:** [[concepts/sdd|SDD]], [[concepts/obsidian-flow|Fluxo Obsidian]]
- **Toolkits:** [[skills/brain|brain toolkit]] — wiki-query, wiki-ingest, wiki-synthesize, wiki-dedup
