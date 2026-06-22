---
title: "ADR-005: Summarization Strategy"
tags: [adr, latte, hardening]
status: accepted
created: "2026-06-20"
rag_score: 0.5
---

# ADR-005: Summarization Strategy — Compressão de contexto em sessões longas

## Status
Accepted

## Contexto

No LATTE original, após round 8, o contexto de `completed_tasks` do Lead podia atingir 3.000 tokens, causando *context saturation*: o Lead passava a decidir baseado apenas no que leu por último, ignorando tasks concluídas no início da execução. O paper *Multi-Agent Systems in Production* documenta este fenômeno: *"By turn 8 in a supervisor pattern, the 'completed tasks' context can be 3,000 tokens. We now summarize completed tasks every 4 turns."*

O número 4 não é arbitrário — vem dos experimentos do Kalvium Labs com 8 projetos. Sumarizar com mais frequência gasta LLM calls desnecessárias; com menos frequência, o contexto já saturou.

## Decisão

Context summarization a cada 4 rounds, baseado no paper:

- Campo `completed_summary: str = ""` no `CoordinationGraph` — sumário acumulativo
- Campo `round_since_summary: int = 0` — contador de rounds desde última sumarização
- A cada 4 rounds (`round_since_summary >= 4`), o Lead sumariza `completed_tasks` em 1-2 linhas
- Template: "Resumo (rounds 1-4): [T001, T002] concluídas. [T001] implementou X, [T002] configurou Y."
- Lead recebe `completed_summary` + últimos 4 rounds (não histórico completo)
- Reset `round_since_summary` após sumarização
- Opcional: não ativa se `completed_tasks < 5`

## Consequências

### Positive
- Prevenção de context saturation — Lead mantém visão completa do progresso
- Redução significativa de tokens no context do Lead (3.000 → ~500 tokens para histórico)
- Determinístico: intervalo fixo de 4 rounds, sem dependência de tokenizer
- Sumarização progressiva: cada sumário incorpora o anterior, mantendo continuidade

### Negative
- Custa 1 LLM call extra a cada 4 rounds para gerar o sumário
- Sumarização pode perder detalhes sutis de outputs de workers
- Se `completed_tasks < 5`, sumarização não ativa — runs curtos não se beneficiam

### Neutral
- Comportamento padrão (sem `completed_summary`) preserva execução original
- Intervalo de 4 rounds é fixo — não adaptativo

## Alternativas Consideradas

**Sumarização adaptativa (baseada em tokens, não rounds)**
- Rejeitado: (a) contar tokens de `completed_tasks` é frágil (depende do tokenizer do modelo), (b) rounds são determinísticos, (c) paper já testou 4 rounds como sweet spot.

**Sumarização a cada round**
- Rejeitado: gasta LLM calls desnecessárias. O contexto não satura em 1-3 rounds. Paper mostra que 4 rounds é o ponto ótimo.

**Sem sumarização (truncar contexto por tamanho)**
- Rejeitado: truncamento cego perde informação crítica. Sumarização preserva semanticamente o que importa.

**State pruning completo (descartar tasks concluídas)**
- Rejeitado: tasks concluídas contêm informações que o Lead pode precisar para decidir sobre tasks futuras (ex: "T003 já implementou X, T007 não precisa refazer").

## References
- Paper: *Multi-Agent Systems in Production* (Kalvium Labs) — context summarization every 4 turns
- Feature 005 spec: `specs/features/005-latte-hardening/spec.md`
- Feature 005 plan: `specs/features/005-latte-hardening/plan.md` (ADR-010 original)
- Orchestrator module: `.hermes/skills/sdd/latte_coordination/orchestrator.py`
