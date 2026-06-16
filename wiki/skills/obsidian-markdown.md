1|---
2|title: "obsidian-markdown"
3|category: skills
4|tags: [obsidian, skill, markdown, formato, OFM]
5|sources: [.hermes/skills/obsidian/obsidian-markdown/SKILL.md]
6|summary: "Referência de sintaxe Obsidian Flavored Markdown (OFM): wikilinks, embeds, callouts, frontmatter, tags, footnotes. Usado por todas as skills que escrevem no vault."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-15"
10|---
11|
12|# obsidian-markdown
13|
14|> Sintaxe OFM (Obsidian Flavored Markdown). A "língua" do vault.
15|
16|## Localização
17|
18|`.hermes/skills/obsidian/obsidian-markdown/SKILL.md`
19|
20|## Elementos principais
21|
22|- **Wikilink:** `[[page]]` — linka para página no vault. Ex: `[[concepts/sdd]]`
23|- **Wikilink com alias:** `[[page|texto]]` — display text customizado. Ex: `[[concepts/sdd|SDD]]`
24|- **Embed:** `![[file]]` — embute nota/imagem/pdf. Ex: `![[diagrama.png]]`
25|- **Callout:** `> [!type]` — bloco destacado. Ex: `> [!warning] Cuidado`
26|- **Frontmatter:** YAML entre `---` no topo do arquivo. Ex: `tags: [sdd, wiki]`
27|- **Tag:** `#tag` no frontmatter. Ex: `#sdd`
28|- **Footnote:** `^[texto]` — nota de rodapé inline. Ex: `^[inferred]`
29|
30|## Regras
31|
32|- Wikilinks usam path relativo à raiz do vault
33|- Frontmatter YAML entre `---`
34|- Tags no frontmatter, não inline
35|- Aliases no frontmatter para sinônimos
36|
37|## Relacionado
38|
39|- [[skills/wiki-ingest|wiki-ingest]] — Usa OFM para escrever páginas
40|- [[skills/wiki-lint|wiki-lint]] — Valida wikilinks
41|- [[concepts/obsidian-flow|Fluxo Obsidian]] — Onde a sintaxe é usada
42|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar padroes de sintaxe OFM usados no vault, exemplos de wikilinks, callouts e embeds antes de agir. O vault contem exemplos reais e decisoes documentadas que evitam retrabalho.