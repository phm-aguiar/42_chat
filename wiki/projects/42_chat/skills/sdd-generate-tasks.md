1|---
2|title: "sdd-generate-tasks"
3|category: projects
4|tags: [sdd, skill, tasks, DAG, execution]
5|sources: []
6|summary: Skill SDD v2.0.0 que gera tasks.md com DAG (dependências, paralelismo, isolamento de arquivos)
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# sdd-generate-tasks
13|
14|> Gera `tasks.md` com formato DAG (Directed Acyclic Graph) para execução paralela segura.
15|
16|## Localização
17|Skill Hermes: `.hermes/skills/sdd/generate-tasks/SKILL.md` (v2.0.0)
18|
19|## Função
20|- Approval gate: verifica `Aprovado: true` no spec.md
21|- Deriva tarefas atômicas com metadados DAG (Papel, Dependências, Paralelizável, Arquivos)
22|- Interação fase por fase via `clarify()`
23|- Validação de DAG: ciclos, dependências quebradas, tasks órfãs
24|- Isolamento de arquivos: tasks paralelas NUNCA compartilham paths
25|
26|## Pipeline
27|`sdd-generate-plan` → `plan.md` → **`sdd-generate-tasks`** → `tasks.md` → `agent-orchestrator`
28|
29|## Relacionado
30|- [[projects/42_chat/skills/sdd-generate-plan]] — Passo anterior
31|- [[projects/42_chat/features/feature-004-sdd-tasks-dag]] — Feature que implementou o formato DAG
32|- [[projects/42_chat/agents/agent-orchestrator]] — Consumidor do tasks.md
33|