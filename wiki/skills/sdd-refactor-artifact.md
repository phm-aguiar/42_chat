1|---
2|title: "sdd-refactor-artifact"
3|category: skills
4|tags: [sdd, skill, refatoracao, artefatos]
5|sources: [.hermes/skills/sdd/refactor-artifact/SKILL.md]
6|summary: "Refatora artefatos SDD (spec.md, plan.md, tasks.md) para conformidade com templates canonicos. Normaliza headers, ajusta frontmatter."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-refactor-artifact
13|
14|> Normaliza artefatos SDD para o formato canonico.
15|
16|## Localizacao
17|`.hermes/skills/sdd/refactor-artifact/SKILL.md`
18|
19|## Quando usar
20|- Spec importada de outro formato
21|- Artefato com headers fora do padrao
22|- Migracao de formato antigo para novo
23|
24|## O que faz
25|- Normaliza headers (## Proposito, ## Escopo, etc.)
26|- Ajusta frontmatter (Aprovado, Autor, Data)
27|- Preserva conteudo — so ajusta estrutura
28|
29|## Relacionado
30|- [[skills/sdd-validate]] — Valida apos refatoracao
31|- [[projects/42_chat/skills/sdd-brainstorm]] — Gera spec no formato correto
32|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar artefatos que precisam de normalizacao, templates canonicos, ou inconsistencias conhecidas antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.