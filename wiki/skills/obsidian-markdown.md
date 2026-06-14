---
title: "obsidian-markdown"
category: skills
tags: [obsidian, skill, markdown, formato, OFM]
sources: [.hermes/skills/obsidian/obsidian-markdown/SKILL.md]
summary: "Referência de sintaxe Obsidian Flavored Markdown (OFM): wikilinks, embeds, callouts, frontmatter, tags, footnotes. Usado por todas as skills que escrevem no vault."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# obsidian-markdown

> Sintaxe OFM (Obsidian Flavored Markdown). A "língua" do vault.

## Localização
`.hermes/skills/obsidian/obsidian-markdown/SKILL.md`

## Elementos principais

| Elemento | Sintaxe | Exemplo |
|---|---|---|
| Wikilink | `[[page]]` | `[[concepts/sdd]]` |
| Wikilink com alias | `[[page\|texto]]` | `[[concepts/sdd\|SDD]]` |
| Embed | `![[file]]` | `![[diagrama.png]]` |
| Callout | `> [!type]` | `> [!warning] Cuidado` |
| Frontmatter | `---\nkey: value\n---` | `tags: [sdd, wiki]` |
| Tag | `#tag` | `#sdd` |
| Footnote | `^[texto]` | `^[inferred]` |

## Regras
- Wikilinks usam path relativo à raiz do vault
- Frontmatter YAML entre `---`
- Tags no frontmatter, não inline
- Aliases no frontmatter para sinônimos

## Relacionado
- [[wiki-ingest]] — Usa OFM para escrever páginas
- [[wiki-lint]] — Valida wikilinks
- [[obsidian-flow|Fluxo Obsidian]] — Onde a sintaxe é usada
