---
title: "Coordination Graph Template"
tags: [sdd, reference]
created: 2026-06-20
rag_score: 0.4825
---
# Coordination Graph — Feature `{{FEATURE_ID}}`

> **Gerado em:** {{DATE}}
> **Feature ID:** `{{FEATURE_ID}}`
> **Lead:** `{{LEAD_AGENT}}`
> **Workers:** {{WORKER_LIST}}
> **Total de nós:** {{TOTAL_NODES}} | **Total de arestas:** {{TOTAL_EDGES}}
> **Rounds executados:** {{TOTAL_ROUNDS}} / {{MAX_ROUNDS}} | **Taxa de conclusão:** {{COMPLETION_RATE}}%

---

## 📋 Metadados

| Campo | Valor |
|-------|-------|
| `feature_id` | `{{FEATURE_ID}}` |
| `date` | {{DATE}} |
| `total_rounds` | {{TOTAL_ROUNDS}} |
| `completion_rate` | {{COMPLETION_RATE}}% |
| `lead` | `{{LEAD_AGENT}}` |
| `workers` | {{WORKER_LIST}} |
| `total_nodes` | {{TOTAL_NODES}} |
| `total_edges` | {{TOTAL_EDGES}} |

---

## 📋 Tabela de Tasks

| Task ID | Agent | Status | Dependências | Rounds Ativos |
|---------|-------|--------|--------------|---------------|
{{#each nodes}}
| `{{id}}` | {{agent}} | {{status_icon}} {{status}} | {{deps}} | {{active_rounds}} |
{{/each}}
| *(fim da tabela)* | — | — | — | — |

---

## 🌐 Grafo de Coordenação

```
{{ASCII_GRAPH}}
```

### Legenda de Status

| Ícone | Status | Descrição |
|-------|--------|-----------|
| ✅ | `done` | Task concluída com sucesso pelo Worker |
| 🔄 | `in_progress` | Worker está ativamente executando a task |
| ⏳ | `pending` | Task criada, aguardando atribuição ou claim |
| 📋 | `assigned` | Task atribuída a um Worker, execução ainda não iniciada |
| ❌ | `released` | Task devolvida ao pool (straggler/timeout) |
| 🔍 | `verified` | Task passou por verificação adicional de qualidade |

### Convenções do Grafo ASCII

- `[T001 ✅ done]` — nó raiz (sem dependências)
- `  |-> [T003 🔄 in_progress]` — aresta de dependência (T003 depende de T001)
- `  |-> [T004 ⏳ pending]` — múltiplos filhos sob o mesmo pai
- Nós sem indentação são raízes do DAG
- Cada nó aparece uma única vez (DAG, não árvore)

---

## 📊 Métricas

### Operadores Utilizados

| Operador | Contagem | Descrição |
|----------|----------|-----------|
| Discover | {{DISCOVER_COUNT}} | Criar nova task no grafo |
| Assign | {{ASSIGN_COUNT}} | Atribuir task a Worker |
| Claim | {{CLAIM_COUNT}} | Worker reivindica task do frontier |
| Complete | {{COMPLETE_COUNT}} | Worker conclui task com sucesso |
| Release | {{RELEASE_COUNT}} | Devolver task ao pool (straggler) |
| Close | {{CLOSE_COUNT}} | Lead força done em task concluída |
| Verify | {{VERIFY_COUNT}} | Spawnar verificação de qualidade |

### Distribuição de Status Final

| Status | Contagem | % do Total |
|--------|----------|------------|
| ⏳ pending | {{PENDING_COUNT}} | {{PENDING_PCT}}% |
| 📋 assigned | {{ASSIGNED_COUNT}} | {{ASSIGNED_PCT}}% |
| 🔄 in_progress | {{IN_PROGRESS_COUNT}} | {{IN_PROGRESS_PCT}}% |
| ✅ done | {{DONE_COUNT}} | {{DONE_PCT}}% |
| ❌ released | {{RELEASED_COUNT}} | {{RELEASED_PCT}}% |
| 🔍 verified | {{VERIFIED_COUNT}} | {{VERIFIED_PCT}}% |

### Métricas de Eficiência

| Métrica | Valor | Descrição |
|---------|-------|-----------|
| Overwrite | {{OVERWRITE_COUNT}} | Operações que sobrescreveram estado anterior sem progresso |
| Wasted | {{WASTED_COUNT}} | Rounds onde nenhuma task avançou de status |
| Idle | {{IDLE_COUNT}} | Workers que ficaram ociosos (sem tasks disponíveis no frontier) |
| Total de ações | {{TOTAL_ACTIONS}} | Soma de todas as operações registradas no histórico |
| Taxa de conclusão | {{COMPLETION_RATE}}% | (done + verified) / total_nodes × 100 |

---

## 📜 Histórico de Operações

> Timeline completa das operações executadas, organizada por round.

{{#each rounds}}
### Round {{round_number}}

| Timestamp | Operador | Task ID | Agent | Detalhes |
|-----------|----------|---------|-------|----------|
{{#each operations}}
| {{timestamp}} | `{{operator}}` | `{{task_id}}` | `{{agent}}` | {{details}} |
{{/each}}

**Resumo do Round {{round_number}}:**
- Operações executadas: {{op_count}}
- Tasks criadas: {{created_this_round}}
- Tasks concluídas: {{completed_this_round}}
- Tasks liberadas (release): {{released_this_round}}
- Verificações spawnadas: {{verified_this_round}}

{{/each}}

---

## 📖 Legenda de Status (Referência Rápida)

- ⏳ **pending** — Task criada, aguardando atribuição ou claim
- 📋 **assigned** — Task atribuída a um Worker, execução ainda não iniciada
- 🔄 **in_progress** — Worker está ativamente executando a task
- ✅ **done** — Worker concluiu a task com sucesso
- ❌ **released** — Task devolvida ao pool (straggler, timeout ou desistência)
- 🔍 **verified** — Task passou por verificação adicional de qualidade

---

*Template para `coordination-graph.md` — gerado pelo módulo `graph_persistence.py` do LATTE Coordination Engine.*
*Referência: `wiki/references/toolkits/sdd/coordination-graph-template.md`*
