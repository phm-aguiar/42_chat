---
title: "001: LATTE Coordination"
category: projects
tags:
  - latte
  - coordination
  - multi-agent
  - sdd
summary: "Orquestração dinâmica com coordination graph, operadores LATTE, heartbeat monitoring e métricas de coordenação."
created: "2026-06-19"
rag_score: 0.4736
updated: "2026-06-19"
status: implemented
sources:
  - repo:specs/features/001-latte-coordination/
lifecycle: verified
lifecycle_changed: "2026-06-19"
base_confidence: 0.95
provenance:
  extracted: 0.9
  inferred: 0.05
  ambiguous: 0.05
---

# 001: LATTE Coordination — Orquestração Dinâmica com Task Graphs

> Substitui o DAG estático (`tasks.md` congelado) por um **coordination graph dinâmico** que evolui durante a execução.
> Subagentes descobrem novas tasks, fazem self-scheduling, e o Lead monitora stragglers com heartbeat,
> verifica qualidade seletivamente, e reassigna trabalho travado — sem esperar intervenção humana.

## Status

**Implementada.** Tasks concluídas: 23/23.

## Resumo do Paper LATTE

Baseado no paper *"LATTE: Language Agent Teams for Task Evolution"* (Mieczkowski et al., 2026). O LATTE propõe um **coordination graph dinâmico** com operadores explícitos (Discover, Claim, Complete, Release, Close, Verify) e heartbeat monitoring, demonstrando:

- **-61% tokens** (297K → 148K)
- **-41% wall-clock** (6.0m → 3.5m)
- **Conflitos entre agentes reduzidos em 5-8×**
- **Acurácia sobe de 58% para 80%** (vs DAG estático com pré-planejamento)

A implementação no 42_Framework aplica o protocolo LATTE ao orchestrator SDD, substituindo o DAG estático por um coordination graph que evolui em rounds discretos (Algorithm A4.5 do paper).

### Como foi aplicado

1. **Rounds discretos** como unidade de heartbeat (ADR-001): cada round = heartbeat check → frontier compute → dispatch → parallel exec → merge.
2. **Grafo em memória** sem banco externo (ADR-002): G_t vive em memória durante execução; G_final é salvo como artefato post-mortem.
3. **delegate_task** como mecanismo de spawn (ADR-003): workers síncronos dentro do round, sem tmux ou processos externos.
4. **Context scoping restrito** (ADR-004): Workers recebem apenas sua task + outputs das dependências diretas (redução de 61% em tokens).
5. **Verify como task comum no grafo** (ADR-005): verificação é um nó `v_verify` com `deps=[v]`, tratada como qualquer outra task.

## Módulos Criados

Todos em `.hermes/skills/sdd/latte-coordination/`:

| Módulo | Arquivo | Tarefa | Descrição |
|--------|---------|--------|-----------|
| **Orchestrator** | `orchestrator.py` | T004 | Loop principal de rounds (Algorithm A4.5) + wrapper `CoordinationGraph` |
| **Heartbeat** | `heartbeat.py` | T005 | Detecção de Workers inativos por H rounds; notificação ao Lead |
| **Frontier** | `frontier.py` | T006 | Cálculo de F_t: tasks `pending` com todas dependências `done` |
| **Dispatcher** | `dispatcher.py` | T007 | Spawn de Workers via `delegate_task` com context scoping |
| **Lead Operators** | `lead_operators.py` | T008 | Operadores exclusivos do Lead: `Assign`, `Release`, `Close`, `Verify` |
| **Worker Operators** | `worker_operators.py` | T009 | Operadores dos Workers: `Claim`, `Complete`, `Discover` |
| **Graph Persistence** | `graph_persistence.py` | T011 | Serialização de G_final como `coordination-graph.md` (tabela + grafo ASCII + métricas) |
| **Metrics** | `metrics.py` | T017 | Métricas de coordenação: overwrite rate, wasted chars, idle rounds, straggler p95, inter-agent messages |

Referências de contrato em `references/`:
- `latte-protocol.md` — Contrato dos 7 operadores (pre/post conditions, invariantes)
- `graph-schema.md` — Schema canônico do coordination graph (nodes, edges, frontier, estados)

## 7 Operadores Implementados

| # | Operador | Chamador | Efeito |
|---|----------|----------|--------|
| 1 | **Assign(v, w)** | Lead | Atribui task `v` ao Worker `w` (pending → assigned) |
| 2 | **Claim(v)** | Worker | Worker pega task `v` do frontier sem esperar Assign (assigned → in_progress) |
| 3 | **Complete(v)** | Worker | Worker marca task `v` como concluída (in_progress → done) |
| 4 | **Release(v)** | Lead | Devolve task `v` para pending (straggler/inatividade) |
| 5 | **Close(v)** | Lead | Força `done` em `v` (testes passam mas Worker travou) |
| 6 | **Verify(v)** | Lead | Spawna `v-verify` como nova task no grafo com `deps=[v]` + propaga dep para todos os downstream |
| 7 | **Discover(v, deps)** | Worker/Lead | Propõe/adiciona nova task `v` com dependências `deps` (Lead avalia/DAG invariance) |

## ADRs (Architecture Decision Records)

5 ADRs documentadas em `specs/features/001-latte-coordination/plan.md`:

