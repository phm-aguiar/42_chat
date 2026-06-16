1|---
2|title: "doc-generate-toc"
3|category: skills
4|tags: [doc, skill, toc, indice]
5|sources: [.hermes/skills/doc/generate-toc/SKILL.md]
6|summary: "Gera tabela de conteudo (TOC) para documentos markdown. Extrai headers e monta indice navegavel com links internos."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# doc-generate-toc
13|
14|> Gera indice navegavel para documentos markdown.
15|
16|## Localizacao
17|`.hermes/skills/doc/generate-toc/SKILL.md`
18|
19|## Quando usar
20|- Documentos longos (spec.md, plan.md)
21|- README.md
22|- Wiki pages extensas
23|
24|## Exemplo
25|```markdown
26|## TOC
27|- [Proposito](#proposito)
28|- [Escopo](#escopo)
29|  - [Dentro](#dentro-do-escopo)
30|  - [Fora](#fora-do-escopo)
31|```
32|
33|## Relacionado
34|- [[skills/doc-extract]] — Extrai secoes referenciadas no TOC
35|- [[skills/doc-generate-llms-txt]] — Indice global do repo
36|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar tabelas de conteudo geradas, documentos longos que precisam de indice, ou padroes de heading antes de agir.