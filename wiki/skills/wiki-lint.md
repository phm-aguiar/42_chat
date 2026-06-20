---
title: "wiki-lint"
category: skills
tags: [wiki, skill, lint, auditoria, qualidade]
sources: [.hermes/skills/wiki/lint/SKILL.md]
summary: "Audita a saúde do vault Obsidian: broken links, páginas órfãs, frontmatter faltante, contradições, stale content. Com --consolidate, corrige automaticamente."
lifecycle: draft
created: "2026-06-13"
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-15"
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

- **Broken wikilinks:** wikilink apontando pra página que não existe
- **Orphaned pages:** páginas sem incoming links
- **Missing frontmatter:** campos obrigatórios faltando
- **Stale content:** páginas desatualizadas vs sources
- **Contradictions:** claims conflitantes entre páginas
- **Index consistency:** `index.md` vs disco
- **Fragmented tags:** clusters de tags sem cross-links

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

- [[skills/wiki-cross-linker|cross-linker]] — Adiciona wikilinks faltantes
- [[skills/wiki-dedup|wiki-dedup]] — Resolve páginas duplicadas
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica (checks de lint, page thresholds, pitfalls)
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Pipeline de manutenção do vault

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas com problemas recorrentes, padroes de broken links, ou auditorias anteriores antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.