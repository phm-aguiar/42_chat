---
title: "sdd-refactor-artifact"
category: skills
tags: [sdd, skill, refatoracao, artefatos]
sources: [.hermes/skills/sdd/refactor-artifact/SKILL.md]
summary: "Refatora artefatos SDD (spec.md, plan.md, tasks.md) para conformidade com templates canonicos. Normaliza headers, ajusta frontmatter."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
---

# sdd-refactor-artifact

> Normaliza artefatos SDD para o formato canonico.

## Localizacao
`.hermes/skills/sdd/refactor-artifact/SKILL.md`

## Quando usar
- Spec importada de outro formato
- Artefato com headers fora do padrao
- Migracao de formato antigo para novo

## O que faz
- Normaliza headers (## Proposito, ## Escopo, etc.)
- Ajusta frontmatter (Aprovado, Autor, Data)
- Preserva conteudo — so ajusta estrutura

## Relacionado
- [[skills/sdd-validate]] — Valida apos refatoracao
- [[projects/42_chat/skills/sdd-brainstorm]] — Gera spec no formato correto

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar artefatos que precisam de normalizacao, templates canonicos, ou inconsistencias conhecidas antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.