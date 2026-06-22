---
title: "002: Wiki Experiential Memory"
status: specified
created: "2026-06-19"
rag_score: 0.4817
tags:
  - memory
  - embeddings
  - retrieval
  - hints
  - feedback-loop
  - sdd
summary: "Memória experiencial com indexação semântica de chunks da wiki, retrieval contextual, hint scoring com feedback loop, e distillation periódica. Inspirado no Experiential Memory do A-MapReduce."
---

# 002: Wiki Experiential Memory — Memória Experiencial com Indexação Semântica

> Transforma a wiki Obsidian de documentação estática em **memória experiencial viva**: indexação semântica de chunks, retrieval contextual, hint scoring automático com feedback loop, e distillation periódica.

## Status

**Specified.** Spec, plan e tasks aprovados. Implementação pendente.

| Artefato | Status | Link |
|---|---|---|
| Spec | ✅ Aprovado | [spec.md](../../../../specs/features/002-experiential-memory/spec.md) |
| Plan (ADRs) | ✅ Pronto | [plan.md](../../../../specs/features/002-experiential-memory/plan.md) |
| Tasks (DAG) | ✅ Pronto | [tasks.md](../../../../specs/features/002-experiential-memory/tasks.md) |

---

## Resumo do Paper A-MapReduce e Aplicação

### O Paper

**A-MapReduce: Executing Wide Search via Agentic MapReduce** (Chen et al., 2026) propõe um framework multi-agente inspirado no paradigma MapReduce para tarefas de *wide search* — buscas de larga escala com grande número de alvos de recuperação. O paper identifica dois dilemas dos MAS tradicionais:

1. **Dilemma 1:** A maioria dos MAS gerencia alvos de retrieval implicitamente via histórico de diálogo ou planos textuais livres, resultando em entradas perdidas, redundância e desalinhamento em execuções longas.
2. **Dilemma 2:** MAS existentes tipicamente re-planejam pipelines para cada query, sem abstrair padrões estruturais compartilhados entre queries similares.

A solução do A-MapReduce: **memória experiencial** — um mecanismo que destila trajetórias de execução de tarefas passadas em *hints estruturais reutilizáveis*, condicionando a decomposição e execução de tarefas futuras nessa memória.

### Resultados Reportados

- **Runtime:** -34.7% (vs variante sem evolução)
- **Custo:** -42.8% ($1.05 → $0.60)
- **Qualidade:** +5.15pp em Item F1 (vs sem memória)

### Como Foi Aplicado à Feature 002

O pipeline SDD atual consulta a wiki de forma textual (grep-like), carregando documentos inteiros. Um paper de 100K tokens é lido por inteiro quando só 3 parágrafos são relevantes. Padrões de decomposição bem-sucedidos não são automaticamente recuperados.

A Feature 002 transpõe o padrão de *experiential memory* do A-MapReduce para o contexto da wiki do SDD:

| Conceito A-MapReduce | Aplicação na Feature 002 |
|---|---|
| **Experiential Memory** | Índice semântico de chunks da wiki (SQLite + embeddings) |
| **Hint scoring com feedback** | Métricas do LATTE (overwrite rate, wasted chars, idle rounds) atualizam scores dos chunks usados como hints |
| **Distillation (Fψ)** | `wiki-distill`: clusterização + síntese canônica, remove redundância sem perder conhecimento |
| **Query-conditioned task decomposition** | `sdd-generate-tasks` consulta o índice e injeta top-5 chunks como `experiential_prior` no prompt |
| **Cross-task pattern reuse** | Hints de features bem-sucedidas ganham peso; features problemáticas perdem. Scores persistem entre sessões |

---

## Milestones

### M2.1: Indexação Semântica

Script que percorre `wiki/`, quebra docs em chunks por seção (`##`), gera embeddings via `all-MiniLM-L6-v2`, armazena em índice local (SQLite + vetor float blob). Cobertura: 100% dos documentos em `wiki/` indexados em < 30s.

