1|---
2|title: "sdd-init-repo"
3|category: skills
4|tags: [sdd, skill, init, scaffold]
5|sources: [.hermes/skills/sdd/init-repo/SKILL.md]
6|summary: "Inicializa a estrutura SDD em um repositorio: .github/memory/, specs/, AGENTS.md. Entry point obrigatorio para novos projetos."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-init-repo
13|
14|> Inicializa um repositorio no padrao SDD. Primeiro passo de qualquer projeto.
15|
16|## Localizacao
17|`.hermes/skills/sdd/init-repo/SKILL.md`
18|
19|## Quando usar
20|- Novo projeto do zero
21|- Migrar projeto existente para SDD
22|
23|## O que cria
24|- `.github/memory/constitution.md` e `tech.md`
25|- `specs/features/`, `specs/domain-events/`, `specs/infra/`
26|- `AGENTS.md`
27|
28|## Relacionado
29|- [[skills/sdd-explore-tech]] — Mapeia stack apos init
30|- [[projects/42_chat/skills/sdd-brainstorm]] — Primeira feature apos init
31|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar repositorios inicializados, templates de constituicao, ou padroes de estrutura SDD antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.