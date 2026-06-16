1|---
2|title: "agent-run"
3|category: skills
4|tags: [agent, skill, runtime, delegate]
5|sources: [.hermes/skills/agent/agent-run/SKILL.md]
6|summary: "Runtime generico de agentes Hermes. Compila contexto limpo (sem corrosao) e spawna subagente isolado via delegate_task."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# agent-run
13|
14|> Spawna qualquer agente definido em `.hermes/agents/` com contexto limpo.
15|
16|## Localizacao
17|`.hermes/skills/agent/agent-run/SKILL.md`
18|
19|## Quando usar
20|- `agent-run onboard "inicializa projeto"`
21|- `agent-run agent-orchestrator "orquestra feature 006"`
22|- Qualquer invocacao de agente Hermes
23|
24|## O que faz
25|1. Le `AGENT.md` + `context.yaml` do agente
26|2. Compila micro-contexto limpo (spec, plan, sessoes relevantes)
27|3. Spawna subagente isolado via `delegate_task`
28|
29|## Relacionado
30|- [[skills/skill-forge]] — Cria novos agentes e skills
31|- [[concepts/sdd-workflow]] — Pipeline que usa agent-run
32|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar agentes definidos, configuracoes de execucao, ou sessoes anteriores de agentes similares antes de agir.