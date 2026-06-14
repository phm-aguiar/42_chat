---
title: "defuddle"
category: skills
tags: [obsidian, skill, extracao, markdown]
sources: [.hermes/skills/obsidian/defuddle/SKILL.md]
summary: Extrai conteúdo limpo em markdown de páginas web, removendo ruído (ads, nav, sidebars). Usado como pré-processamento antes do wiki-ingest.
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# defuddle

> Extrai markdown limpo de páginas web. "Tira o lixo, deixa o conteúdo."

## Localização
`.hermes/skills/obsidian/defuddle/SKILL.md`

## Quando usar
- Antes de `wiki-ingest` de uma URL
- Extrair documentação de sites para referência
- Limpar páginas web pra ingest no vault

## Exemplo
```
URL: https://docs.exemplo.com/api
→ defuddle
→ Markdown limpo (sem header, nav, footer, ads)
→ wiki-ingest → página no vault
```

## Relacionado
- [[skills/wiki-ingest|wiki-ingest]] — Consumidor do output do defuddle
- [[skills/obsidian-markdown|obsidian-markdown]] — Formato de saída
