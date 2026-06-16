1|---
2|title: "defuddle"
3|category: skills
4|tags: [obsidian, skill, extracao, markdown]
5|sources: [.hermes/skills/obsidian/defuddle/SKILL.md]
6|summary: "Extrai conteúdo limpo em markdown de páginas web, removendo ruído (ads, nav, sidebars). Usado como pré-processamento antes do wiki-ingest."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# defuddle
13|
14|> Extrai markdown limpo de páginas web. "Tira o lixo, deixa o conteúdo."
15|
16|## Localização
17|`.hermes/skills/obsidian/defuddle/SKILL.md`
18|
19|## Quando usar
20|- Antes de `wiki-ingest` de uma URL
21|- Extrair documentação de sites para referência
22|- Limpar páginas web pra ingest no vault
23|
24|## Exemplo
25|```
26|URL: https://docs.exemplo.com/api
27|→ defuddle
28|→ Markdown limpo (sem header, nav, footer, ads)
29|→ wiki-ingest → página no vault
30|```
31|
32|## Relacionado
33|- [[skills/wiki-ingest|wiki-ingest]] — Consumidor do output do defuddle
34|- [[skills/obsidian-markdown|obsidian-markdown]] — Formato de saída
35|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas que referenciam URLs similares, verificar se uma pagina web ja foi ingerida, ou consultar decisoes sobre extract vs browser antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.