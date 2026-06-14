---
title: "doc-generate-toc"
category: skills
tags: [doc, skill, toc, indice]
sources: [.hermes/skills/doc/generate-toc/SKILL.md]
summary: "Gera tabela de conteudo (TOC) para documentos markdown. Extrai headers e monta indice navegavel com links internos."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# doc-generate-toc

> Gera indice navegavel para documentos markdown.

## Localizacao
`.hermes/skills/doc/generate-toc/SKILL.md`

## Quando usar
- Documentos longos (spec.md, plan.md)
- README.md
- Wiki pages extensas

## Exemplo
```markdown
## TOC
- [Proposito](#proposito)
- [Escopo](#escopo)
  - [Dentro](#dentro-do-escopo)
  - [Fora](#fora-do-escopo)
```

## Relacionado
- [[skills/doc-extract]] — Extrai secoes referenciadas no TOC
- [[skills/doc-generate-llms-txt]] — Indice global do repo
