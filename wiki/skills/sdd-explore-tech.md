1|---
2|title: "sdd-explore-tech"
3|category: skills
4|tags: [sdd, skill, tech, stack, mapeamento]
5|sources: [.hermes/skills/sdd/explore-tech/SKILL.md]
6|summary: "Mapeia a stack tecnologica do projeto: linguagens, frameworks, banco de dados, CI/CD. Preenche .github/memory/tech.md."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-explore-tech
13|
14|> Descobre e documenta a stack tecnologica do projeto.
15|
16|## Localizacao
17|`.hermes/skills/sdd/explore-tech/SKILL.md`
18|
19|## Quando usar
20|- Apos `sdd-init-repo`
21|- Quando adicionar nova dependencia ao projeto
22|- Antes de `sdd-generate-plan` (precisa da stack definida)
23|
24|## O que faz
25|- Le `go.mod`, `package.json`, `pyproject.toml`, etc.
26|- Detecta CI/CD (GitHub Actions, GitLab CI)
27|- Atualiza `.github/memory/tech.md`
28|
29|## Relacionado
30|- [[skills/sdd-init-repo]] — Roda antes
31|- [[skills/sdd-validate]] — Valida o que foi mapeado
32|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar stack ja mapeado, dependencias documentadas, ou decisoes sobre tecnologias no vault antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.