**Tasks:** T001–T004 (Fase 1: Fundação)

### M2.2: Retrieval Contextual

API de query: dado texto (spec, tarefa), retorna top-k chunks por similaridade cosseno. Integração com `wiki-query` (modo `--semantic`), `sdd-generate-tasks` (hints no G₀), `sdd-brainstorm` (contexto de features similares). Retrieval top-5 < 1s.

**Tasks:** T005–T009 (Fase 2: M2.2)

### M2.3: Hint Scoring + Feedback Loop

Cada chunk/index entry ganha score (inicial neutro = 0.5). Métricas do `sdd-validate` pós-LATTE (overwrite rate, wasted chars, idle rounds) são convertidas em utility signal e atualizam scores. Score decay: chunks não usados por N features perdem 0.01/feature (floor = 0.1). Scores persistem entre sessões via `content_hash` (SHA256).

**Tasks:** T010–T012 (Fase 2: M2.3)

### M2.4: Distillation

Comando periódico (`wiki-distill`) que clusteriza chunks similares (KMeans), remove duplicatas (cosseno > 0.95), e sintetiza chunks canônicos por cluster via LLM. Similar ao operador Fψ do A-MapReduce. Reduz entropia do hint pool sem perder conhecimento — chunks redundantes têm score zerado (não deletados). Alvo: -30% chunks pós-distillation.

**Tasks:** T013–T016 (Fase 2: M2.4)

---

## Critérios de Sucesso

| # | Métrica | Baseline | Alvo | Método |
|---|---|---|---|---|
| 1 | **Retrieval quality** | N/A | ≥ 80% top-3 chunks julgados relevantes | LLM-judge em 20 consultas |
| 2 | **Index coverage** | 0% | 100% docs em `wiki/` indexados | `find wiki/ -name '*.md' \| wc -l` vs `COUNT(DISTINCT source)` |
| 3 | **Token reduction** | Baseline: generate-tasks sem hints | -30% tokens na geração de G₀ | Contar tokens antes/depois em 5 features |
| 4 | **Score convergence** | Scores aleatórios (inicial 0.5) | Top-5 hints estáveis após 5 features (σ < 0.1) | Track scores ao longo de features consecutivas |
| 5 | **Distillation efficacy** | Pré-distillation | -30% chunks no índice pós-distillation | `COUNT(*)` antes/depois |
| 6 | **Index speed** | N/A | Index completo < 30s | `time hermes wiki index --full` |
| 7 | **Query speed** | N/A | Retrieval top-5 < 1s | `time hermes wiki query --semantic "..."` |

---

## Dependência: Feature 001 (LATTE)

A Feature 002 **depende** da Feature 001 (LATTE Coordination) especificamente para o **M2.3 (Hint Scoring + Feedback Loop)**. O feedback loop consome as métricas de coordenação geradas pelo `sdd-validate` pós-execução LATTE:

- `overwrite_rate` — tasks que tiveram output sobrescrito por outro worker
- `wasted_chars` — caracteres produzidos e descartados
- `idle_rounds` — % de rounds sem progresso

Essas métricas são convertidas em *utility signal* que atualiza os scores dos chunks usados como hints na feature executada. Hints que levaram a boa execução (poucos overwrites, baixo desperdício) ganham peso; hints de features problemáticas perdem.

**Sem a Feature 001**, os milestones M2.1, M2.2 e M2.4 funcionam independentemente. Apenas o feedback loop (M2.3) fica inoperante — scores permanecem neutros (0.5) e o sistema opera como retrieval semântico puro, ainda útil mas sem o ciclo de melhoria contínua.

---

## Modelo de Embedding: `all-MiniLM-L6-v2`

### Escolha

**`sentence-transformers/all-MiniLM-L6-v2`** — 384 dimensões, ~23MB, roda em CPU sem GPU, sem API key.

