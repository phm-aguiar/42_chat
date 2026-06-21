---
feature_id: "003"
plan_for: "Wiki Hybrid Retrieval & Normalization"
spec: "specs/features/003-hybrid-retrieval/spec.md"
created: "2026-06-20"
author: phm-aguiar
stack: "Hermes Agent (Python), rank_bm25, SQLite, sentence-transformers"
depends_on: "002-experiential-memory"
---

# Plano Arquitetural — Wiki Hybrid Retrieval & Normalization

## Metadados

| Campo | Valor |
|---|---|
| **Stack** | Hermes Agent (Python), `rank_bm25`, SQLite, `sentence-transformers` |
| **Feature fonte** | `specs/features/003-hybrid-retrieval/spec.md` |
| **Escopo (1 frase)** | Pesquisa híbrida BM25+cosine, normalização de frontmatter em 34 docs, thresholds adaptativos configuráveis |
| **Dependência** | Feature 002 (Wiki Experiential Memory) — estende `search.py` e o índice SQLite |

## Contratos e Fronteiras

### Entrada

| Artefato | Formato | Fonte |
|---|---|---|
| Índice SQLite | 2019 chunks com embeddings | Feature 002 (`~/.hermes/wiki_index.db`) |
| Query text | String natural language ou termo exato | `search_similar()` |
| Parâmetros | `hybrid: bool`, `threshold: float`, `alpha: float` | Chamador |
| Docs sem frontmatter | 34 arquivos .md | `wiki/` |

### Saída

| Artefato | Formato | Destino |
|---|---|---|
| Resultados híbridos | `list[dict]` com `similarity`, `bm25_score`, `hybrid_score` | `search_similar()` return |
| Docs normalizados | .md com YAML frontmatter adicionado | `wiki/` (in-place) |
| Relatório de normalização | stdout: "34 docs normalizados, 0 erros" | Terminal |

### Operadores (API estendida)

```
search_similar(query, model, k=5, hybrid=False, threshold=None, alpha=0.7)
  → hybrid=False: comportamento idêntico ao atual (cosine-only)
  → hybrid=True: BM25 + cosine fusion com peso alpha
  → threshold: filtra resultados abaixo do threshold
  → alpha: 0.0 = só BM25, 1.0 = só cosine, 0.7 = default balanceado

normalize_frontmatter(wiki_root='wiki/', dry_run=False)
  → Adiciona title+tags+created aos docs sem frontmatter
  → dry_run=True: só reporta, não modifica
```

## ADRs

### ADR-001: rank_bm25 em vez de SQLite FTS5

**Decisão:** Usar `rank_bm25` (Python puro, pip install rank-bm25) para scoring lexical.

**Justificativa:** Implementação canônica do BM25 (Robertson & Zaragoza 2009), sem dependência de C extensions, O(n) por query com n=2000. SQLite FTS5 exigiria criar tabela FTS separada e popular, e seu ranking interno não é BM25 puro (usa variante própria). Para 2000 documentos, rank_bm25 processa em < 50ms.

**Alternativa rejeitada:** SQLite FTS5 com `bm25()` function. Rejeitado porque (a) FTS5 ranking não é BM25 canônico, (b) exige tabela separada e sincronização com tabela `chunks`, (c) overkill pra escala atual.

### ADR-002: α = 0.7 como peso padrão da fusão

**Decisão:** `hybrid_score = 0.7 * cosine_norm + 0.3 * bm25_norm`. Prioriza semântico mas dá peso significativo ao lexical.

**Justificativa:** O relatório recomenda "aliar busca lexical com mapeamento vetorial". α=0.7 favorece o cosine (que já funciona bem para consultas conceituais em pt-BR) enquanto α=0.3 de BM25 resolve o gap de termos exatos. O parâmetro é exposto para ajuste fino.

**Alternativa rejeitada:** α=0.5 (pesos iguais). Rejeitado porque (a) cosine já é validado com 312ms e boa qualidade, (b) BM25 puro degrada em consultas conceituais multilíngues, (c) o relatório recomenda "delegar triagem ao LLM" — o cosine fornece contexto semântico que o BM25 não captura.

### ADR-003: Normalização só nos 34 docs sem frontmatter

**Decisão:** O script `normalize_frontmatter` só processa docs que não começam com `---`. Docs com YAML existente são ignorados.

**Justificativa:** Minimiza risco de corrupção. Os 207 docs com frontmatter já têm estrutura estabelecida — modificar poderia quebrar wikilinks, aliases, ou metadados existentes. A normalização é um passo de "leveling up" do mínimo, não uma reestruturação.

**Alternativa rejeitada:** Normalização completa (auditar + corrigir todos os 238 docs). Rejeitado porque (a) risco de regressão em docs estáveis, (b) frontmatter existente pode ter campos personalizados que o script não conhece, (c) 87% de cobertura já é aceitável.

### ADR-004: Thresholds como parâmetro, não como config global

**Decisão:** `search_similar(threshold=0.50)` aceita threshold por chamada. Sem threshold = sem filtro (comportamento atual).

**Justificativa:** Diferentes contextos de uso exigem thresholds diferentes: consultas interativas (0.50), cross-links automáticos (0.70), debugging (None = sem filtro). Um config global não capturaria essa granularidade. O default None preserva compatibilidade.

**Alternativa rejeitada:** Threshold no config.yaml ou variável de ambiente. Rejeitado porque (a) o threshold certo depende do contexto de uso, não do ambiente, (b) exigiria reload de config para ajuste, (c) o relatório recomenda thresholds diferentes para modos diferentes.

## Auditoria de Constituição

| Regra | Status | Evidência |
|---|---|---|
| **Spec aprovado antes de implementar** | ✅ PASS | `spec.md` com `Aprovado: true` |
| **Vault wiki atualizado após feature** | ✅ PLAN | Docs normalizados in-place; índice atualizado com novo search |
| **Nunca inferir — ambiguidade = pergunta** | ✅ PASS | Edge cases #1-8 documentados |
| **Hermes nativo — sem dependências externas** | ✅ PASS | rank_bm25 (pip), sem APIs externas |
| **Dependência documentada** | ✅ PASS | Feature 002 declarada como dependência |
| **Compatibilidade reversa** | ✅ PASS | search_similar() sem params novos = comportamento idêntico |
