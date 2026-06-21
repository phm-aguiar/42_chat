---
feature_id: "002"
plan_for: "Wiki Experiential Memory — Memória Experiencial com Indexação Semântica"
spec: "specs/features/002-experiential-memory/spec.md"
created: "2026-06-19"
author: phm-aguiar
stack: "Hermes Agent (Python), SQLite, sentence-transformers (all-MiniLM-L6-v2)"
depends_on: "001-latte-coordination"
---

# Plano Arquitetural — Wiki Experiential Memory

## Metadados

| Campo | Valor |
|---|---|
| **Stack** | Hermes Agent (Python), SQLite, `sentence-transformers` (all-MiniLM-L6-v2), Obsidian wiki |
| **Feature fonte** | `specs/features/002-experiential-memory/spec.md` |
| **Escopo (1 frase)** | Indexação semântica de chunks da wiki com retrieval contextual, hint scoring com feedback loop, e distillation periódica — wiki como memória experiencial viva |
| **Dependência** | Feature 001 (LATTE) para métricas de coordenação usadas como utility signal no M2.3 |

## Contratos e Fronteiras

### Entrada

| Artefato | Formato | Fonte |
|---|---|---|
| Documentos da wiki | Markdown (.md) em `wiki/` | Vault Obsidian |
| Comando `index --full` | CLI: `hermes wiki index --full` | Usuário ou cron |
| Comando `query --semantic` | CLI: `hermes wiki query --semantic "texto"` | Pipeline SDD (generate-tasks, brainstorm) |
| Métricas de coordenação | JSON: `{overwrite_rate, wasted_chars, idle_rounds, ...}` | `sdd-validate` pós-LATTE (feature 001) |
| Comando `distill` | CLI: `hermes wiki distill` | Usuário ou cron |

### Saída

| Artefato | Formato | Destino |
|---|---|---|
| Índice de embeddings | SQLite: `~/.hermes/wiki_index.db` | Consumido pelas queries |
| Chunks + metadados | Tabela `chunks`: `{id, source, heading, content, embedding, score, content_hash}` | Índice |
| Resultado de query | JSON: `[{chunk_id, source, heading, content, score, similarity}]` | stdout / pipeline SDD |
| Scores atualizados | Coluna `score` na tabela `chunks` | Persiste entre sessões |
| Chunks canônicos (distillation) | Novas entradas em `chunks` com `source=_distilled/` | Índice |

### Operadores (API do índice)

```
index(paths: list[str])        → percorre paths, chunka, embedda, insere no SQLite
query(text: str, k: int = 5)   → embedda text, cosine similarity contra índice, retorna top-k
score(chunk_id, delta: float)  → atualiza score do chunk (feedback loop)
distill(threshold: float=0.95) → clusteriza, remove redundância, gera canônicos
reindex()                      → limpa índice e re-indexa do zero (idempotente)
```

### Fronteiras (o que NÃO é contratual)

- O índice NÃO modifica arquivos da wiki (só lê)
- Scores NÃO são visíveis no Obsidian (são metadados do índice, não da wiki)
- Distillation NÃO deleta conteúdo original da wiki (cria novos chunks sintéticos)
- O modelo de embedding NÃO é fine-tunado nos dados da wiki
- A busca NÃO é híbrida (lexical + semântica) — v1 é só semântica

## ADRs (Architecture Decision Records)

### ADR-001: all-MiniLM-L6-v2 como modelo de embedding

**Decisão:** Usar `sentence-transformers/all-MiniLM-L6-v2` (384 dimensões, ~23MB) como modelo fixo de embeddings.

**Justificativa:** Mesmo modelo usado no A-MapReduce com resultados validados. Roda em CPU, sem GPU, sem API key. 384 dimensões é compacto o suficiente para SQLite blob storage (384 × 4 bytes = 1.5KB por chunk). Para 500 chunks, índice ocupa ~750KB de embeddings.

**Alternativa rejeitada:** `intfloat/multilingual-e5-small` (multilingual, pt-BR incluído). Rejeitado porque (a) é maior (118MB), (b) requer prefixo "query:" / "passage:" nos inputs, (c) A-MapReduce validou all-MiniLM-L6-v2 em tarefa similar de retrieval semântico. A wiki tem docs em pt-BR e EN — all-MiniLM cobre inglês bem e português razoavelmente via transfer learning (ambas línguas indo-europeias compartilham espaço de embedding).

### ADR-002: SQLite como store de embeddings

**Decisão:** Armazenar embeddings como BLOB (float32, 384 × 4 bytes) em SQLite, com índices por `content_hash`, `source`, e `score`.

