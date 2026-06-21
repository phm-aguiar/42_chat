---
feature_id: "002"
title: "Wiki Experiential Memory — Memória Experiencial com Indexação Semântica"
spec: "specs/features/002-experiential-memory/spec.md"
plan: "specs/features/002-experiential-memory/plan.md"
created: "2026-06-19"
author: phm-aguiar
depends_on: "001-latte-coordination"
---

# Tasks — Wiki Experiential Memory

> DAG de 30 tasks atômicas em 4 fases canônicas, cobrindo 4 milestones (M2.1–M2.4).

## Fase 1: Fundação (M2.1 — Indexação Semântica)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T001 | Instalar dependências: `sentence-transformers` + `all-MiniLM-L6-v2`. Verificar download automático na primeira execução | Dev | Nenhuma | false | `requirements.txt` ou `pyproject.toml` (patch), `.hermes/skills/wiki/experiential-memory/setup.py` |
| T002 | Implementar chunking: quebra docs por headings `##`, fallback parágrafos, gera `content_hash = SHA256(content)`, metadados (source, heading_path, tags) | Dev | T001 | false | `.hermes/skills/wiki/experiential-memory/chunker.py` |
| T003 | Implementar store SQLite: schema `chunks(id, source, heading, content, embedding BLOB, score REAL, content_hash TEXT)`, índices por hash, source, score | Dev | T002 | false | `.hermes/skills/wiki/experiential-memory/store.py` |
| T004 | Implementar CLI `hermes wiki index --full`: percorre `wiki/`, chunka, embedda (all-MiniLM-L6-v2), insere. Relatório final com stats | Dev | T003 | false | `.hermes/skills/wiki/experiential-memory/cli_index.py` |

## Fase 2: Implementação (M2.2 + M2.3 + M2.4)

### M2.2 — Retrieval Contextual

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T005 | Implementar cosine similarity search: embed query → dot product contra todos embeddings → top-k por score × similarity | Dev | T003 | false | `.hermes/skills/wiki/experiential-memory/search.py` |
| T006 | Implementar CLI `hermes wiki query --semantic "texto" --top-k N`: embedda query, search, retorna JSON com chunks + scores + similarities | Dev | T004, T005 | false | `.hermes/skills/wiki/experiential-memory/cli_query.py` |
| T007 | Integrar `wiki-query`: estender skill existente com modo `--semantic`. Fallback para modo textual se índice não existe | Dev | T006 | false | `.hermes/skills/wiki/wiki-query/SKILL.md` (patch) |
| T008 | Integrar `sdd-generate-tasks`: consultar índice antes de gerar G₀. Injectar top-5 chunks como `experiential_prior` no prompt. Feature flag: `--with-memory` | Dev | T007 | true | `.hermes/skills/sdd/generate-tasks/SKILL.md` (patch) |
| T009 | Integrar `sdd-brainstorm`: ao iniciar entrevista, consultar índice por features similares. Injectar hints como contexto adicional | Dev | T007 | true | `.hermes/skills/sdd/brainstorm/SKILL.md` (patch) |

### M2.3 — Hint Scoring + Feedback

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T010 | Implementar score update: `score(chunk_id, delta)` — atualiza score no SQLite. Scores inicializados como 0.5. Range [0, 1] | Dev | T007 | false | `.hermes/skills/wiki/experiential-memory/scoring.py` |
| T011 | Integrar `sdd-validate`: após métricas de coordenação (LATTE), converter overwrite/wasted/idle em utility signal. Atualizar scores dos chunks usados como hints | Dev | T010 | false | `.hermes/skills/sdd/validate/SKILL.md` (patch), `.hermes/skills/wiki/experiential-memory/feedback.py` |
| T012 | Implementar score decay: chunks não usados por N features perdem 0.01 por feature. Floor = 0.1. Evita hints obsoletos no topo | Dev | T010 | false | `.hermes/skills/wiki/experiential-memory/decay.py` |

### M2.4 — Distillation

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T013 | Implementar clusterização: KMeans sobre embeddings (k = n_clusters auto via elbow). Agrupa chunks similares por cosseno > threshold | Dev | T007 | false | `.hermes/skills/wiki/experiential-memory/cluster.py` |
| T014 | Implementar geração de chunks canônicos: para cada cluster, síntese via LLM dos chunks (prompt: "consolide esses hints em 1 padrão canônico"). Score agregado = média ponderada | Dev | T013 | false | `.hermes/skills/wiki/experiential-memory/distill.py` |
| T015 | Implementar CLI `hermes wiki distill`: executa cluster → síntese → atualiza índice (chunks originais score=0, canônicos inseridos como `source=_distilled/`). Relatório antes/depois | Dev | T014 | false | `.hermes/skills/wiki/experiential-memory/cli_distill.py` |
| T016 | Implementar sumarização de `_raw/` na ingestão: `wiki-ingest` detecta docs em `_raw/`, gera chunk `Summary` automático (propósito, achados, métricas). Chunk indexado como os demais | Dev | T004 | true | `.hermes/skills/wiki/wiki-ingest/SKILL.md` (patch), `.hermes/skills/wiki/experiential-memory/summarizer.py` |

