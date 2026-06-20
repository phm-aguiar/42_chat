---
title: "json-canvas"
category: skills
tags: [obsidian, skill, canvas, visual]
sources: [.hermes/skills/obsidian/json-canvas/SKILL.md]
summary: "Cria e edita JSON Canvas (.canvas files) — mapas visuais com nós, arestas e conexões. Formato nativo do Obsidian para pensamento visual."
lifecycle: draft
created: "2026-06-13"
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# json-canvas

> Cria e edita Canvas files — mapas visuais de conhecimento no Obsidian.

## Localização
`.hermes/skills/obsidian/json-canvas/SKILL.md`

## Quando usar
- Mapear relações entre conceitos visualmente
- Criar diagramas de arquitetura no próprio Obsidian
- Brainstorm visual de features

## Formato
Arquivos `.canvas` são JSON com nós (nodes) e arestas (edges):
```json
{
  "nodes": [
    {"id": "1", "type": "file", "file": "concepts/sdd.md"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "1", "toNode": "2"}
  ]
}
```

## Relacionado
- [[skills/obsidian-bases|obsidian-bases]] — Tabelas (outro formato visual)
- [[skills/mermaid-visualizer|mermaid-visualizer]] — Diagramas Mermaid

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar canvas files existentes no vault, padroes de layout, ou integracoes com outras paginas visuais antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.