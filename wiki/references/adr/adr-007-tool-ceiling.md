---
title: "ADR-007: Tool Ceiling"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
---

# ADR-007: Tool Ceiling — Limite de ferramentas por agente (5-8 ideal)

## Status
Accepted

## Contexto

No LATTE original, workers herdavam todas as ferramentas disponíveis no sistema (20+ tools), mas na prática cada tipo de worker precisava de apenas 4-6 ferramentas. O paper *Multi-Agent Systems in Production* recomenda especialização: *"Specializing agents means each one sees 4-6 relevant tools instead of the full library."*

O excesso de ferramentas tem dois custos: (a) ~2K tokens extras no system prompt por worker (cada tool com schema ocupa ~300 tokens), (b) aumento da probabilidade de o worker escolher a ferramenta errada (paradoxo da escolha). O `delegate_task` do Hermes já suporta `toolsets` nativamente — não é necessário reinventar.

## Decisão

Toolsets por task via `delegate_task` (API existente):

- `dispatcher.py` passa `toolsets` no spawn do worker baseado no tipo da task (Dev, QA, DevOps)
- Mapeamento default (`TOOLSET_MAP`):
  - **Dev**: `[terminal, file, patch, read_file, search_files]` — 5 tools
  - **QA**: `[terminal, file, read_file, search_files]` — 4 tools
  - **DevOps**: `[terminal, file, process]` — 3 tools
- Configurável por task no `tasks.md` (campo `toolsets: [terminal, file]`)
- Workers recebem apenas as tools do seu toolset — redução de 20+ para 4-6

## Consequências

### Positive
- Redução de ~2K tokens no system prompt por worker (20+ tools → 4-6)
- Menor superfície de decisão — worker escolhe entre 4-6 tools, não 20+
- Especialização natural: Dev tools para Dev, QA tools para QA
- API existente do `delegate_task` — zero nova infraestrutura
- Configurável por task para casos especiais (ex: task que precisa de `docker`)

### Negative
- Worker não pode usar ferramenta fora do seu toolset mesmo que precise (ex: Dev não tem `process`)
- Mapeamento default pode não cobrir todos os casos — tasks atípicas precisam de configuração manual
- Se `tasks.md` não especificar `toolsets`, o default é aplicado (pode surpreender)

### Neutral
- Comportamento original (todas as tools) preservado se `toolsets` não for passado
- `delegate_task` já suporta o parâmetro — mudança é apenas no dispatcher

## Alternativas Consideradas

**Tool filtering no context scoping (pós-spawn)**
- Rejeitado: (a) tools são definidas no system prompt antes do spawn, (b) filtrar pós-spawn não reduz tokens, (c) `delegate_task` já tem o parâmetro `toolsets` no momento certo.

**Tool ceiling global (mesmo toolset para todos os workers)**
- Rejeitado: Dev, QA e DevOps têm necessidades diferentes. Toolset único seria muito restritivo para Dev ou muito permissivo para QA.

**Tool discovery dinâmico (worker decide quais tools precisa)**
- Rejeitado: adiciona complexidade e custo (worker gastaria LLM calls decidindo tools). Mapeamento estático por role é suficiente e determinístico.

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — agent specialization with 4-6 tools
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-011 original)
- Hermes `delegate_task` API: parâmetro `toolsets`
- Dispatcher module: `.hermes/skills/sdd/latte_coordination/dispatcher.py`
