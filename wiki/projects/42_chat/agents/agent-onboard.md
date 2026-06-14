1|---
2|title: "onboard — Agente de Inicialização SDD"
3|category: projects
4|tags: [sdd, agent, onboard, init]
5|summary: "Agente que inicializa projetos no framework SDD: estrutura, stack, brainstorm."
6|created: "2026-06-13"
7|updated: "2026-06-13"
8|sources:
9|  - repo:.hermes/agents/onboard/
10|lifecycle: implemented
11|lifecycle_changed: "2026-06-13"
12|base_confidence: 0.9
13|provenance:
14|  extracted: 0.9
15|  inferred: 0.1
16|  ambiguous: 0.0
17|---
18|
19|# onboard
20|
21|> Agente de entrada do framework SDD. Inicializa a estrutura, mapeia a stack e conduz brainstorms de features.
22|
23|## Responsabilidades
24|
25|1. **Inicializar projeto:** `sdd-init-repo` + `sdd-explore-tech`
26|2. **Brainstorm de features:** `sdd-brainstorm` → spec.md interativo
27|3. **Encaminhar para execução:** orienta invocação do `agent-orchestrator`
28|
29|## Skills que carrega
30|
31|| Skill | Quando |
32||---|---|
33|| `sdd-init-repo` | Criar `.github/memory/` e `specs/` |
34|| `sdd-explore-tech` | Preencher `tech.md` |
35|| `sdd-brainstorm` | Entrevista interativa para spec.md |
36|| `sdd-validate` | Auditar estrutura SDD |
37|
38|## Como invocar
39|
40|```bash
41|agent-run onboard "inicializa o projeto 42_chat"
42|```
43|
44|## O que NÃO faz
45|
46|- Não implementa código
47|- Não toma decisões técnicas do plan.md
48|- Não modifica constitution.md sem permissão
49|- Não executa tasks — isso é o [[projects/42_chat/agents/agent-orchestrator]]
50|
51|## Relacionado
52|
53|- [[projects/42_chat/agents/agent-orchestrator]] — Executor runtime (complementar)
54|- [[sdd]] — Metodologia
55|- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Agent Orchestrator]] — Feature que implementa o executor
56|