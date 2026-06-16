1|---
2|title: "skill-forge"
3|category: skills
4|tags: [general, skill, scaffold, criacao]
5|sources: [.hermes/skills/general/skill-forge/SKILL.md]
6|summary: "Cria novas skills Hermes com scaffold padronizado: SKILL.md com frontmatter YAML, diretorios references/ scripts/ assets/."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# skill-forge
13|
14|> Forja novas skills. Scaffold + template + validacao.
15|
16|## Localizacao
17|`.hermes/skills/general/skill-forge/SKILL.md`
18|
19|## Quando usar
20|- Criar nova skill Hermes
21|- Garantir que a skill segue o padrao (SKILL.md + frontmatter)
22|
23|## O que cria
24|```
25|.hermes/skills/categoria/nome/
26|├── SKILL.md          ← Frontmatter YAML + corpo markdown
27|├── references/       ← Documentos de referencia
28|├── scripts/          ← Scripts auxiliares
29|└── assets/           ← Templates e assets
30|```
31|
32|## Relacionado
33|- [[skills/agent-run]] — Skills sao usadas por agentes
34|- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] — Feature que originou esta skill
35|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar skills existentes com nomes similares, templates de SKILL.md, ou dependencias entre skills antes de agir.