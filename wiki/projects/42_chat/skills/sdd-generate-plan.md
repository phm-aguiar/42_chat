1|---
2|title: "sdd-generate-plan"
3|category: projects
4|tags: [sdd, skill, plan, architecture, ADR]
5|sources: []
6|summary: Skill SDD que gera plan.md com decisões arquiteturais (ADR) a partir do spec.md
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-generate-plan
13|
14|> Gera `plan.md` a partir do `spec.md`, `tech.md` e `constitution.md`.
15|
16|## Localização
17|Skill Hermes: `.hermes/skills/sdd/generate-plan/SKILL.md`
18|
19|## Função
20|- Lê spec.md, tech.md e constitution.md
21|- Gera 4 seções canônicas: Metadados, Contratos, ADRs, Auditoria de Constituição
22|- Pelo menos 1 ADR gerada
23|- Auditoria contra todas as regras do constitution.md
24|
25|## Pipeline
26|`sdd-brainstorm` → `spec.md` → **`sdd-generate-plan`** → `plan.md` → `sdd-generate-tasks` → `tasks.md`
27|
28|## Relacionado
29|- [[projects/42_chat/skills/sdd-brainstorm]] — Passo anterior
30|- [[projects/42_chat/skills/sdd-generate-tasks]] — Próximo passo
31|- [[concepts/sdd]] — Auditado pelo plan
32|- [[concepts/sdd]] — Stack usada no plano
33|