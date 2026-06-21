---
title: "agent-run"
category: skills
tags: [agent, skill, runtime, delegate]
sources: [.hermes/skills/agent/agent-run/SKILL.md]
summary: "Runtime generico de agentes Hermes. Compila contexto limpo (sem corrosao) e spawna subagente isolado via delegate_task."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# agent-run

> Spawna qualquer agente definido em `.hermes/agents/` com contexto limpo.

## Localizacao
`.hermes/skills/agent/agent-run/SKILL.md`

## Quando usar
- `agent-run onboard "inicializa projeto"`
- `agent-run agent-orchestrator "orquestra feature 006"`
- Qualquer invocacao de agente Hermes

## O que faz
1. Le `AGENT.md` + `context.yaml` do agente
2. Compila micro-contexto limpo (spec, plan, sessoes relevantes)
3. Spawna subagente isolado via `delegate_task`

## Relacionado
- [[skills/skill-forge]] — Cria novos agentes e skills
- [[concepts/sdd-workflow]] — Pipeline que usa agent-run

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar agentes definidos, configuracoes de execucao, ou sessoes anteriores de agentes similares antes de agir.