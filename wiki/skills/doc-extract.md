1|---
2|title: "doc-extract"
3|category: skills
4|tags: [doc, skill, extracao, markdown]
5|sources: [.hermes/skills/doc/extract/SKILL.md]
6|summary: "Extrai uma secao especifica de um arquivo markdown. Util para referenciar trechos de specs sem copiar o arquivo inteiro."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# doc-extract
13|
14|> Extrai secoes de documentos markdown. Cirurgico — so o trecho relevante.
15|
16|## Localizacao
17|`.hermes/skills/doc/extract/SKILL.md`
18|
19|## Quando usar
20|- Referenciar uma ADR especifica do plan.md
21|- Extrair cenarios BDD do spec.md
22|- Citar regra do constitution.md
23|
24|## Exemplo
25|```
26|doc-extract specs/features/006-agent-dev/spec.md "## Escopo"
27|→ retorna apenas a secao Escopo
28|```
29|
30|## Relacionado
31|- [[skills/doc-generate-toc]] — Gera indice do documento
32|- [[skills/doc-generate-llms-txt]] — Gera llms.txt
33|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar secoes ja extraidas, documentos similares, ou cross-referencias entre artefatos antes de agir.