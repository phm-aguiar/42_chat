---
title: "agent-run"
category: skills
tags: [agent, skill, runtime, delegate, latte, orchestrator]
sources: [.hermes/skills/agent/agent-run/SKILL.md]
summary: "Runtime generico de agentes Hermes. Compila contexto limpo (sem corrosao) e spawna subagente isolado via delegate_task. Suporta modo LATTE com coordination graph dinamico via graph-operators."
lifecycle: partial
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-19"
---

# agent-run

> Spawna qualquer agente definido em `.hermes/agents/` com contexto limpo.
> **Novo (LATTE):** Quando `graph-operators: enabled` no `tasks.md`, entra em modo de coordenacao dinamica com rounds, heartbeat, e 7 operadores de mutacao de grafo.

## Localizacao
`.hermes/skills/agent/agent-run/SKILL.md`

## Quando usar
- `agent-run onboard "inicializa projeto"`
- `agent-run agent-orchestrator "orquestra feature 006"`
- Qualquer invocacao de agente Hermes
- Feature com `graph-operators: enabled` no `tasks.md` → modo LATTE automatico

## O que faz
1. Le `AGENT.md` + `context.yaml` do agente
2. Compila micro-contexto limpo (spec, plan, sessoes relevantes)
3. Spawna subagente isolado via `delegate_task`
4. **(LATTE)** Se `graph-operators: enabled`, ativa orchestrator com coordination graph dinamico

---

## Modo LATTE (Coordenação Dinâmica)

### 1. Detecção: `graph-operators: enabled` no `tasks.md`

O `agent-run` inspeciona o frontmatter YAML do `tasks.md` da feature. Se encontrar:

```yaml
graph-operators: enabled
```

...o runtime **substitui** o pipeline sequencial tradicional pelo orchestrator LATTE. Parâmetros adicionais lidos do mesmo frontmatter:

| Parâmetro | Default | Descrição |
|---|---|---|
| `graph-operators` | (ausente) | `"enabled"` ativa modo LATTE; ausente = modo legacy (DAG estático) |
| `heartbeat-threshold` | `4` | Rounds consecutivos sem ação que disparam detecção de straggler |
| `max-rounds` | `40` | Número máximo de rounds antes de abortar execução |

**Modo legacy (compatibilidade reversa):** `tasks.md` sem `graph-operators` → orchestrator trata o DAG como estático, sem rounds, heartbeat, ou operadores dinâmicos.

### 2. Loop de Rounds (Algorithm A4.5)

O orchestrator executa um loop de rounds numerados `t = 1, 2, ..., T_max`:

```
Fase 0: Planning
  G₀ ← Lead.Discover(τ)     // Lead inicializa o coordination graph

Fase 1: Execution (loop)
  for t = 1 to T_max:
    1. Heartbeat monitoring
       → Flag para ℓ qualquer w ∈ W inativo por H rounds consecutivos

    2. Frontier identification
       → F_t ← {v ∈ G_t : status(v) = pending ∧ ∀(u,v) ∈ E_t, status(u) = done}

    3. Agent dispatching
       → Re-engaja Workers ocupados com novo contexto
       → Atribui Workers ociosos a tasks em F_t (máx 1 Worker por task)
       → Invoca ℓ se G_t mudou, heartbeat flagged, ou ℓ ocioso por H rounds

    4. Parallel execution
       → ℓ recebe grafo completo G_t
       → Workers recebem task atribuída ou F_t
       → Cada agente emite ações ⊆ {Discover, Claim, Complete}
       → G_t ← Apply(G_{t-1}, todas as ações emitidas)

    5. Termination check
       → if ∀v ∈ G_t : status(v) = done → return G_t
```

**Paralelismo máximo por round:** `min(|F_t|, |W|)` Workers despachados simultaneamente.

**Ordem intra-round:** Lead processa primeiro, depois Workers em paralelo; resultados coletados antes de avançar para `t+1`.

### 3. Heartbeat Monitoring (H = 4 rounds)

Mecanismo de detecção de *stragglers* — Workers que estão travados e não emitem ações:

| Propriedade | Valor |
|---|---|
| **Threshold default** | `H = 4` rounds consecutivos |
| **Configurável via** | `heartbeat-threshold` no frontmatter do `tasks.md` |
| **Unidade** | Rounds (não wall-clock time) |
| **Reset** | Qualquer ação do Worker (Claim, Complete, Discover) reseta o contador |
| **Escopo** | Workers com task em `assigned` ou `in_progress` |
| **Lead também monitorado** | Se Lead fica H rounds sem ação, é reengajado |

**Algoritmo por round:**
1. Para cada Worker `w` com task `v` em `assigned` ou `in_progress`: incrementa contador
2. Se `w` emitiu ação neste round → reseta contador para 0
3. Se contador ≥ H: flag `w` como STRAGGLER, notifica Lead
4. Lead pode: `Release` (devolver ao pool), `Reassign` (atribuir a outro Worker), ou `Broadcast` (dar instruções mais claras)

