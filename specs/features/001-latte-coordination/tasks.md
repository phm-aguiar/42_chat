---
feature_id: "001"
title: "LATTE Coordination — Orquestração Dinâmica com Task Graphs"
spec: "specs/features/001-latte-coordination/spec.md"
plan: "specs/features/001-latte-coordination/plan.md"
created: "2026-06-19"
author: phm-aguiar
graph-operators: enabled
heartbeat-threshold: 4
max-rounds: 40
---

# Tasks — LATTE Coordination

> DAG de 23 tasks atômicas em 4 fases canônicas.

## Fase 1: Fundação (Contratos e Schemas)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T001 | Estender schema `tasks.md`: seções `graph-operators`, `heartbeat-threshold`, `max-rounds`, sintaxe G₀ | Dev | Nenhuma | true | `.hermes/skills/sdd/generate-tasks/references/task-rules.md`, `specs/features/001-latte-coordination/tasks.md` (este arquivo como exemplo) |
| T002 | Definir contrato LATTE: formato de mensagens Lead↔Workers, pre/post conditions dos 7 operadores, invariantes do grafo | Dev | Nenhuma | true | `.hermes/skills/sdd/latte-coordination/references/latte-protocol.md` |
| T003 | Definir schema do coordination graph em memória: `nodes[{id, agent, status, deps}]`, `edges[{from, to}]`, frontier F_t, funções de validação | Dev | Nenhuma | true | `.hermes/skills/sdd/latte-coordination/references/graph-schema.md` |

## Fase 2: Implementação (Runtime LATTE)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T004 | Implementar loop de rounds (Algorithm A4.5): heartbeat → frontier → dispatch → parallel exec → merge → termination check | Dev | T001, T002, T003 | false | `.hermes/skills/sdd/latte-coordination/orchestrator.py` |
| T005 | Implementar heartbeat monitoring: detecta Workers inativos por H rounds, notifica Lead com lista de tasks stalled | Dev | T004 | true | `.hermes/skills/sdd/latte-coordination/heartbeat.py` |
| T006 | Implementar frontier computation (F_t): identifica tasks pending com todas dependências done | Dev | T004 | true | `.hermes/skills/sdd/latte-coordination/frontier.py` |
| T007 | Implementar dispatch + context scoping: spawna Workers via delegate_task com contexto restrito (task + outputs deps diretas) | Dev | T004, T006 | true | `.hermes/skills/sdd/latte-coordination/dispatch.py` |
| T008 | Implementar operadores Lead: Assign, Release, Close, Verify — mutações no grafo com verificação de preconditions | Dev | T004 | true | `.hermes/skills/sdd/latte-coordination/lead_operators.py` |
| T009 | Implementar operadores Worker: Claim, Complete, Discover — propostas de mutação, Lead avalia/merge | Dev | T004 | true | `.hermes/skills/sdd/latte-coordination/worker_operators.py` |
| T010 | Integrar `sdd-generate-tasks`: parsing de `graph-operators: enabled`, `heartbeat-threshold`, extração de G₀ do tasks.md | Dev | T001, T004 | true | `.hermes/skills/sdd/generate-tasks/SKILL.md` (patch), `.hermes/skills/sdd/latte-coordination/g0_parser.py` |
| T011 | Persistir G_final como `coordination-graph.md` no wiki: tabela markdown + grafo ASCII, após execução concluída | Dev | T007, T008, T009 | false | `.hermes/skills/sdd/latte-coordination/graph_persistence.py` |

## Fase 3: Validação (Smoke Tests + Métricas)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T012 | Smoke test — Cenário 1: execução normal com DAG simples (3 tasks, 1 Discover dinâmico, 1 Claim) | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_scenario_1_normal.py` |
| T013 | Smoke test — Cenário 2: straggler detection (worker parado 4 rounds) + Release + reassign | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_scenario_2_straggler.py` |
| T014 | Smoke test — Cenário 3: Verify spawn (task upstream de 3 outras → verificação seletiva) | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_scenario_3_verify.py` |
| T015 | Smoke test — Cenário 4: Close forçado (worker esquece Complete, testes passam, Lead força done) | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_scenario_4_close.py` |
| T016 | Smoke test — Edge case #3: Claim duplo no mesmo round (FIFO, primeiro vence) | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_scenario_5_claim_race.py` |
| T017 | Implementar métricas de coordenação no `sdd-validate`: overwrite rate, wasted chars, idle rounds, straggler p95, inter-agent messages | QA | T012, T013, T014, T015, T016 | false | `.hermes/skills/sdd/validate/SKILL.md` (patch), `.hermes/skills/sdd/validate/references/coordination-metrics.md` |
| T018 | Teste de compatibilidade reversa: tasks.md sem `graph-operators` → orchestrator trata como DAG estático (modo legacy) | QA | T011 | true | `.hermes/skills/sdd/latte-coordination/tests/test_legacy_compat.py` |

