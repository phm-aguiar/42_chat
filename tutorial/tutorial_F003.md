# Tutorial — Feature 003: Hybrid Retrieval & Normalization

> **Status:** ✅ Implementado em `.hermes/skills/wiki/experiential_memory/`
> (mesmo diretório da 002 — estende search.py + adiciona bm25.py e
> normalize_frontmatter.py)

Feature enxuta que resolve o maior gap da 002: **busca semântica sozinha não
acha termos exatos**. Códigos, stack traces, hashes hexadecimais, nomes de
classe — cosine similarity falha nisso. BM25 resolve.

---

## O que ela faz (3 coisas)

### 1. Fusão híbrida BM25 + cosine

```
hybrid_score = 0.7 * cosine_norm + 0.3 * bm25_norm
```

Na prática:

```bash
# Só semântico (comportamento da 002)
python3 cli_query.py --semantic "autenticação OAuth2"

# Híbrido (BM25 + semântico)
python3 cli_query.py --hybrid "pqxx::connection" --top-k 3
```

O α=0.7 prioriza semântico (que já funciona bem) mas dá peso ao BM25 pra
queries exatas. O parâmetro `--alpha` é exposto se quiser ajustar.

### 2. Thresholds adaptativos

```bash
# Consulta interativa — threshold baixo (0.50), mais resultados
python3 cli_query.py --hybrid --threshold 0.50 "migration auth"

# Cross-link automático — threshold alto (0.70), só resultados fortes
python3 cli_query.py --hybrid --threshold 0.70 "error handling"
```

Default sem threshold = sem filtro (compatível com 002).

### 3. Normalização de frontmatter

34 docs da wiki estão sem YAML frontmatter. O script adiciona o mínimo:

```yaml
---
title: "Nome do Documento"
tags: []
created: "2026-06-20"
---
```

```bash
# Preview seco — não modifica nada
python3 normalize_frontmatter.py --dry-run

# Manda ver
python3 normalize_frontmatter.py

# Depois reindexa pra tudo ficar consistente
python3 cli_index.py --full
```

---

## Tasks implementadas (15, 60% paralelizáveis)

| Fase | Módulos | O que faz |
|---|---|---|
| 1. BM25 + Fusão | `bm25.py`, `search.py` (patch), `cli_query.py` (patch) | BM25 scoring, fusão híbrida, integração CLI |
| 2. Normalização | `normalize_frontmatter.py` | Detecta + adiciona YAML frontmatter |
| 3. Validação | testes | Ganho lexical ≥20%, thresholds, compat |

---

## ADRs

| ADR | Decisão | Por quê |
|---|---|---|
| ADR-001 | `rank_bm25`, não FTS5 | BM25 canônico, pip install, <50ms pra 2000 chunks |
| ADR-002 | α=0.7 default | Cosine já validado, BM25 complementa sem dominar |
| ADR-003 | Só docs sem frontmatter | Minimiza risco nos que já têm YAML |
| ADR-004 | Threshold por chamada | Contexto diferente exige thresholds diferentes |

---

## Uso no dia a dia

```bash
cd /home/zeenyt__/Projetos/42_chat/.hermes/skills/wiki/experiential_memory

# Setup único
pip install rank-bm25
python3 normalize_frontmatter.py --dry-run   # ver o que vai mudar
python3 normalize_frontmatter.py             # aplicar
python3 cli_index.py --full                   # reindexar

# Busca
python3 cli_query.py --hybrid "pqxx::connection" --top-k 3
python3 cli_query.py --hybrid "stack trace segmentation fault" --threshold 0.50
```

---

## Integração no pipeline

No pipeline SDD, `cli_query.py --hybrid` substitui `--semantic` quando a
consulta tem termos técnicos exatos. O `sdd-generate-tasks` com
`--with-memory` já usa híbrido automaticamente (a 003 estende a 002, a
integração é transparente).
