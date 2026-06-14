---
title: "sdd-refactor-artifact"
category: skills
tags: [sdd, skill, refatoracao, artefatos]
sources: [.hermes/skills/sdd/refactor-artifact/SKILL.md]
summary: "Refatora artefatos SDD (spec.md, plan.md, tasks.md) para conformidade com templates canonicos. Normaliza headers, ajusta frontmatter."
lifecycle: draft
created: "2026-06-13"
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
- [[skills/sdd-brainstorm]] — Gera spec no formato correto