## Fase 4: Documentação (Wiki Update)

| ID | Descrição | Papel | Dependências | Paralelizável | Arquivos |
|---|---|---|---|---|---|
| T019 | Atualizar `wiki/concepts/sdd-workflow.md`: novo fluxo com LATTE rounds, heartbeat, operadores, G_final | Dev | T017, T018 | true | `wiki/concepts/sdd-workflow.md` |
| T020 | Atualizar `wiki/skills/agent-run.md`: documentar orquestrador com heartbeat + operadores LATTE | Dev | T017, T018 | true | `wiki/skills/agent-run.md` |
| T021 | Atualizar `wiki/skills/sdd-generate-tasks.md`: documentar graph-operators, heartbeat-threshold, G₀ | Dev | T017, T018 | true | `wiki/skills/sdd-generate-tasks.md` |
| T022 | Atualizar `wiki/skills/sdd-validate.md`: documentar métricas de coordenação (LATTE) | Dev | T017, T018 | true | `wiki/skills/sdd-validate.md` |
| T023 | Criar `wiki/references/toolkits/sdd/coordination-graph-template.md`: template markdown para G_final | Dev | T017, T018 | true | `wiki/references/toolkits/sdd/coordination-graph-template.md` |

## Validação do DAG

### Anti-ciclo (DFS)
```
T001 → T004 → T005 → ...
T002 → T004
T003 → T004
T004 → T005, T006, T008
T006 → T007
T004+T006 → T007
T004 → T008
T004 → T009
T001+T004 → T010
T007+T008+T009 → T011
T011 → T012, T013, T014, T015, T016, T018
T012-T016 → T017
T017+T018 → T019, T020, T021, T022, T023
```
✅ **Sem ciclos detectados.** Todos os caminhos são forward-only.

### Dependências quebradas
✅ Todas as refs em `Dependências` existem (T001-T018 referenciadas apenas após definidas).

### Órfãs
- T023: último nó, sem dependentes → ✅ intencional (template é artefato final)
- T018: sem dependentes além das docs → ✅ intencional (teste isolado)
- Nenhuma task sem dependências E sem dependentes (todas têm pelo menos um)

### Conflitos de arquivos
| Batch paralelo | Tasks | Arquivos | Conflito? |
|---|---|---|---|
| Fase 1 | T001, T002, T003 | `task-rules.md`, `latte-protocol.md`, `graph-schema.md` | ✅ Disjuntos |
| Fase 2 batch 1 | T005, T006, T008 | `heartbeat.py`, `frontier.py`, `lead_operators.py` | ✅ Disjuntos |
| Fase 2 batch 2 | T007, T009, T010 | `dispatch.py`, `worker_operators.py`, `g0_parser.py` + `SKILL.md` | ✅ Disjuntos |
| Fase 3 batch 1 | T012, T013, T014 | `test_scenario_1/2/3_normal/straggler/verify.py` | ✅ Disjuntos |
| Fase 3 batch 2 | T015, T016 | `test_scenario_4/5_close/claim_race.py` | ✅ Disjuntos |
| Fase 4 todas | T019-T023 | 5 páginas wiki distintas | ✅ Disjuntos |

### Sumário
- **Total tasks:** 23
- **Dev:** 13 (T001-T011, T019-T023)
- **QA:** 10 (T012-T018)
- **Paralelizáveis:** 19/23 (83%)
- **Ciclos:** 0
- **Deps quebradas:** 0
- **Órfãs:** 2 (intencionais)
- **Conflitos de arquivo:** 0
