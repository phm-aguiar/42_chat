1|---
2|title: "llm-wiki"
3|category: skills
4|tags: [wiki, skill, arquitetura, fundamentos]
5|sources: [.hermes/skills/wiki/llm-wiki/SKILL.md]
6|summary: "Fundacao teorica do modelo wiki: 3 camadas (sources → wiki → schema), taxonomia, templates, confidence e lifecycle."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# llm-wiki
13|
14|> A teoria por tras do vault. O schema que governa como o conhecimento e compilado.
15|
16|## Localizacao
17|`.hermes/skills/wiki/llm-wiki/SKILL.md`
18|
19|## Quando usar
20|- Entender o modelo de 3 camadas
21|- Configurar novo vault
22|- Debug de comportamento do wiki
23|
24|## Conceitos chave
25|- **Compile, don't retrieve** — conhecimento destilado uma vez
26|- **3 camadas** — raw sources → wiki compilado → schema
27|- **Provenance** — toda claim rastreavel a uma fonte
28|- **Confidence + Lifecycle** — sinais de confianca por pagina
29|
30|## Relacionado
31|- [[concepts/wiki-model]] — Resumo executivo do modelo
32|- [[concepts/obsidian-flow]] — Como o modelo opera no dia a dia
33|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar implementacoes do padrao, vaults similares, ou decisoes sobre a arquitetura de 3 camadas antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.