## Fase 3: Validação (QA — Smoke Tests)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T017 | Smoke — indexação completa: roda `index --full`, verifica `COUNT(DISTINCT source) = COUNT(wiki/*.md)`. 100% coverage | QA | T004, T005 | true | `.hermes/skills/wiki/experiential-memory/tests/test_index_coverage.py` |
| T018 | Smoke — retrieval quality: 20 consultas pré-definidas, LLM-judge avalia top-3 chunks (relevante/não). ≥ 80% precisão | QA | T017 | true | `.hermes/skills/wiki/experiential-memory/tests/test_retrieval_quality.py` |
| T019 | Smoke — token reduction: gerar G₀ de 3 features com e sem hints. Contar tokens. -30% vs baseline | QA | T017 | true | `.hermes/skills/wiki/experiential-memory/tests/test_token_reduction.py` |
| T020 | Smoke — score convergence: simular 5 features consecutivas. Verificar top-5 hints estáveis (desvio padrão scores < 0.1) | QA | T019 | false | `.hermes/skills/wiki/experiential-memory/tests/test_score_convergence.py` |
| T021 | Smoke — distillation efficacy: rodar `distill`, verificar `COUNT(*)` chunks < 70% do original. Chunks canônicos gerados > 0 | QA | T020 | false | `.hermes/skills/wiki/experiential-memory/tests/test_distill_efficacy.py` |
| T022 | Smoke — index speed: `time index --full` < 30s. Smoke — query speed: `time query --semantic` < 1s para top-5 | QA | T004, T005 | true | `.hermes/skills/wiki/experiential-memory/tests/test_speed.py` |
| T023 | Smoke — re-indexação idempotente: index 2×, verificar scores preservados (content_hash match). Chunks removidos da wiki → scores arquivados | QA | T004, T005, T010 | true | `.hermes/skills/wiki/experiential-memory/tests/test_reindex_idempotent.py` |
| T024 | Smoke — cold start: wiki com < 10 docs. Index não quebra, query retorna resultados (poucos), sem crash | QA | T004, T005 | true | `.hermes/skills/wiki/experiential-memory/tests/test_cold_start.py` |

## Fase 4: Documentação (Wiki Update)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T025 | Atualizar `wiki/concepts/obsidian-flow.md`: adicionar fluxo de indexação semântica + retrieval | Dev | T017, T021 | true | `wiki/concepts/obsidian-flow.md` |
| T026 | Atualizar `wiki/skills/wiki-query.md`: documentar modo `--semantic` | Dev | T017, T021 | true | `wiki/skills/wiki-query.md` |
| T027 | Atualizar `wiki/skills/wiki-ingest.md`: documentar auto-summarize de `_raw/` | Dev | T017, T021 | true | `wiki/skills/wiki-ingest.md` |
| T028 | Criar `wiki/references/toolkits/wiki/experiential-memory.md`: documentação completa da feature 002 | Dev | T017, T021 | true | `wiki/references/toolkits/wiki/experiential-memory.md` |
| T029 | Atualizar `wiki/skills/sdd-generate-tasks.md`: documentar `experiential_prior` e `--with-memory` | Dev | T017, T021 | true | `wiki/skills/sdd-generate-tasks.md` |
| T030 | Atualizar `wiki/skills/sdd-validate.md`: documentar utility signal → score update | Dev | T017, T021 | true | `wiki/skills/sdd-validate.md` |

## Validação do DAG

### Anti-ciclo (DFS)
```
T001 → T002 → T003 → T004
T003 → T005 → T006 → T007
T004+T005 → T017, T022
T004+T005+T010 → T023
T006 → T007
T007 → T008, T009, T010, T013
T008 ∥ T009
T010 → T011, T012
T013 → T014 → T015
T004 → T016
T017 → T018, T019
T019 → T020 → T021
T004+T005 → T024
```
✅ **Sem ciclos detectados.**

### Dependências quebradas
✅ Todas as refs em `Dependências` existem.

### Órfãs
- T030: último nó, sem dependentes → ✅ intencional (artefato final)
- T024: sem dependentes → ✅ intencional (teste isolado de cold start)

### Conflitos de arquivos
| Batch paralelo | Tasks | Arquivos | Conflito? |
|---|---|---|---|
| Fase 2 M2.2 | T008, T009 | `generate-tasks/SKILL.md`, `brainstorm/SKILL.md` | ✅ Disjuntos |
| Fase 2 M2.3 | T011, T012 | `validate/SKILL.md`, `decay.py` | ✅ Disjuntos |
| Fase 2 M2.4 | T016 ∥ T013-T015 | `wiki-ingest/SKILL.md`, `cluster.py`/`distill.py`/`cli_distill.py` | ✅ Disjuntos |
| Fase 3 bat 1 | T017, T022, T023 | `test_index_coverage.py`, `test_speed.py`, `test_reindex_idempotent.py` | ✅ Disjuntos |
| Fase 3 bat 2 | T018, T019 | `test_retrieval_quality.py`, `test_token_reduction.py` | ✅ Disjuntos |
| Fase 4 todas | T025-T030 | 6 páginas wiki distintas | ✅ Disjuntos |

### Sumário
- **Total tasks:** 30
- **Dev:** 16 (T001-T016)
- **QA:** 8 (T017-T024)
- **Dev (docs):** 6 (T025-T030)
- **Paralelizáveis:** 16/30 (53%)
- **Ciclos:** 0
- **Deps quebradas:** 0
- **Conflitos de arquivo:** 0
