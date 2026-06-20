---
title: "wiki-dedup"
category: skills
tags: [wiki, skill, deduplicacao, limpeza]
sources: [.hermes/skills/wiki/dedup/SKILL.md]
summary: "Detecta paginas duplicadas ou com sobreposicao significativa no vault. Sugere merge ou arquivamento."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# wiki-dedup

> Encontra e resolve duplicatas no vault.

## Localizacao
`.hermes/skills/wiki/dedup/SKILL.md`

## Quando usar
- Vault cresceu e tem sobreposicao
- Multiplos ingests da mesma fonte
- Antes de `wiki-lint --consolidate`

## Relacionado
- [[skills/wiki-lint]] — Lint detecta contradicoes, dedup detecta duplicatas
- [[skills/wiki-cross-linker]] — Apos merge, cross-linker reconecta

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas candidatas a merge, verificar similaridade entre conceitos, ou identificar duplicatas antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.