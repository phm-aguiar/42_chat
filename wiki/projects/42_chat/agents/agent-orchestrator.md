1|---
2|title: "agent-orchestrator — Executor Runtime SDD"
3|category: projects
4|tags: [sdd, agent, orchestrator, delegate-task]
5|summary: "Agente que lê DAG de tasks e spawna subagentes Dev/QA/Test em paralelo."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:.hermes/agents/agent-orchestrator/
10|lifecycle: in-progress
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.8
13|provenance:
14|  extracted: 0.8
15|  inferred: 0.2
16|  ambiguous: 0.0
17|---
18|
19|# agent-orchestrator
20|
21|> O capataz. Lê o plano (`tasks.md` com DAG), spawna subagentes (Dev, QA, Test), verifica entregas, escala bloqueios.
22|
23|## Funcionamento
24|
25|1. **Approval gate:** verifica `Aprovado: true` no spec.md
26|2. **Carrega DAG:** lê `tasks.md`, valida (sem ciclos, sem órfãs)
27|3. **Janela deslizante:** até 3 subagentes simultâneos via `delegate_task`
28|4. **Retry:** 3 tentativas com contexto enriquecido
29|5. **Validação:** verifica arquivos criados, smoke-test, exit code
30|6. **Escalação:** 3 falhas → pausa sub-árvore → input humano
31|
32|## Toolsets por papel
33|
34|| Papel | Toolsets |
35||---|---|
36|| Dev | `terminal`, `file` |
37|| QA | `terminal`, `file`, `web` |
38|| Test | `terminal`, `file` |
39|
40|## Como invocar
41|
42|```bash
43|agent-run agent-orchestrator "orquestra a feature 005"
44|```
45|
46|## Relacionado
47|
48|- [[projects/42_chat/agents/agent-onboard|onboard]] — Inicialização (complementar)
49|- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Formato que o orchestrator consome
50|- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Feature]] — Spec, plan e tasks
51|