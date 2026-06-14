1|---
2|title: "003: Forjar Nova Skill"
3|category: projects
4|tags: [sdd, skills, hermes-agent, tooling]
5|summary: "Skill forge-new-skill para criar skills Hermes Agent com scaffold, template e validação."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:specs/features/003-forge-skill/
10|lifecycle: in-progress
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.8
13|provenance:
14|  extracted: 0.8
15|  inferred: 0.2
16|  ambiguous: 0.0
17|---
18|
19|# 003: Forjar Nova Skill
20|
21|> Skill que automatiza criação de novas skills Hermes Agent com scaffold, template e validação SDD.
22|
23|## Status
24|
25|**Em progresso.** Tasks concluídas: 5/10. Metade da feature implementada.
26|
27|## O que já funciona
28|
29|- `scaffold-skill.sh`: gera árvore `.hermes/skills/<nome>/` com `assets/`, `scripts/`, `references/`
30|- `template-skill.md`: placeholders `{{skill_name}}`, `{{skill_description}}`, `{{skill_title}}`
31|- `skill-format.md`: documentação do formato SKILL.md (frontmatter, descrição, paths)
32|- `SKILL.md` da forge-new-skill: fluxo de 4 passos
33|- `spec.md` da feature 003 no formato canônico SDD
34|
35|## Tasks pendentes
36|
37|- **T006:** Adicionar ao sdd-refactor-artifact suporte a plan.md + tasks.md
38|- **T007:** Testar skill dummy com forge-new-skill + sdd-validate
39|- **T008:** Escopo (projeto vs global) com confirmação do usuário
40|- **T009:** plan.md + tasks.md da própria feature 003
41|- **T010:** llms.txt na raiz
42|
43|## Relacionado
44|
45|- [[projects/42_chat/features/feature-002-sdd-templates|002: Templates]] — Formatos que a skill usa
46|- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Upgrade futuro do tasks.md
47|- `skill-forge` — Skill Hermes para criação de novas skills (`.hermes/skills/skill-forge/`)
48|