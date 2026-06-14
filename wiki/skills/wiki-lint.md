---
title: "wiki-lint"
category: skills
tags: [wiki, skill, lint, auditoria, qualidade]
sources: [.hermes/skills/wiki/lint/SKILL.md]
summary: "Audita a saúde do vault Obsidian: broken links, páginas órfãs, frontmatter faltante, contradições, stale content. Com --consolidate, corrige automaticamente."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# wiki-lint

> Auditor de saúde do vault. Encontra problemas antes que virem débito técnico.

## Localização
`.hermes/skills/wiki/lint/SKILL.md`

## Quando usar
- Após múltiplos ingests (mover/renomear páginas quebra links)
- Antes de commit (gate de qualidade)
- Periodicamente (cron job semanal)

## Checks (13 no total)
| Check | O que detecta |
|---|---|
| Broken wikilinks | `[[page]]` que não existe |
| Orphaned pages | Páginas sem incoming links |
| Missing frontmatter | Campos obrigatórios faltando |
| Stale content | Páginas desatualizadas vs sources |
| Contradictions | Claims conflitantes |
| Index consistency | `index.md` vs disco |
| Fragmented tags | Clusters de tags sem cross-links |

## Modo --consolidate
Além de reportar, **corrige** automaticamente:
- Conserta broken links (fuzzy match)
- Adiciona cross-references pra órfãos
- Promove drafts antigos → reviewed
- Normaliza aliases de tags

## Exemplo real
Na feature 006, o `wiki-lint` encontrou 18 broken links (renomeações de
`runtime-orchestrator` → `agent-orchestrator`). Todos corrigidos em 1 commit.

## Relacionado
- [[wiki-ingest]] — Cria páginas que o lint audita
- [[skills/wiki-cross-linker]] — Complementar: adiciona links, lint verifica
- [[obsidian-flow|Fluxo Obsidian]] — Quando rodar