**Evidência do paper LATTE:** Release invocado em 36% dos trials; redução de 2.3× no p95 de tempo de conclusão.

### 4. Operadores Disponíveis

O protocolo LATTE define **7 operadores de mutação** do coordination graph. O orchestrator valida preconditions antes de aplicar cada um:

| # | Operador | Chamador | Efeito | Precondition principal |
|---|---|---|---|---|
| 1 | **Discover**(v, deps) | Lead / Worker (proposta) | Adiciona novo nó `pending` com dependências `deps` | `v ∉ V_t`, `deps ⊆ V_t`, grafo resultante é DAG |
| 2 | **Assign**(v, w) | Lead somente | Atribui nó `pending` a Worker `w` → status `assigned` | `status(v) = pending`, `w ∈ W` |
| 3 | **Claim**(v) | Worker somente | Worker reivindica nó do frontier → status `in_progress` | `v ∈ F_t`, agente ∈ `{⊥, w}` |
| 4 | **Complete**(v) | Worker somente | Worker marca task como concluída → status `done` | `status(v) = in_progress`, `agent(v) = w` |
| 5 | **Release**(v) | Lead somente | Devolve nó travado para `pending` (straggler) | `status(v) ∈ {assigned, in_progress}` |
| 6 | **Close**(v) | Lead somente | Força `done` em nó cujo Worker está inativo mas trabalho foi feito | Testes devem passar (`<run_tests />`) |
| 7 | **Verify**(v) | Lead somente | Spawna nó de verificação `v_ver` como dependente de `v` | `status(v) = done`, `v_ver ∉ V_t` |

**Resumo de permissões por papel:**

| Ação | Lead (ℓ) | Worker (w) |
|---|---|---|
| `Discover` | ✅ | ✅ (proposta; Lead avalia/merge) |
| `Assign` | ✅ | ❌ |
| `Claim` | ❌ | ✅ |
| `Complete` | ❌ | ✅ |
| `Release` | ✅ | ❌ |
| `Close` | ✅ | ❌ |
| `Verify` | ✅ | ❌ |

**Resolução de Claim duplo (race condition):** FIFO — primeiro Worker a chegar vence; perdedores recebem erro e devem re-poll o frontier.

### 5. Context Scoping

Workers recebem **contexto restrito** para evitar corrosão de contexto (*context pollution*):

| Agente | Recebe |
|---|---|
| **Lead (ℓ)** | Grafo completo `G_t` + mensagens de todos os agentes (visão global) |
| **Worker (w)** | Apenas sua task atribuída + **outputs das dependências diretas** |

- Workers **NÃO** têm visão global do grafo
- Workers **NÃO** recebem traces completos de outros Workers
- Cada Worker opera isolado com contexto mínimo necessário para sua task
- Outputs de dependências (`node.output`) são incluídos no contexto compilado

### 6. Arquivos de Referência

Implementação e contratos do LATTE em `.hermes/skills/sdd/latte-coordination/`:

```
.hermes/skills/sdd/latte-coordination/
├── references/
│   ├── latte-protocol.md       ← Contrato LATTE: 7 operadores, mensagens Lead↔Workers,
│   │                              invariantes do grafo, heartbeat, Algorithm A4.5
│   └── graph-schema.md         ← Schema do coordination graph em memória:
│                                  nodes[{id, agent, status, deps}], edges, F_t, validação
├── orchestrator.py             ← Loop de rounds (Algorithm A4.5)
├── heartbeat.py                ← Heartbeat monitoring (straggler detection)
├── frontier.py                 ← Frontier computation (F_t)
├── dispatch.py                 ← Dispatch + context scoping
├── lead_operators.py           ← Operadores Lead: Assign, Release, Close, Verify
├── worker_operators.py         ← Operadores Worker: Claim, Complete, Discover
├── g0_parser.py                ← Parsing de G₀ do tasks.md
├── graph_persistence.py        ← Persistência de G_final como coordination-graph.md
└── tests/
    ├── test_scenario_1_normal.py
    ├── test_scenario_2_straggler.py
    ├── test_scenario_3_verify.py
    ├── test_scenario_4_close.py
    ├── test_scenario_5_claim_race.py
    └── test_legacy_compat.py
```

Consulte [[skills/wiki-query|wiki-query]] para buscar o contrato LATTE completo, schema do grafo, e configurações de execução.

## Relacionado
- [[skills/skill-forge]] — Cria novos agentes e skills
- [[concepts/sdd-workflow]] — Pipeline que usa agent-run (inclui fluxo LATTE)
- [[skills/sdd-generate-tasks]] — Geração de tasks.md com `graph-operators`
- [[skills/sdd-validate]] — Métricas de coordenação LATTE

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar agentes definidos, configuracoes de execucao, ou sessoes anteriores de agentes similares antes de agir.