1|---
2|title: "005: Agent Orchestrator"
3|category: projects
4|tags: [sdd, orchestrator, delegate-task, paralelismo]
5|summary: "Agente supervisor que lê DAG de tasks e spawna subagentes Dev/QA/Test em paralelo com retry e escalação."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:specs/features/005-runtime-orchestrator/
10|lifecycle: in-progress
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.8
13|provenance:
14|  extracted: 0.8
15|  inferred: 0.2
16|  ambiguous: 0.0
17|---
18|
19|# 005: Agent Orchestrator
20|
21|> Agente Hermes que lê `tasks.md` com DAG e spawna subagentes especializados (Dev, QA, Test) em paralelo via `delegate_task`.
22|
23|## Status
24|
25|**Em implementação.** Spec ✓ Plan ✓ Tasks ✓ (16 tasks, 4 fases).
26|
27|## Artefatos
28|
29|- `spec.md` — Especificação funcional completa
30|- `plan.md` — 5 ADRs documentadas
31|- `tasks.md` — 16 tasks em 4 fases (Estrutura, Orquestração, Validação, Documentação)
32|- `.hermes/agents/agent-orchestrator/AGENT.md` — Agente implementado
33|- `.hermes/agents/agent-orchestrator/context.yaml` — Receita de contexto
34|
35|## Comportamento
36|
37|1. Lê `tasks.md` com DAG (formato da feature 004)
38|2. Verifica `Aprovado: true` no spec.md (approval gate)
39|3. Spawna subagentes em janela deslizante de 3 simultâneos
40|4. Política de retry: máx 3 tentativas com contexto enriquecido
41|5. Valida evidência de DONE antes de marcar `[x]`
42|6. Escala bloqueios para humano após 3 falhas
43|
44|## Como invocar
45|
46|```bash
47|agent-run agent-orchestrator "orquestra a feature 005"
48|```
49|
50|## Dependências
51|
52|- **Feature 004 (sdd-tasks-dag):** formato DAG no tasks.md
53|
54|## Relacionado
55|
56|- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Dependência direta
57|- [[projects/42_chat/agents/agent-onboard|onboard]] — Agente de inicialização (complementar)
58|- [[sdd]] — Metodologia
59|