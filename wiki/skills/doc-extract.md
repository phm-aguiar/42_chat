---
title: "doc-extract"
category: skills
tags: [doc, skill, extracao, markdown]
sources: [.hermes/skills/doc/extract/SKILL.md]
summary: "Extrai uma secao especifica de um arquivo markdown. Util para referenciar trechos de specs sem copiar o arquivo inteiro."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# doc-extract

> Extrai secoes de documentos markdown. Cirurgico — so o trecho relevante.

## Localizacao
`.hermes/skills/doc/extract/SKILL.md`

## Quando usar
- Referenciar uma ADR especifica do plan.md
- Extrair cenarios BDD do spec.md
- Citar regra do constitution.md

## Exemplo
```
doc-extract specs/features/006-agent-dev/spec.md "## Escopo"
→ retorna apenas a secao Escopo
```

## Relacionado
- [[skills/doc-generate-toc]] — Gera indice do documento
- [[skills/doc-generate-llms-txt]] — Gera llms.txt

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar secoes ja extraidas, documentos similares, ou cross-referencias entre artefatos antes de agir.