1|---
2|title: "wiki-status"
3|category: skills
4|tags: [wiki, skill, status, delta, auditoria]
5|sources: [.hermes/skills/wiki/status/SKILL.md]
6|summary: "Mostra o estado atual do vault: paginas, delta desde ultimo ingest, fontes pendentes, recomendacao append vs rebuild."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# wiki-status
13|
14|> Raio-X do vault. O que foi ingerido, o que mudou, o que falta.
15|
16|## Localizacao
17|`.hermes/skills/wiki/status/SKILL.md`
18|
19|## Quando usar
20|- Antes de `wiki-ingest` (avaliar delta)
21|- Diagnosticar vault desatualizado
22|- Ver cobertura de fontes
23|
24|## Relacionado
25|- [[skills/wiki-lint]] — Lint audita saude, status audita cobertura
26|- [[skills/wiki-ingest]] — Ingest usa status para decidir append vs rebuild
27|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar deltas anteriores, metricas historicas do vault, ou recomendacoes de rebuild antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.