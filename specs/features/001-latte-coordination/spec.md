---
feature_id: "001"
title: "LATTE Coordination — Orquestração Dinâmica com Task Graphs"
status: draft
created: "2026-06-19"
author: phm-aguiar
tags: [sdd, orquestracao, multi-agente, latex, task-graph, coordenacao]
based_on: "LATTE: Language Agent Teams for Task Evolution (Mieczkowski et al., 2026)"
---

**Aprovado:** true

# LATTE Coordination — Orquestração Dinâmica com Task Graphs

> Aplica o protocolo LATTE ao orchestrator SDD, substituindo o DAG estático
> (`tasks.md` congelado) por um **coordination graph dinâmico** que evolui durante
> a execução. Subagentes descobrem novas tasks, fazem self-scheduling, e o Lead
> monitora stragglers com heartbeat, verifica qualidade seletivamente, e reassigna
> trabalho travado — sem esperar intervenção humana.

## Propósito

O pipeline SDD atual gera um `tasks.md` estático (G₀) que nunca muda durante
a execução. Se um subagente descobre trabalho não previsto (migration extra,
teste de integração faltando, edge case não mapeado), não há mecanismo para
incorporar isso ao grafo. Se um subagente trava, o orquestrador retry 3× cegamente
e escala pro humano — sem diagnóstico, sem reassignment tático.

O LATTE (Language Agent Teams for Task Evolution) mostrou que um **coordination
graph dinâmico** com operadores explícitos (Discover, Claim, Complete, Release,
Close, Verify) e heartbeat monitoring reduz tokens em 61%, wall-clock em 41%,
e conflitos entre agentes em 5-8×, enquanto sobe a acurácia de 58% para 80%
(vs DAG estático).

**Esta feature implementa o protocolo LATTE no orchestrator SDD** e adiciona
métricas de coordenação ao `sdd-validate`.

## Escopo

### Dentro do escopo

| Item | Descrição |
|---|---|
| **Orchestrator com rounds** | Loop Algorithm A4.5: heartbeat → frontier → dispatch → parallel exec → merge |
| **Operadores LATTE** | Discover, Assign, Claim, Complete, Release, Close, Verify no orchestrator e subagentes |
| **Heartbeat monitoring** | Detecta subagentes inativos por H rounds; notifica Lead; permite Release + reassign |
| **Frontier-based dispatch** | Só ativa subagentes quando há tasks prontas em F_t (max paralelismo sem violar deps) |
| **Self-scheduling (Claim)** | Subagentes ociosos podem Claim tasks do frontier sem esperar Assign do Lead |
| **Verify seletivo** | Lead pode spawnar verificação em tasks de alto risco (upstream, incerteza detectada) |
| **tasks.md estendido** | Nova seção `graph-operators: enabled` e `heartbeat-threshold: N` |
| **Métricas no sdd-validate** | Overwrite rate, wasted chars, idle rounds, straggler tail latency, inter-agent messages |
| **Persistência do grafo final** | G_final salvo em `wiki/projects/<nome>/coordination-graph.md` como artefato |
| **Gate humano preservado** | Aprovação de spec, escalação após 3 falhas do Lead, interação fase por fase no generate-tasks |

### Fora do escopo

- Kanban multi-profile — o grafo de coordenação é por feature, não cross-project
- Substituir `delegate_task` como mecanismo de spawn — continua usando delegate_task internamente
- Fine-tuning de agentes em dados de coordenação (paper menciona como trabalho futuro)
- Suporte a tasks não-software (paper foca em código; estender para outros domínios é v2)

## Constraints

