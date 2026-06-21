---
feature_id: "001"
plan_for: "LATTE Coordination — Orquestração Dinâmica com Task Graphs"
spec: "specs/features/001-latte-coordination/spec.md"
created: "2026-06-19"
author: phm-aguiar
stack: "Hermes Agent (Python + skills YAML/Markdown)"
---

# Plano Arquitetural — LATTE Coordination

## Metadados

| Campo | Valor |
|---|---|
| **Stack** | Hermes Agent (runtime Python), skills em YAML/Markdown, Obsidian wiki |
| **Feature fonte** | `specs/features/001-latte-coordination/spec.md` |
| **Escopo (1 frase)** | Substituir DAG estático do orchestrator SDD por coordination graph dinâmico com operadores LATTE (Discover, Claim, Release, Verify) + heartbeat monitoring + métricas de coordenação no sdd-validate |

## Contratos e Fronteiras

### Entrada

| Artefato | Formato | Fonte |
|---|---|---|
| `tasks.md` com `graph-operators: enabled` | YAML frontmatter + seções DAG | `sdd-generate-tasks` (estendido) |
| `G_t` (coordination graph em memória) | DAG: `{nodes: [{id, agent, status, deps}], edges: [{from, to}]}` | Estado interno do orchestrator |
| Heartbeat threshold `H` (default=4) | Inteiro positivo | `tasks.md` seção `heartbeat-threshold` |

### Saída

| Artefato | Formato | Destino |
|---|---|---|
| `G_final` (grafo pós-execução) | Markdown renderizado como tabela + gráfico ASCII | `wiki/projects/<nome>/coordination-graph.md` |
| Métricas de coordenação | Seção `Coordenação (LATTE)` no relatório de validate | stdout do `sdd-validate` |
| Código implementado (inalterado) | O mesmo de sempre — a mudança é só na orquestração | Repo da feature |

### Operadores (interface Lead ↔ Workers)

```
Lead:
  Assign(v, w)    → worker w recebe task v
  Release(v)      → task v volta pra pending
  Close(v)        → força done em v (testes passam mas worker travou)
  Verify(v)       → spawna v_verify como nova task no grafo
  Discover(v,deps)→ adiciona nova task v com dependências deps

Workers:
  Claim(v)        → worker pega task v do frontier
  Complete(v)     → worker marca v como done
  Discover(v,deps)→ worker propõe nova task (Lead avalia)
```

### Fronteiras (o que NÃO é contratual)

- Workers NÃO podem Assign, Release, Close, Verify — só o Lead
- O grafo NÃO é persistido em banco externo — vive em memória durante execução
- O protocolo de rounds NÃO garante ordem entre Workers no mesmo round
- Claim duplo no mesmo round: FIFO, primeiro vence, segundo recebe "already claimed"

## ADRs (Architecture Decision Records)

### ADR-001: Rounds explícitos como unidade de heartbeat

**Decisão:** O orchestrator avança em rounds discretos (não contínuos). Cada round = heartbeat check → frontier compute → dispatch → parallel execute → merge.

**Justificativa:** O paper LATTE usa rounds como unidade natural de heartbeat (H=4 rounds sem ação = straggler). Sem rounds, heartbeat dependeria de wall-clock time (ruidoso: depende de latência de API, rede, modelo). Rounds são determinísticos e reproduzíveis.

**Alternativa rejeitada:** Heartbeat baseado em tempo real (ex: 120s). Rejeitado porque latência de API varia entre providers (DeepSeek vs OpenAI vs Anthropic) e entre horários do dia. Rounds normalizam isso — 4 rounds com DeepSeek podem ser 40s, com OpenAI 80s, mas a lógica de detecção é a mesma.

### ADR-002: Grafo em memória, sem banco externo

**Decisão:** O coordination graph G_t vive exclusivamente em memória durante a execução do orchestrator. Não usa SQLite, Redis, ou arquivo intermediário.

**Justificativa:** O ciclo de vida de uma feature SDD é curto (minutos a dezenas de minutos). Persistir o grafo em banco adiciona complexidade de serialização sem benefício — se o orchestrator morrer, a feature inteira precisa ser re-executada de qualquer forma. O G_final é salvo no wiki como artefato post-mortem.

