---
title: "wiki-query"
category: skills
tags: [wiki, skill, busca, query, retrieval]
sources: [.hermes/skills/wiki/query/SKILL.md]
summary: "Busca híbrida (lexical + vetorial) no vault Obsidian. Modo index-only (barato, lê só frontmatter) ou full-read (profundo, lê corpos). Usado pelo agente principal para recuperar conhecimento compilado."
lifecycle: draft
tier: core
created: "2026-06-13"
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# wiki-query

> Busca conhecimento compilado no vault. "O que já decidimos sobre X?"

## Localização
`.hermes/skills/wiki/query/SKILL.md`

## Quando usar
- Antes de brainstorm (features similares já existem?)
- Durante implementação (decisões arquiteturais passadas?)
- Debugging (edge case já documentado?)

## Modos
| Modo | Custo | Quando |
|---|---|---|
| **Index-only** | Baixo | Lê só `summary:` do frontmatter — suficiente pra 80% das perguntas |
| **Full-read** | Alto | Lê corpos das páginas — para perguntas complexas |

## Como funciona
1. Busca lexical (grep) nos frontmatters
2. Busca vetorial (embeddings) se configurado
3. Combina resultados com ranking
4. Sintetiza resposta ou retorna páginas relevantes

## Exemplo
```
Query: "Como o agent-dev lida com spec ambígua?"
→ wiki-query index-only
→ Encontra: feature-006-agent-dev.md (summary: "nunca infere, reporta BLOCKED")
→ Retorna: página + trecho relevante
```

## Relacionado
- [[skills/wiki-ingest|wiki-ingest]] — Alimenta o que a query busca
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica (query operation, compile-dont-retrieve)
- [[concepts/wiki-model|Wiki Model]] — Compile, don't retrieve
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Quando usar