### Justificativa

| Critério | all-MiniLM-L6-v2 | Alternativa rejeitada (multilingual-e5-small) |
|---|---|---|
| **Validação prévia** | ✅ Mesmo modelo usado no A-MapReduce com resultados reportados | ❌ Não validado no contexto de wide search |
| **Tamanho** | 23MB | 118MB (5× maior) |
| **Setup** | Zero configuração — `pip install sentence-transformers` | Requer prefixos `"query:"` / `"passage:"` nos inputs |
| **Dimensões** | 384d → 1.5KB por chunk (500 chunks = ~750KB) | 384d também, mas modelo 5× maior em disco |
| **Cobertura linguística** | Inglês excelente; português razoável via transfer learning (línguas indo-europeias) | Pt-BR nativo, mas sobrekill para wiki bilíngue |
| **Armazenamento** | SQLite BLOB (384 × 4 bytes float32) | Mesmo formato, mas download inicial 5× mais lento |

Além disso, o modelo é **fixo** — trocar requer re-indexação completa, o que é aceitável (índice < 30s). O índice é sempre reconstruível a partir da wiki (idempotente).

**ADR completo:** Ver [plan.md — ADR-001](../../../../specs/features/002-experiential-memory/plan.md#adr-001-all-MiniLM-L6-v2-como-modelo-de-embedding).

---

## Arquitetura Resumida

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

### Contratos da API de Índice

```python
index(paths: list[str])        → percorre paths, chunka, embedda, insere
query(text: str, k: int = 5)   → embedda text, cosine similarity, retorna top-k
score(chunk_id, delta: float)  → atualiza score do chunk (feedback loop)
distill(threshold: float=0.95) → clusteriza, remove redundância, gera canônicos
reindex()                      → limpa índice e re-indexa do zero (idempotente)
```

---

## Constraints

1. **Hermes nativo:** Tudo local — embeddings via `all-MiniLM-L6-v2` (23MB, CPU), índice em SQLite.
2. **Wiki como source of truth:** Índice sempre derivado da wiki. Re-indexação idempotente.
3. **Chunking por seção:** Docs quebrados em headings `##`, com metadados (source, heading_path, tags).
4. **Scores persistem:** Atrelados a `content_hash` (SHA256), sobrevivem a re-indexações.
5. **Distillation não destrutiva:** Nunca deleta conteúdo original. Chunks sintéticos marcados como `source=_distilled/`.
6. **Cold start resiliente:** Scores neutros (0.5), sistema funciona como retrieval sem feedback até acumular 3+ features.

---

## Tasks (Resumo do DAG)

- **Total:** 30 tasks atômicas em 4 fases canônicas
- **Fase 1 — Fundação:** T001–T004 (indexação semântica)
- **Fase 2 — Implementação:** T005–T016 (retrieval + scoring + distillation)
- **Fase 3 — Validação:** T017–T024 (8 smoke tests, 53% paralelizáveis)
- **Fase 4 — Documentação:** T025–T030 (atualização de 6 páginas wiki)
- **Paralelismo:** 16/30 tasks (53%)
- **Ciclos:** 0
- **Dependências quebradas:** 0

DAG completo em [tasks.md](../../../../specs/features/002-experiential-memory/tasks.md).

---

## Relacionado

- Paper A-MapReduce: [[references/papers/A-MapReduce|A-MapReduce — Executing Wide Search via Agentic MapReduce]]
- Paper LATTE: [[references/papers/LATTE|LATTE — Language Agent Teams for Task Evolution]]
- Feature 001: [specs/features/001-latte-coordination/](../../../../specs/features/001-latte-coordination/spec.md) — dependência para feedback loop
- [[concepts/sdd|SDD]] — Metodologia
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Integração wiki ↔ pipeline
- [[skills/brain|brain toolkit]] — wiki-query, wiki-ingest, wiki-synthesize, wiki-dedup
