1|---
2|title: "002: Templates Canônicos SDD"
3|category: projects
4|tags: [sdd, templates, spec, plan, tasks]
5|summary: "Define os 4 templates canônicos SDD: spec.md, plan.md, tasks.md, AGENTS.md + llms.txt."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:specs/features/002-sdd-templates/
10|lifecycle: in-progress
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.85
13|provenance:
14|  extracted: 0.85
15|  inferred: 0.15
16|  ambiguous: 0.0
17|---
18|
19|# 002: Templates Canônicos SDD
20|
21|> Define formatos canônicos para spec.md, plan.md, tasks.md, AGENTS.md e llms.txt.
22|
23|## Status
24|
25|**Em progresso.** Tasks concluídas: 7/11.
26|
27|## Formatos definidos
28|
29|- **spec.md** — 4 seções: Visão Geral, BDD, Restrições, Checklist
30|- **plan.md** — 4 seções: Metadados, Contratos, Decisões, Auditoria
31|- **tasks.md** — Fases com T001-TNNN, dependências explícitas
32|- **AGENTS.md** — Seção SDD Workflow
33|- **llms.txt** — Navegação, camadas, links
34|
35|## Tasks pendentes
36|
37|- **T008:** Geração de plan.md + tasks.md a partir de spec.md
38|- **T009:** sdd-validate verifica conformidade dos templates
39|- **T010:** Testes de snapshot para refatorador
40|- **T011:** Exemplos antes/depois na spec
41|
42|## Relacionado
43|
44|- [[projects/42_chat/features/feature-001-start-repo|001: Estrutura]] — Base que esta feature refina
45|- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] — Consumidora dos templates
46|- [[sdd]] — Metodologia
47|