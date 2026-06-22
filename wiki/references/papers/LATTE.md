---
title: "LATTE — Language Agent Teams for Task Evolution"
tags: [paper, multi-agent, coordination, task-graph, heartbeat, sdd]
status: implemented
created: 2026-06-19
rag_score: 0.5181
source: "https://arxiv.org/html/2605.06320v1"
authors: "Mieczkowski, Ku, Eisape, Arumugam, Matters, Collins, Sucholutsky, Griffiths (Princeton, Cambridge, MIT, NYU)"
feature: "[[projects/42_Framework/features/001-latte-coordination|Feature 001: LATTE Coordination]]"
---

# LATTE — Language Agent Teams for Task Evolution

> Coordination graph dinâmico para times de LLM. Implementado como Feature 001.

## Resumo

Framework de orquestração multi-agente onde um time de LLMs constroi e mantém coletivamente um **coordination graph** compartilhado. O grafo (DAG) codifica subtasks, dependências, atribuições de agentes e estado de progresso. Operadores de mutação (Discover, Assign, Claim, Complete, Release, Close, Verify) permitem adaptação dinâmica durante execução.

## Principais Contribuições

- **Coordination graph dinâmico**: alternativa a pipelines fixos (MetaGPT) e times descentralizados
- **7 operadores** com preconditions/postconditions formais e invariantes (DAG)
- **Heartbeat monitoring**: detecta stragglers após H=4 rounds, Release + reassign
- **Context scoping**: Workers recebem só task + outputs de dependências diretas
- **Verify seletivo**: verificação sob demanda em tasks de alto risco

## Resultados Reportados

- **-61% tokens** vs Leader-Worker (148K vs 379K)
- **-41% wall-clock** (3.5min vs 5.9min)
- **+10pp accuracy** (80% vs 70%)
- **5.3× menos overwrites**, **8.2× menos conflitos**
- **-56% straggler p95** (130s vs 294s)

## Aplicação no 42_Framework

Implementado como **[[projects/42_Framework/features/001-latte-coordination|Feature 001: LATTE Coordination]]** — substitui o DAG estático do [[concepts/sdd|orchestrator SDD]] por coordination graph dinâmico. 23 tasks, 8 módulos Python (~5500 linhas), ~40 testes.

### Módulos

| Módulo | Função |
|---|---|
| `orchestrator.py` | Loop A4.5 (heartbeat → frontier → dispatch → execute → check) |
| `heartbeat.py` | Straggler detection (H=4 rounds) |
| `frontier.py` | Cálculo de F_t (tasks prontas) |
| `dispatcher.py` | Spawn de Workers com context scoping |
| `lead_operators.py` | Assign, Release, Close, Verify, Discover |
| `worker_operators.py` | Claim, Complete, Discover |
| `graph_persistence.py` | Salva G_final como coordination-graph.md |
| `metrics.py` | Extrai métricas de coordenação (overwrite, waste, idle, p95) |

### Bug Corrigido

`Verify(v)` não propagava dependência para nós downstream. Correção: identificar todos os dependentes de `v` e adicionar `v-verify` às suas `deps`.

## Relacionado

- [[projects/42_Framework/features/001-latte-coordination|Feature 001]] — implementação no 42_Framework
- [[projects/42_Framework/features/002-experiential-memory|Feature 002]] — usa métricas LATTE como utility signal
- [[references/papers/A-MapReduce|A-MapReduce]] — memória experiencial cross-task
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — checkpointing e state pruning
- [[concepts/sdd|SDD]] — metodologia base
- [[concepts/sdd-workflow|SDD Workflow]] — pipeline com modo LATTE
- [[skills/agent-run|agent-run]] — orquestrador com heartbeat e operadores
- [[skills/sdd-generate-tasks|sdd-generate-tasks]] — gerador do G₀ com graph-operators
- [[skills/sdd-validate|sdd-validate]] — métricas de coordenação LATTE