| ADR | Decisão | Justificativa |
|-----|---------|---------------|
| **ADR-001** | Rounds explícitos como unidade de heartbeat | Determinístico e reproduzível; independe de latência de API/network |
| **ADR-002** | Grafo em memória, sem banco externo | Ciclo de vida curto (minutos); crash recovery inviável com delegate_task |
| **ADR-003** | delegate_task como mecanismo de spawn | Síncrono dentro do round; evita polling/filesystem coordination |
| **ADR-004** | Context scoping restrito (task + deps diretas) | -61% tokens; reduz contaminação de contexto e alucinações |
| **ADR-005** | Verify como task comum no grafo | Reusa dispatch/heartbeat/Complete; evita "modo verificação" separado |

## Bug Corrigido Durante Implementação

**Bug:** Operador `Verify(v)` não propagava dependência para nós downstream.

**Descrição:** Inicialmente, ao chamar `verify(T001)`, o nó `T001-verify` era criado com `deps=[T001]`, mas tasks que dependiam de `T001` (ex: T002, T003, T004) **não** recebiam `T001-verify` como nova dependência. Isso fazia com que as tasks downstream executassem antes da verificação concluir — violando o propósito da verificação seletiva.

**Correção:** O operador `Verify` (em `lead_operators.py`, linhas 677-691) agora percorre todos os nós do grafo e adiciona `T001-verify` como dependência adicional de qualquer nó que tenha `T001` em `deps`. Arestas `(T001-verify, downstream)` são inseridas no grafo. O test `test_scenario_3_verify.py` (T014) valida este comportamento com asserts explícitos.

## Artefatos

- `spec.md` — Especificação funcional completa (8 cenários, 9 edge cases)
- `plan.md` — 5 ADRs, contratos, auditoria de constituição
- `tasks.md` — 23 tasks em 4 fases canônicas (Fundação, Implementação, Validação, Documentação)

### Smoke Tests (6 cenários + 1 compatibilidade)

| Test | Arquivo | Cenário |
|------|---------|---------|
| T012 | `test_scenario_1_normal.py` | Execução normal com Discover dinâmico + Claim |
| T013 | `test_scenario_2_straggler.py` | Straggler detection + Release + reassign |
| T014 | `test_scenario_3_verify.py` | Verify spawn + bloqueio downstream |
| T015 | `test_scenario_4_close.py` | Close forçado (Worker esquece Complete) |
| T016 | `test_scenario_5_claim_race.py` | Claim duplo no mesmo round (FIFO) |
| T018 | `test_legacy_compat.py` | Compatibilidade reversa (tasks.md sem `graph-operators`) |

### Documentação Wiki (Fase 4)

- Atualizado: `wiki/concepts/sdd-workflow.md` — Fluxo com rounds LATTE, heartbeat, operadores, G_final
- Atualizado: `wiki/skills/agent-run.md` — Orquestrador com heartbeat + operadores
- Atualizado: `wiki/skills/sdd-generate-tasks.md` — `graph-operators`, `heartbeat-threshold`, G₀
- Atualizado: `wiki/skills/sdd-validate.md` — Métricas de coordenação (LATTE)
- Criado: `wiki/references/toolkits/sdd/coordination-graph-template.md` — Template markdown para G_final

## Métricas de Coordenação (sdd-validate)

A seção `Coordenação (LATTE)` no relatório do `sdd-validate` inclui:

- Overwrite rate (alvo < 5 por trial)
- Wasted chars (caracteres descartados)
- Idle rounds (proporção de rounds ociosos, alvo > 40%)
- Straggler p95 (tempo no percentil 95 por task)
- Inter-agent messages (total Lead↔Workers)
- Tokens consumidos + wall-clock time
- **Feature 005:** LLM calls budget (llm_calls_made / max_llm_calls)
- **Feature 005:** Errors registrados (timeout, failure propagation)
- **Feature 005:** Verify mode (deterministic / llm)

## Hardening (Feature 005)

7 patches de produção aplicados ao LATTE em 2026-06-20:

| # | Mudança | ADR | Status |
|---|---------|-----|--------|
| 1 | Budget tracking (max_llm_calls=25) | ADR-006 | ✅ |
| 2 | Timeout por operador (45s + fallback) | ADR-007 | ✅ |
| 3 | Partial failure propagation (agent_errors) | ADR-008 | ✅ |
| 4 | Verify determinístico (checks antes do LLM) | ADR-009 | ✅ |
| 5 | Context summarization (a cada 4 rounds) | ADR-010 | ✅ |
| 6 | Equal-weight merge (prompt constraint) | ADR-012 | ✅ |
| 7 | Tool ceiling (4-6 tools por worker) | ADR-011 | ✅ |

**Benchmark:** -55% LLM calls, -50% rounds em cenário de stress com 5 tasks + 1 timeout.

Ver: [[projects/42_Framework/features/005-latte-hardening|Feature 005: LATTE Hardening]]

## Modo Legacy

Tasks.md sem `graph-operators: enabled` → orchestrator trata como DAG estático (compatibilidade reversa, T018).

## Relacionado

- **Paper:** [[references/papers/LATTE|LATTE — Language Agent Teams for Task Evolution]]
- [[specs/features/001-latte-coordination/spec|Spec]]
- [[specs/features/001-latte-coordination/plan|Plan]]
- [[specs/features/001-latte-coordination/tasks|Tasks]]
- [[concepts/sdd|SDD]] — Metodologia
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline com modo LATTE
- [[skills/sdd-generate-tasks|sdd-generate-tasks]] — Gerador do G₀ com graph-operators
- [[skills/agent-run|agent-run]] — Orquestrador com heartbeat + operadores
- [[projects/42_Framework/42_Framework]] — Meta-framework
