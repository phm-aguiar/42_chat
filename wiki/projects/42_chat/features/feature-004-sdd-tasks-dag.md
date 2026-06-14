1|---
2|title: "004: Tasks com DAG"
3|category: projects
4|tags: [sdd, tasks, dag, paralelismo]
5|summary: "Upgrade do sdd-generate-tasks: formato DAG com dependências, paralelismo e isolamento de arquivos."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:specs/features/004-sdd-tasks-dag/spec.md
10|lifecycle: draft
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.7
13|provenance:
14|  extracted: 0.7
15|  inferred: 0.3
16|  ambiguous: 0.0
17|---
18|
19|# 004: Tasks com DAG
20|
21|> Upgrade do `sdd-generate-tasks`: formato DAG no `tasks.md` com fases, dependências explícitas, paralelismo e isolamento de arquivos.
22|
23|## Status
24|
25|**Draft.** Spec escrita e revisada. `Aprovado: false`. Aguardando aprovação humana.
26|
27|## Por que DAG?
28|
29|O formato atual é flat (fases sequenciais com "Depende de Tnnn" simples). Não modela paralelismo explícito nem garante isolamento de arquivos entre tasks concorrentes.
30|
31|O Runtime Orchestrator (feature 005) **não funciona** sem este formato.
32|
33|## Formato DAG
34|
35|Cada task ganha metadados estruturados:
36|- `Papel:` Dev, QA, Test
37|- `Dependências:` T001, T002
38|- `Paralelizável: true|false`
39|- `Arquivos:` paths que a task modifica
40|
41|Paralelismo seguro: tasks da mesma fase com `Arquivos` disjuntos e sem dependência entre si.
42|
43|## Approval Gate
44|
45|1. Usuário altera `Aprovado: false` → `Aprovado: true` no spec.md
46|2. Invoca `sdd-generate-tasks`
47|3. Skill verifica o gate → gera tasks.md com DAG
48|
49|## Dependências
50|
51|- **Nenhuma.** Feature independente (upgrade de skill existente)
52|- **Consumida por:** [[projects/42_chat/features/feature-005-agent-orchestrator|005: Runtime Orchestrator]]
53|
54|## Relacionado
55|- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] — Feature anterior
56|- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Orchestrator]] — Consumidora do DAG
57|- [[sdd]] — Metodologia
58|