1|---
2|title: "sdd-validate"
3|category: skills
4|tags: [sdd, skill, validacao, qualidade]
5|sources: [.hermes/skills/sdd/validate/SKILL.md]
6|summary: "Valida a conformidade SDD do repositorio: diretorios obrigatorios, artefatos por feature, AGENTS.md. Reporta PASS/FAIL/WARN."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-validate
13|
14|> Auditor de conformidade SDD. Read-only — nunca modifica arquivos.
15|
16|## Localizacao
17|`.hermes/skills/sdd/validate/SKILL.md`
18|
19|## Quando usar
20|- Antes de commit (gate de qualidade)
21|- Apos criar nova feature (spec/plan/tasks existem?)
22|- Periodicamente
23|
24|## Checks
25|- `.github/memory/` (constitution.md, tech.md)
26|- `specs/` (features, domain-events, infra)
27|- Cada feature: spec.md, plan.md, tasks.md
28|- `AGENTS.md`
29|
30|## Relacionado
31|- [[skills/sdd-init-repo]] — Cria a estrutura que validate audita
32|- [[skills/wiki-lint]] — Equivalente para o vault
33|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar validacoes anteriores, problemas recorrentes de conformidade, ou excecoes documentadas antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.