**Alternativa rejeitada:** SQLite com WAL mode para crash recovery. Rejeitado porque (a) delegate_task não sobrevive a crash do processo pai, (b) recovery de estado parcial de um DAG de tasks de código é complexo e propenso a inconsistências (arquivos parcialmente escritos, testes em estado desconhecido).

### ADR-003: delegate_task como mecanismo de spawn (sem tmux/hermes process)

**Decisão:** Subagentes são spawnados via `delegate_task` (mecanismo nativo do Hermes), não via `hermes chat -q` ou tmux.

**Justificativa:** `delegate_task` é síncrono dentro do round — o orchestrator espera todos os Workers terminarem antes de avançar. Isso simplifica o merge de resultados e a atualização do grafo. `hermes chat -q` seria assíncrono e exigiria polling ou filesystem-based coordination.

**Alternativa rejeitada:** Spawn via `hermes chat -q` (background). Rejeitado porque exigiria coordenação via sistema de arquivos (pid files, output files), polling, e tratamento de timeouts — complexidade que o delegate_task já resolve.

### ADR-004: Context scoping restrito (task + dependências diretas)

**Decisão:** Workers recebem APENAS: descrição da sua task + outputs das dependências diretas concluídas. NÃO recebem spec.md, plan.md, ou constitution.md completos.

**Justificativa:** O paper mostra redução de 61% em tokens (379K → 148K) com context scoping. Além da economia, reduz contaminação de contexto — o Worker focado em implementar um handler HTTP não precisa ler sobre ADRs de autenticação ou edge cases do frontend.

**Alternativa rejeitada:** Passar spec.md completo para todo Worker. Rejeitado porque (a) gasta tokens desnecessariamente, (b) Workers alucinam mais com contexto irrelevante (paper mostra mais overwrites e conflitos), (c) fere o princípio D4 do LATTE (context scoping).

### ADR-005: Verify como task comum no grafo (não como round separado)

**Decisão:** `Verify(v)` insere um node `v_verify` no grafo com `deps=[v]`. É tratado como qualquer outra task — um Worker executa, pode ser Discover/Claim, e quando completa libera dependentes.

**Justificativa:** Tratar verificação como task normal do grafo simplifica a implementação (reusa dispatch, heartbeat, Complete). Evita criar um "modo verificação" separado no orchestrator.

**Alternativa rejeitada:** Verify como round separado (Lead faz review inline, sem spawnar Worker). Rejeitado porque (a) fere D4 (Lead teria que ler output completo do Worker), (b) adiciona um caminho de código separado no loop de rounds, (c) paper mostra que Verify emerge naturalmente como task.

## Auditoria de Constituição

> **Nota:** O repositório `42_Framework` é um meta-framework e não possui `constitution.md` formal. Os portões abaixo são derivados do pipeline SDD documentado em `wiki/concepts/sdd.md` e `wiki/concepts/sdd-workflow.md`.

| Regra | Status | Evidência |
|---|---|---|
| **Spec aprovado antes de implementar** | ✅ PASS | `spec.md` com `Aprovado: true` |
| **Vault wiki atualizado após feature** | ✅ PLAN | `G_final` salvo em `wiki/projects/<nome>/coordination-graph.md` |
| **Nunca inferir — ambiguidade = pergunta** | ✅ PASS | Edge case #5 (Verify loop), #1 (grafo vazio), #7 (worker morto) documentados |
| **Tasks paralelas com arquivos disjuntos** | ✅ PASS | DAG invariance (ADR-002) + operadores preservam acyclicidade |
| **Hermes nativo — sem dependências externas** | ✅ PASS | ADR-003: delegate_task, sem tmux, sem banco externo |
| **4 fases canônicas (Fundação, Impl, Validação, Docs)** | ⚠️ N/A | Esta feature modifica o runtime do pipeline, não implementa feature de código. As 4 fases se aplicam às features que USAM o pipeline, não ao pipeline em si. |
