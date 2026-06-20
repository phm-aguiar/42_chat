---
title: "obsidian-markdown"
category: skills
tags: [obsidian, skill, markdown, formato, OFM]
sources: [.hermes/skills/obsidian/obsidian-markdown/SKILL.md]
summary: "Referência de sintaxe Obsidian Flavored Markdown (OFM): wikilinks, embeds, callouts, frontmatter, tags, footnotes. Usado por todas as skills que escrevem no vault."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-15"
---

# obsidian-markdown

> Sintaxe OFM (Obsidian Flavored Markdown). A "língua" do vault.

## Localização

`.hermes/skills/obsidian/obsidian-markdown/SKILL.md`

## Elementos principais

- **Wikilink:** `[[page]]` — linka para página no vault. Ex: `[[concepts/sdd]]`
- **Wikilink com alias:** `[[page|texto]]` — display text customizado. Ex: `[[concepts/sdd|SDD]]`
- **Embed:** `![[file]]` — embute nota/imagem/pdf. Ex: `![[diagrama.png]]`
- **Callout:** `> [!type]` — bloco destacado. Ex: `> [!warning] Cuidado`
- **Frontmatter:** YAML entre `---` no topo do arquivo. Ex: `tags: [sdd, wiki]`
- **Tag:** `#tag` no frontmatter. Ex: `#sdd`
- **Footnote:** `^[texto]` — nota de rodapé inline. Ex: `^[inferred]`

## Regras

- Wikilinks usam path relativo à raiz do vault
- Frontmatter YAML entre `---`
- Tags no frontmatter, não inline
- Aliases no frontmatter para sinônimos

## Relacionado

- [[skills/wiki-ingest|wiki-ingest]] — Usa OFM para escrever páginas
- [[skills/wiki-lint|wiki-lint]] — Valida wikilinks
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Onde a sintaxe é usada

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar padroes de sintaxe OFM usados no vault, exemplos de wikilinks, callouts e embeds antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.