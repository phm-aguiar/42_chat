---
title: "Wiki Frontmatter Template"
category: meta
tags: [wiki, template, frontmatter, standard]
created: "2026-06-21"
rag_score: 0.5
summary: "Template canônico de frontmatter para todas as páginas do vault. Define 3 tiers de campos: obrigatórios (todas), por diretório, e opcionais."
---

# Wiki Frontmatter Template

> Todo arquivo `.md` no vault `wiki/` deve começar com frontmatter YAML entre `---`.
> Campos marcados **OBRIGATÓRIO** quebram `wiki-lint --validate-template` se ausentes.
> Campos **POR DIRETÓRIO** são obrigatórios apenas nos diretórios listados.

## Tier 1: Obrigatórios (todas as páginas)

```yaml
---
title: "Título da Página"
tags: [tag1, tag2, tag3]
created: "YYYY-MM-DD"
---
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `title` | string | Título da página. Use aspas duplas se contiver `:`. |
| `tags` | list | Lista YAML de tags. Mínimo 1 item. Use `[]` se nenhuma tag se aplicar. |
| `created` | string | Data ISO 8601 (`YYYY-MM-DD`). Data de criação da página no vault. |

## Tier 2: Por Diretório

### concepts/

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `category` | string | Sempre `"concepts"` |

Exemplo:
```yaml
---
title: "Spec-Driven Development (SDD)"
category: concepts
tags: [sdd, metodologia, pipeline]
created: "2026-06-13"
---
```

### references/

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `category` | string | Subcategoria: `"go"`, `"testing"`, `"devops"`, `"reference"`, `"tutorial"`, etc. |
| `summary` | string | 1-2 frases descrevendo o conteúdo. Use aspas duplas se contiver `:`. |
| `updated` | string | Data ISO 8601 da última atualização de conteúdo. |
| `lifecycle` | string | `"raw"` \| `"reviewed"` \| `"canonical"` \| `"archived"`. Default: `"reviewed"`. |

Exemplo:
```yaml
---
title: "Go Code Review Rules"
category: go
tags: [go, style-guide, coding-standards]
created: "2026-06-15"
updated: "2026-06-20"
summary: "Regras de code review para Go: naming, error handling, concorrência, interfaces."
lifecycle: reviewed
---
```

### skills/

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `category` | string | Sempre `"skill"` |
| `summary` | string | 1-2 frases descrevendo o que a skill faz. |

Exemplo:
```yaml
---
title: "wiki-lint"
category: skill
tags: [wiki, skill, validacao, auditoria]
created: "2026-06-14"
summary: "Audita integridade do vault: wikilinks quebrados, estrutura de diretórios, frontmatter inválido."
---
```

### journal/

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `category` | string | Sempre `"journal"` |

Exemplo:
```yaml
---
title: "Digest 2026-06-21"
category: journal
tags: [digest, weekly]
created: "2026-06-21"
---
```

### entities/ e synthesis/

Sem campos adicionais obrigatórios além do Tier 1. `category` opcional.
Use `category: entity` para entities/ e `category: synthesis` para synthesis/.

### _meta/

Sem campos adicionais obrigatórios. `category: meta` recomendado.

## Tier 3: Opcionais (qualquer página)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `aliases` | list | Nomes alternativos para wikilinks. Ex: `["SDD", "Spec-Driven"]` |
| `status` | string | `"draft"` \| `"accepted"` \| `"deprecated"` \| `"superseded"` (ADRs) |
| `sources` | list | URLs ou paths de onde o conteúdo foi ingerido. |
| `provenance` | string | Origem do documento: `"ingested"`, `"generated"`, `"manual"`. |
| `base_confidence` | float | 0.0–1.0. Confiança na veracidade (para conteúdo ingerido). |
| `tier` | int | 1–5. Relevância do documento para o framework. |
| `superseded_by` | string | Path da página que substitui esta. |
| `lifecycle_changed` | string | Data ISO da última mudança de lifecycle. |
| `lifecycle_reason` | string | Justificativa da mudança de lifecycle. |
| `author` | string | Autor original (para conteúdo ingerido). |
| `published` | string | Data de publicação original (para conteúdo ingerido). |
| `description` | string | Descrição curta alternativa ao summary. |

## Regras de Formatação

1. **Aspas em strings com `:`:** Sempre envolva em aspas duplas valores que contenham
   dois-pontos. Ex: `summary: "Guia de migração Vite 7 → 8: Rolldown substitui esbuild"`
   — sem aspas, o YAML interpreta `8: Rolldown` como nested mapping.

2. **Tags como lista YAML:** Use `[tag1, tag2]` (flow style) ou:
   ```yaml
   tags:
     - tag1
     - tag2
   ```

3. **Datas ISO 8601:** Sempre `YYYY-MM-DD`. Opcionalmente `YYYY-MM-DDThh:mm:ss`.

4. **Ordem canônica dos campos:**
   ```yaml
   title
   category
   tags
   created
   updated
   summary
   lifecycle
   status
   sources
   provenance
   base_confidence
   tier
   aliases
   superseded_by
   lifecycle_changed
   lifecycle_reason
   author
   published
   description
   ```
