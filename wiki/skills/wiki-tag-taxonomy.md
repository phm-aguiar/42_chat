1|---
2|title: "wiki-tag-taxonomy"
3|category: skills
4|tags: [wiki, skill, tags, taxonomia, vocabulario]
5|sources: [.hermes/skills/wiki/tag-taxonomy/SKILL.md]
6|summary: "Gerencia taxonomia de tags do vault: normaliza aliases, detecta tags sem pagina, sugere consolidacao."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# wiki-tag-taxonomy
13|
14|> Mantem a taxonomia de tags consistente.
15|
16|## Localizacao
17|`.hermes/skills/wiki/tag-taxonomy/SKILL.md`
18|
19|## Quando usar
20|- Tags inconsistentes (ex: `ml` vs `machine-learning`)
21|- Apos muitos ingests (tags proliferam)
22|- Periodicamente
23|
24|## Relacionado
25|- [[skills/wiki-lint]] — Lint verifica consistencia, taxonomy gerencia
26|- [[skills/wiki-cross-linker]] — Links e tags sao complementares
27|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar tags em uso, distribuicao de tags por categoria, ou violacoes de taxonomia antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.