**Justificativa:** SQLite é embedded (zero infra), já usado no Hermes (state.db), suporta queries com ORDER BY + LIMIT eficientes. Para cosine similarity contra 500 chunks, um scan sequencial em Python (dot product + norma) é < 10ms — não justifica pgvector, faiss, ou Chroma.

**Alternativa rejeitada:** Chroma / FAISS. Rejeitado porque (a) adiciona dependência pesada (C++ extensions), (b) overkill para 500-2000 chunks, (c) A-MapReduce usa JSON simples — SQLite já é um upgrade sobre isso.

### ADR-003: Chunking por headings (##) com fallback por parágrafos

**Decisão:** Documentos são quebrados em seções delimitadas por `##` headings. Se um chunk resultante tem > 4096 tokens, é subdividido. Se o documento não tem headings, chunk por parágrafos (linhas em branco).

**Justificativa:** Headings são a estrutura natural de documentos Markdown. Cada seção tende a ser autocontida (um conceito, uma skill, uma decisão). Isso produz chunks semanticamente coerentes, que é o que o retrieval precisa. O A-MapReduce não detalha chunking (opera sobre task matrix), mas o paper referencia "semantic neighborhoods" como unidade de retrieval.

**Alternativa rejeitada:** Sliding window de 512 tokens com overlap. Rejeitado porque (a) chunks artificiais misturam tópicos, (b) overlap gera redundância no índice, (c) a estrutura da wiki já é hierárquica — perdemos isso com janela deslizante.

### ADR-004: Scores por content_hash (SHA256) — sobrevivem a re-indexações

**Decisão:** Cada chunk tem um `content_hash = SHA256(content)`. Scores são atrelados ao hash, não ao row ID. Re-indexação recalcula hashes e re-associa scores existentes.

**Justificativa:** Permite re-indexar a wiki sem perder histórico de feedback. Se um documento não mudou, seu chunk mantém o score. Se mudou (hash diferente), score reseta (novo conteúdo = nova evidência necessária).

**Alternativa rejeitada:** Scores por `(source, heading)`. Rejeitado porque se o conteúdo da seção mudar, o score antigo não é mais válido — mas o identificador `(source, heading)` não captura isso.

### ADR-005: Distillation como operação explícita, não contínua

**Decisão:** `wiki-distill` é um comando explícito (usuário ou cron), não uma operação que roda automaticamente após cada feature.

**Justificativa:** Distillation envolve clusterização (KMeans/FINCH) + síntese via LLM — operação cara (tokens, tempo). Rodar a cada feature seria desperdício. Além disso, o usuário pode querer revisar os chunks canônicos gerados antes de commitá-los. O A-MapReduce roda Fψ periodicamente também, não a cada query.

**Alternativa rejeitada:** Distillation contínua (após cada N features, automático). Rejeitado porque (a) custo de LLM imprevisível no meio do pipeline, (b) chunks canônicos gerados sem revisão humana podem introduzir viés, (c) fere o princípio de "wiki como source of truth" se o sistema modifica o índice sem supervisão.

### ADR-006: Índice derivado, wiki como source of truth

**Decisão:** O índice SQLite é sempre reconstruível a partir da wiki. Nenhuma operação de índice modifica arquivos `.md` originais. Chunks canônicos (distillation) são armazenados como `source=_distilled/` — metadado que indica origem sintética, não arquivo real.

**Justificativa:** Preserva a wiki como fonte primária auditável. Se o índice corromper, `reindex()` resolve. Se a distillation gerar bobagem, os chunks `_distilled/` podem ser dropados sem afetar a wiki.

**Alternativa rejeitada:** Índice como source of truth (escrita bidirecional). Rejeitado porque (a) fere o ecossistema Obsidian (arquivos .md são a unidade atômica), (b) conflitos de merge entre índice e wiki seriam frequentes, (c) backups e versionamento (git) já funcionam para .md.

## Auditoria de Constituição

> **Nota:** O repositório `42_Framework` é um meta-framework e não possui `constitution.md` formal. Os portões abaixo são derivados do pipeline SDD.

| Regra | Status | Evidência |
|---|---|---|
| **Spec aprovado antes de implementar** | ✅ PASS | `spec.md` com `Aprovado: true` |
| **Vault wiki atualizado após feature** | ✅ PASS | Chunks canônicos gerados como `_distilled/` no índice; wiki existente é fonte, não destino |
| **Nunca inferir — ambiguidade = pergunta** | ✅ PASS | Edge cases #1-9 documentados |
| **Hermes nativo — sem dependências externas** | ✅ PASS | SQLite (built-in), sentence-transformers (pip), sem APIs externas |
| **Dependência documentada** | ✅ PASS | Feature 001 (LATTE) declarada como dependência no frontmatter |
| **4 fases canônicas** | ⚠️ N/A | Feature de infraestrutura (índice + retrieval), não feature de código tradicional |
