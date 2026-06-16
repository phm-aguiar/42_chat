1|---
2|title: "json-canvas"
3|category: skills
4|tags: [obsidian, skill, canvas, visual]
5|sources: [.hermes/skills/obsidian/json-canvas/SKILL.md]
6|summary: "Cria e edita JSON Canvas (.canvas files) — mapas visuais com nós, arestas e conexões. Formato nativo do Obsidian para pensamento visual."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# json-canvas
13|
14|> Cria e edita Canvas files — mapas visuais de conhecimento no Obsidian.
15|
16|## Localização
17|`.hermes/skills/obsidian/json-canvas/SKILL.md`
18|
19|## Quando usar
20|- Mapear relações entre conceitos visualmente
21|- Criar diagramas de arquitetura no próprio Obsidian
22|- Brainstorm visual de features
23|
24|## Formato
25|Arquivos `.canvas` são JSON com nós (nodes) e arestas (edges):
26|```json
27|{
28|  "nodes": [
29|    {"id": "1", "type": "file", "file": "concepts/sdd.md"}
30|  ],
31|  "edges": [
32|    {"id": "e1", "fromNode": "1", "toNode": "2"}
33|  ]
34|}
35|```
36|
37|## Relacionado
38|- [[skills/obsidian-bases|obsidian-bases]] — Tabelas (outro formato visual)
39|- [[skills/mermaid-visualizer|mermaid-visualizer]] — Diagramas Mermaid
40|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar canvas files existentes no vault, padroes de layout, ou integracoes com outras paginas visuais antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.