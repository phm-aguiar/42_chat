1|---
2|title: "sdd-brainstorm"
3|category: projects
4|tags: [sdd, skill, brainstorm, spec]
5|sources: []
6|summary: Skill SDD que conduz entrevista interativa via clarify() para gerar spec.md
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-brainstorm
13|
14|> Entry point do pipeline SDD. Transforma ideias em `spec.md` via entrevista interativa.
15|
16|## Localização
17|Skill Hermes: `.hermes/skills/sdd/brainstorm/SKILL.md`
18|
19|## Função
20|- Conduz entrevista com `clarify()` — uma pergunta por vez
21|- Gera `spec.md` com template canônico
22|- Gate de aprovação antes de prosseguir
23|
24|## Pipeline
25|`sdd-brainstorm` → `spec.md` → `sdd-generate-plan` → `plan.md` → `sdd-generate-tasks` → `tasks.md`
26|
27|## Relacionado
28|- [[concepts/sdd]] — Metodologia completa
29|- [[projects/42_chat/skills/sdd-generate-plan]] — Próximo passo
30|- [[projects/42_chat/features/feature-001-start-repo]] — Feature que iniciou o repo
31|