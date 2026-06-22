---
feature_id: "004"
plan_for: "Wiki Standardization"
spec: "specs/features/004-wiki-standardization/spec.md"
created: "2026-06-21"
author: phm-aguiar
---

# Plan — Wiki Standardization

## Metadados

- **Stack:** Python (scripts de validação/chunking), YAML (frontmatter), Markdown (wiki)
- **Feature fonte:** `specs/features/004-wiki-standardization/spec.md`
- **Escopo:** Template canônico + correção 20 problemáticos + skill validação + chunking inteligente

## Contratos e Fronteiras

### Entrada

- `wiki/` — 374 páginas Markdown com frontmatter YAML inconsistente
- `wiki-lint` — skill existente de auditoria de vault (wikilinks, estrutura)
- Feature 002 (`cli_index.py`, `cli_query.py`) — índice SQLite + embeddings
- Feature 003 (`bm25.py`, `search.py` com hybrid mode) — busca híbrida

### Saída

- `wiki/_meta/template.md` — template canônico de frontmatter
- `.hermes/skills/wiki/wiki-lint/` — estendido com `validate_template.py`
- `wiki/tools/golangci-lint/linters/*.md` — split de `Linters.md`
- 20 arquivos corrigidos (YAML escaping + title)
- Índice reindexado via Feature 002

### Interfaces

- `wiki-validate-template` é invocada como submódulo do `wiki-lint`
- `chunk_split.py` lê arquivo grande, produz N sub-páginas + `_index.md`
- Thresholds de chunking configuráveis via `wiki/_meta/chunking.yaml`

## ADRs

### ADR-001: Template com 3 tiers de campos (obrigatório / diretório / opcional)

**Decisão:** Template canônico define 3 níveis:
- **Obrigatórios (todas as páginas):** `title`, `tags`, `created`
- **Por diretório:** `category` (concepts/, references/), `summary` (references/, skills/), `lifecycle` (references/), `updated` (todas exceto _raw/)
- **Opcionais:** `aliases`, `status`, `sources`, `provenance`, `base_confidence`, `tier`, `superseded_by`

**Justificativa:** Campos como `lifecycle` e `provenance` fazem sentido para references/
(material ingerido de fontes externas) mas não para journal/ (notas cronológicas).
Forçar campos irrelevantes gera ruído. Tier 2 (por diretório) equilibra padronização
com contexto.

**Alternativa rejeitada:** Template único com 15 campos obrigatórios para todas as
páginas. Rejeitada porque páginas de journal e _staging ficariam poluídas com campos
sem significado.

### ADR-002: Correção com script idempotente, não edição manual

**Decisão:** Script `fix_frontmatter.py` que:
1. Detecta YAML quebrado por `:` não escapado em campos string (regex)
2. Envolve o valor em aspas duplas preservando o conteúdo
3. Para páginas sem `title`, deriva do H1 (`# Título`) ou do nome do arquivo
4. Dry-run mode (`--dry-run`) para preview antes de aplicar

**Justificativa:** 20 arquivos com 2 padrões de erro (YAML escaping + title ausente).
Automação é mais segura que edição manual (sem risco de typos) e repetível (se novos
arquivos com o mesmo padrão forem ingeridos no futuro).

**Alternativa rejeitada:** Editar manualmente cada arquivo. Rejeitada por escala
(20 arquivos, propenso a erro humano) e falta de reprodutibilidade.

### ADR-003: Chunking estrutural (por seção), não por tokens

**Decisão:** Arquivos >500 linhas ou >25KB são splitados por headings de nível 2
(`##`). Cada sub-página herda o frontmatter do original + `part_of` link. Um
`_index.md` lista as sub-páginas com descrições de 1 linha.

**Justificativa:** Chunking por tokens (Feature 002) já funciona para busca semântica.
Mas chunks de 500 tokens de um documento de 4000 linhas perdem a estrutura hierárquica
— o embedding de um parágrafo sobre `bodyclose` não carrega o contexto de que está
dentro de "GolangCI-Lint Linters Reference". Chunking estrutural preserva a hierarquia
e permite que a busca híbrida (Feature 003) faça BM25 no título da sub-página + cosine
no conteúdo.

**Alternativa rejeitada:** Aumentar o tamanho do chunk na Feature 002 (ex: 2000 tokens).
Rejeitada porque prejudica a precisão da busca semântica (chunks maiores diluem o sinal).

### ADR-004: Validação como extensão do wiki-lint, não skill separada

**Decisão:** `wiki-validate-template` é um submódulo do `wiki-lint` existente,
invocado com `--validate-template`. O `wiki-lint` ganha um modo `--strict` que
inclui validação de template + chunking candidates.

**Justificativa:** O `wiki-lint` já é o ponto de entrada de auditoria do vault.
Criar uma skill separada fragmenta o fluxo de validação. Extensão mantém
consistência com o portão #4 da constituição ("vault fiel").

**Alternativa rejeitada:** Skill standalone `wiki-validate-template`. Rejeitada
porque o gatilho natural é o mesmo do `wiki-lint` (pré-commit, auditoria periódica)
e o usuário teria que lembrar de rodar duas skills.

## Auditoria de Constituição

| Portão | Status | Evidência |
|--------|--------|-----------|
| #1 Validação SDD | ✅ | spec.md + plan.md + tasks.md presentes |
| #2 Aprovação humana | ✅ | `Aprovado: true` no spec.md |
| #3 Smoke test | ✅ | `fix_frontmatter.py --dry-run` + `wiki-lint --validate-template` como smoke tests |
| #4 Vault fiel | ✅ | Feature atualiza o próprio vault — template.md + reindex |
| Anti-padrão #6 (vault desatualizado) | ✅ | Correção + reindex mantém vault consistente |
