---
title: "wiki-ingest"
category: skills
tags: [wiki, skill, ingest, destilacao]
sources: [.hermes/skills/wiki/ingest/SKILL.md]
summary: Destila raw sources (specs, docs, logs) em páginas wiki interligadas. É o entry point do pipeline wiki — transforma artefatos do framework em conhecimento navegável.
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# wiki-ingest

> Destila raw sources em páginas wiki. Entry point do pipeline de knowledge management.

## Localização
`.hermes/skills/wiki/ingest/SKILL.md`

## Quando usar
- Após feature implementada (destilar spec/plan/tasks em página wiki)
- Após nova decisão arquitetural (atualizar concepts/)
- Após importar documentos externos

## O que faz
1. Lê a source (spec.md, plan.md, conversa, URL)
2. Extrai conceitos, decisões, relações
3. Cria/atualiza página wiki com frontmatter completo
4. Adiciona `[[wikilinks]]` para páginas relacionadas
5. Registra no `.manifest.json`
6. Atualiza `index.md` e `log.md`

## Exemplo
```
Source: specs/features/006-agent-dev/spec.md
Output: wiki/projects/42_chat/features/feature-006-agent-dev.md
```

## Relacionado
- [[wiki-lint]] — Audita o que foi ingerido
- [[wiki-query]] — Busca o que foi ingerido
- [[obsidian-flow|Fluxo Obsidian]] — Onde se encaixa
