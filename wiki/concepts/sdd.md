1|---
2|title: "Spec-Driven Development (SDD)"
3|category: concepts
4|tags: [sdd, metodologia]
5|summary: "Metodologia onde specs são a fonte primária; código deriva delas."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources: []
9|---
10|
11|# Spec-Driven Development (SDD)
12|
13|> Specs deixam de servir ao código; código passa a servir às specs.
14|
15|## Pipeline no 42_chat
16|
17|1. [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
18|2. [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
19|3. [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md
20|4. Aprovação humana (`Aprovado: true`)
21|5. [[projects/42_chat/agents/agent-orchestrator]] — Execução paralela com subagentes
22|
23|## Regras
24|
25|- Nunca implementar sem spec.md + plan.md aprovados
26|- Consultar [[constitution]] antes de qualquer código
27|- Validar estrutura periodicamente
28|