1. **Rounds com heartbeat:** O orchestrator avança em rounds discretos. Heartbeat dispara após H rounds sem ação do subagente (default H=4, configurável).
2. **Max paralelismo = min(|F_t|, |W|):** Número de Workers dispatchados por round limitado pelo frontier e pool size.
3. **DAG invariance:** Todo operador preserva acyclicidade do grafo. Discover rejeitado se introduzir ciclo.
4. **Context scoping:** Workers recebem apenas: descrição da sua task + outputs das dependências diretas. Não recebem spec.md/plan.md completos.
5. **Gate humano:** `Aprovado: true` continua obrigatório. Escalação após 3 falhas do Lead (não do Worker) preservada.
6. **Hermes nativo:** Tudo roda via `delegate_task` e `terminal` — sem dependências externas além do Hermes Agent.
7. **Constitutional (portão #4):** Após execução, o vault Obsidian (`wiki/`) DEVE ser atualizado com o coordination graph final.

## Critérios de Sucesso

| Métrica | Baseline (DAG estático atual) | Alvo | Fonte |
|---|---|---|---|
| **Acurácia first-pass** | Features concluídas sem escalação humana | +15pp vs baseline | LATTE paper: 58% → 80% |
| **Tokens por feature** | Tokens gastos na execução (feature 006 ref) | -40% vs baseline | LATTE paper: 297K → 148K |
| **Wall-clock por feature** | Tempo total de execução | -30% vs baseline | LATTE paper: 6.0m → 3.5m |
| **Overwrite rate** | Vezes que agente sobrescreve trabalho de outro | < 5 por trial | LATTE paper: 22.8 → 4.3 |
| **Wasted output** | Caracteres escritos que não chegam ao produto final | -70% vs baseline | LATTE paper: 45K → 5K |
| **Idle rounds** | Proporção de rounds com agente ocioso | > 40% (eficiente, não desperdiçando) | LATTE paper: 51.3% idle |
| **Straggler p95** | Tempo no percentil 95 por task | -50% vs baseline | LATTE paper: 294s → 130s |

**Medição:** Feature 006 (agent-dev) como baseline estático. Rodar 5 trials com LATTE
e comparar médias. Métricas extraídas automaticamente pelo `sdd-validate` pós-execução.

## Funcionalidade

### Cenário 1: Execução normal com descoberta dinâmica

**Dado** que `spec.md` está aprovado e `tasks.md` contém G₀ com 5 tasks
**Quando** o orchestrator inicia a execução com LATTE
**Então**:
1. Lead calcula F₀ (tasks sem dependências pendentes) — ex: T001, T002
2. Dispatcheia subagentes para T001 e T002
3. Worker em T002 descobre que precisa de migration extra → emite `Discover(T007, deps=[T002])`
4. Lead avalia proposta, aceita, adiciona T007 ao grafo
5. T001 completa → F_t agora contém T003 + T007
6. Worker ocioso dá `Claim(T007)` sem esperar Assign
7. Execução continua até todos done

### Cenário 2: Straggler detection e reassignment

**Dado** que Worker X está assigned a T004 por 4 rounds sem emitir ação
**Quando** heartbeat detecta inatividade
**Então**:
1. Lead recebe notificação: "Worker X stalled em T004"
2. Lead emite `Release(T004)` — task volta pra pending
3. Lead pode `Assign(T004, WorkerY)` com instruções mais claras
4. OU Worker Y dá `Claim(T004)` do frontier
5. T004 concluída por Y

### Cenário 3: Verificação seletiva

**Dado** que T001 (core schema) foi marcada `done` e é upstream de 6 outras tasks
**Quando** Lead avalia o grafo e detecta alto risco (muitas dependências downstream)
**Então**:
1. Lead emite `Verify(T001)` — spawna T001-verify como task de verificação
2. T001-verify entra no grafo com `deps=[T001]`
3. Tasks downstream de T001 agora dependem de T001-verify, não de T001 direto
4. Worker de verificação revisa output e aprova ou corrige

### Cenário 4: Close forçado

**Dado** que todos os testes passam mas T003 ainda está `in_progress` (Worker esqueceu de emitir Complete)
**Quando** Lead confirma com `run_tests` que tudo passa
**Então**:
1. Lead emite `Close(T003)` — força `done` sem esperar Worker
2. Tasks dependentes de T003 são liberadas no próximo frontier

### Cenário 5: Métricas de coordenação no validate

**Dado** que a feature 001 foi executada com LATTE
**Quando** `sdd-validate` é executado no diretório da feature
**Então** o relatório inclui seção `Coordenação`:

```
Coordenação (LATTE):
  Overwrite rate:        3 (alvo < 5)      PASS
  Concurrent writes:     1                  PASS
  Wasted chars:          3,142              PASS
  Idle rounds:           48.7%              PASS
  Inter-agent messages:  15                 PASS
  Straggler p95:         87s                PASS
  Rounds total:          12
  Tasks discovered:      3 (dinâmicas)
  Verifications spawned: 1
  Releases:              0
```

## Edge Cases

1. **Grafo vazio:** Se G₀ tem 0 tasks (erro no generate-tasks), orchestrator aborta com "Empty task graph".
2. **Ciclo introduzido por Discover:** Lead rejeita proposta, Worker recebe "rejected: cycle detected".
3. **Claim duplo:** Dois Workers claim mesma task no mesmo round → FIFO, primeiro vence, segundo recebe "already claimed".
4. **Todos Workers stalled:** Heartbeat detecta todos parados → Lead escala pro humano (mecanismo atual).
5. **Verify em loop:** Lead não pode spawnar Verify de Verify (profundidade máxima 1).
6. **Timeout global:** Se execução exceder T_max rounds (default 40), aborta e reporta tasks pendentes.
7. **Worker morre (processo):** delegate_task retorna erro → Lead trata como stalled e faz Release automático.
8. **tasks.md sem `graph-operators`:** Modo legacy — orchestrator trata como DAG estático (compatibilidade reversa).
9. **Heartbeat threshold baixo demais (H=1):** Pode causar Releases prematuros em tasks legítimas longas. Mínimo H=2.

## Relacionado

- Paper: `wiki/_raw/ImprovingtheEfficiencyofLanguageAgentTeamswithAdaptiveTaskGraphs.md`
- Algoritmo: Appendix A4.5 do paper (LATTE Execution Protocol)
- Operadores: Appendix A3 (Graph Mutation Operators)
- [[concepts/sdd|SDD]] — Metodologia
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline atual
- [[skills/sdd-generate-tasks|sdd-generate-tasks]] — Gerador do G₀
- [[skills/agent-run|agent-run]] — Orquestrador atual
