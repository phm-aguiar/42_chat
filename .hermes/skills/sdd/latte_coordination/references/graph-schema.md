# Schema do Coordination Graph — LATTE

> **Base:** Seção 3.1 do paper LATTE (Mieczkowski et al., 2026), Definition 1 e Definition 2.
> **Propósito:** Especificação da estrutura de dados em memória para o coordination graph G_t
> usado pelo orchestrator LATTE (T004). Este documento é a referência canônica para o schema
> do grafo; toda implementação Python em `orchestrator.py`, `frontier.py`, `lead_operators.py`
> e `worker_operators.py` deve seguir este contrato.

---

## 1. Definição Formal (Paper LATTE, Definition 1)

> **Definition 1 (Dynamic Coordination Graph).** A *dynamic coordination graph* G_t at round
> t ∈ {1,…,T} is a directed acyclic graph G_t = (V_t, E_t, λ_t).
>
> - V_t: finite set of nodes, each corresponding to a subtask.
> - E_t ⊆ V_t × V_t: set of dependency edges between subtasks. (u,v) ∈ E_t means subtask v
>   cannot begin until u is complete.
> - λ_t: V_t → (A ∪ {⊥}) × S assigns each node an agent and a status.
>   - ⊥ (None) denotes unassigned.
>   - S := { pending, assigned, in_progress, done, verified }

### 1.1 Conjunto de agentes A

```
A = {ℓ} ∪ W
```
- ℓ (Lead): responsável por manter a estrutura de coordenação.
- W = {w₁, w₂, …, wₙ} (Workers): responsáveis por executar subtasks atribuídas.

### 1.2 Representação concreta do nó (Node)

Cada nó v ∈ V_t é representado como um dicionário Python com a seguinte estrutura:

```python
Node = {
    "id": str,           # Identificador único da subtask (ex: "T001", "T001-verify")
    "agent": str | None, # Agent ID atribuído ou None (⊥ no paper) se unassigned
    "status": str,       # Um dos valores em S (ver Seção 2)
    "deps": list[str],   # Lista de IDs dos nós dos quais este nó depende
                         # Equivale às arestas de entrada: (dep, self.id) ∈ E_t
}
```

**Regras:**
- `id` é único e imutável após criação.
- `deps` contém apenas IDs que existem em V_t no momento da inserção.
- O grafo completo é reconstruído a partir da lista de nós: arestas são derivadas de `node["deps"]`.

### 1.3 Representação concreta da aresta (Edge)

Arestas são derivadas dos `deps` de cada nó, mas mantemos uma representação explícita
para consultas eficientes de grafo (topological sort, cycle detection, reverse lookups):

```python
Edge = {
    "from": str,  # ID do nó upstream (pré-requisito)
    "to": str,    # ID do nó downstream (dependente)
}
```

**Invariante:** Para toda edge (u, v) ∈ E_t, u e v existem em V_t, e u precede v
topologicamente (o grafo é um DAG).

---

## 2. Status Possíveis (Conjunto S)

O conjunto de status S é finito, ordenado pela relação de progressão natural:

```
S = { pending, assigned, in_progress, done, verified }
```

| Status       | Significado                                                                | Quem define             |
|-------------|----------------------------------------------------------------------------|-------------------------|
| `pending`    | Subtask criada, pronta para ser atribuída ou claimed, mas sem owner ainda  | Discover, Release       |
| `assigned`   | Subtask atribuída a um Worker específico, mas execução ainda não iniciada   | Assign                  |
| `in_progress`| Worker está ativamente executando a subtask                                 | Claim (transição auto)  |
| `done`       | Worker concluiu a subtask com sucesso                                      | Complete, Close         |
| `verified`   | Subtask passou por verificação adicional de qualidade                      | Verify (conclusão)      |

### 2.1 Máquina de estados (State Machine)

```
                    Discover/Release
                         │
                    ┌────▼─────┐
          Assign    │ pending   │  Claim (auto-transition)
        ┌──────────►│           │◄──────────┐
        │           └───────────┘           │
        │                 │ Release         │
        │                 │                 │
   ┌────▼─────┐          │          ┌──────┴──────┐
   │ assigned  │          │          │ in_progress  │
   │           │──Claim──►│          │              │
   └───────────┘          │          └──────┬───────┘
        │                 │                 │
        │ Release         │          Complete│Close
        │                 │                 │
        └────────►┌───────▼──────┐   ┌──────▼──────┐
                  │   pending     │   │    done      │
                  └───────────────┘   └──────┬───────┘
                                             │
                                      Verify │ (conclusão)
                                             │
                                      ┌──────▼──────┐
                                      │  verified    │
                                      └──────────────┘
```

### 2.2 Transições válidas

| De           | Para          | Operador          | Precondição                                            |
|-------------|---------------|-------------------|--------------------------------------------------------|
| `pending`    | `assigned`    | Assign(v, w)      | v ∈ V_t, w ∈ W, status(v) = pending                    |
| `pending`    | `in_progress` | Claim(v)          | v ∈ F_t (frontier), Worker não tem task ativa           |
| `assigned`   | `in_progress` | Claim(v) (auto)   | Worker inicia execução após ser assigned                |
| `assigned`   | `pending`     | Release(v)        | v ∈ V_t, status(v) = assigned (straggler detection)     |
| `in_progress`| `done`        | Complete(v)       | Worker w é o agente atribuído a v                       |
| `in_progress`| `pending`     | Release(v)        | v ∈ V_t, status(v) = in_progress (straggler)            |
| `done`       | `verified`    | Verify(v) (fim)   | v_verify completa com sucesso, status(v) → verified     |
| `done` / `in_progress` | `done` | Close(v)    | Lead força done; testes passam mas worker travou        |

**Nota:** A transição `done → verified` é atômica e ocorre quando a task `v_verify` (criada
pelo operador Verify) é concluída com sucesso.

---

## 3. Definição Formal do Frontier F_t (Paper LATTE, Definition 2)

> **Definition 2 (Frontier).** The *frontier* F_t ⊆ V_t at round t is the set of pending nodes
> with no unsatisfied dependencies:
>
> F_t := { v ∈ V_t | status(v) = pending and ∀(u,v) ∈ E_t, status(u) = done }

### 3.1 Interpretação

F_t é o conjunto de subtasks **imediatamente executáveis** no round t. Qualquer nó em F_t:
1. Está com status `pending` (ninguém está trabalhando nele).
2. Todas as suas dependências diretas estão com status `done` (ou `verified` — ver nota).

Portanto, F_t determina o **paralelismo máximo** no round t:
- Número máximo de Workers dispatchados: min(|F_t|, |W|).

### 3.2 Nota sobre verified

No paper, a definição formal de F_t usa `status(u) = done`. Na nossa implementação,
`verified` é tratado como um super-estado de `done` — ou seja, um nó `verified` também
satisfaz a condição de dependência para seus sucessores. Portanto, na prática:

```
F_t := { v ∈ V_t | status(v) = pending and
        ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }
```

---

## 4. Funções de Validação e Consulta

Todas as funções abaixo são implementadas no módulo Python do orchestrator e operam
sobre a representação em memória do grafo (Seção 5).

### 4.1 `is_acyclic(graph: dict) -> bool`

Verifica se o grafo é um DAG (não contém ciclos).

```python
def is_acyclic(graph: dict) -> bool:
    """
    Verifica se o coordination graph é um DAG usando Kahn's algorithm
    (topological sort). Retorna True se e somente se não houver ciclos.

    Args:
        graph: Dict com estrutura conforme Seção 5.

    Returns:
        True se o grafo é acíclico, False caso contrário.

    Complexity:
        O(|V| + |E|) tempo, O(|V|) espaço.
    """
    # Build adjacency list and in-degree map
    adj = {node["id"]: [] for node in graph["nodes"]}
    indegree = {node["id"]: 0 for node in graph["nodes"]}

    for node in graph["nodes"]:
        for dep in node["deps"]:
            adj[dep].append(node["id"])
            indegree[node["id"]] += 1

    # Kahn's algorithm: queue nodes with indegree 0
    queue = [nid for nid, deg in indegree.items() if deg == 0]
    visited_count = 0

    while queue:
        current = queue.pop(0)  # FIFO
        visited_count += 1
        for neighbor in adj[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited_count == len(graph["nodes"])
```

**Quando chamar:** Antes de aceitar qualquer operação Discover (único operador que adiciona
arestas). Também como sanity check após qualquer mutação.

### 4.2 `is_valid_transition(graph: dict, node_id: str, new_status: str, operator: str) -> bool`

Verifica se uma transição de status é permitida pela máquina de estados (Seção 2.2).

```python
# Tabela de transições válidas
VALID_TRANSITIONS = {
    "pending":     {"assigned", "in_progress"},
    "assigned":    {"in_progress", "pending"},
    "in_progress": {"done", "pending"},
    "done":        {"verified"},
    "verified":    set(),  # Estado terminal
}

def is_valid_transition(graph: dict, node_id: str, new_status: str,
                        operator: str) -> bool:
    """
    Verifica se a transição de status é válida.

    Args:
        graph: Coordination graph atual.
        node_id: ID do nó a ser modificado.
        new_status: Status de destino.
        operator: Nome do operador solicitante (ex: "Assign", "Complete").

    Returns:
        True se a transição é válida.

    Raises:
        KeyError: Se node_id não existe no grafo.
    """
    node = _find_node(graph, node_id)
    current = node["status"]

    # Verificação genérica pela tabela de transições
    if new_status not in VALID_TRANSITIONS.get(current, set()):
        return False

    # Verificações específicas por operador (preconditions adicionais)
    if operator == "Assign" and new_status == "assigned":
        return current == "pending"
    if operator == "Claim" and new_status == "in_progress":
        return current in {"pending", "assigned"}
    if operator == "Complete" and new_status == "done":
        return current == "in_progress"
    if operator == "Release" and new_status == "pending":
        return current in {"assigned", "in_progress"}
    if operator == "Close" and new_status == "done":
        return current in {"in_progress", "done"}
    if operator == "Verify" and new_status == "verified":
        return current == "done"

    return True
```

**Quando chamar:** Antes de toda mutação de status (Assign, Claim, Complete, Release, Close,
Verify).

### 4.3 `compute_frontier(graph: dict) -> list[str]`

Calcula F_t — o conjunto de nós pending com todas as dependências satisfeitas.

```python
def compute_frontier(graph: dict) -> list[str]:
    """
    Calcula o frontier F_t conforme Definition 2 do paper LATTE.

    F_t := { v ∈ V_t | status(v) = pending and
             ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }

    Args:
        graph: Coordination graph atual.

    Returns:
        Lista ordenada de node IDs no frontier.
        Ordenação: por número de dependências (menos → mais), desempate alfabético.
        Esta ordenação prioriza tasks com menos blockers, maximizando throughput.

    Complexity:
        O(|V| + |E|) com caching interno de status.
    """
    # Build status lookup
    status_map = {node["id"]: node["status"] for node in graph["nodes"]}

    frontier = []
    for node in graph["nodes"]:
        if node["status"] != "pending":
            continue
        # Check all dependencies are done or verified
        deps_satisfied = all(
            status_map.get(dep) in ("done", "verified")
            for dep in node["deps"]
        )
        if deps_satisfied:
            frontier.append(node["id"])

    # Stable sort: fewer deps first, then alphabetical
    frontier.sort(key=lambda nid: (
        len(_find_node(graph, nid)["deps"]),
        nid
    ))
    return frontier
```

**Quando chamar:** No início de cada round t, após heartbeat e antes de dispatch.

---

## 5. Representação do Grafo como Dict Python

O coordination graph G_t é representado em memória como um dicionário Python com a
seguinte estrutura canônica. Esta é a representação usada por **todas** as funções do
orchestrator (T004), frontier (T006), lead_operators (T008) e worker_operators (T009).

### 5.1 Estrutura completa

```python
# G_t — Coordination Graph at round t
graph: dict = {
    "metadata": {
        "feature_id": str,          # ID da feature sendo executada (ex: "001")
        "round": int,               # Round atual t (0-indexed: G₀ tem round=0)
        "max_rounds": int,          # T_max — round máximo antes de abort
        "heartbeat_threshold": int,  # H — rounds sem ação que disparam straggler
        "workers": list[str],       # Lista de Worker IDs disponíveis (W)
        "lead": str,                # Lead ID (ℓ)
        "created_at": str,          # ISO 8601 timestamp
    },
    "nodes": [
        {
            "id": str,              # ID único da subtask
            "agent": str | None,    # Agent ID ou None (⊥ = unassigned)
            "status": str,          # pending | assigned | in_progress | done | verified
            "deps": list[str],      # IDs dos nós dos quais este depende
            "description": str,     # Descrição em linguagem natural da subtask
            "output": str | None,   # Output produzido pelo Worker (None até Complete)
            "rounds_inactive": int, # Contador de rounds sem ação (heartbeat)
            "created_at_round": int,# Round em que o nó foi criado
            "assigned_at_round": int | None,  # Round em que foi assignado
            "completed_at_round": int | None, # Round em que foi completado
        },
        # ... mais nós
    ],
    "edges": [
        {
            "from": str,  # ID do nó upstream
            "to": str,    # ID do nó downstream
        },
        # ... mais arestas (derivadas dos deps, mantidas para consulta rápida)
    ],
    "history": [
        {
            "round": int,        # Round em que ocorreu
            "operator": str,     # Nome do operador (Assign, Claim, Complete, ...)
            "node_id": str,      # Nó afetado
            "agent": str,        # Quem executou o operador
            "details": dict,     # Detalhes adicionais (ex: {"from_status": "pending", "to_status": "assigned"})
            "timestamp": str,    # ISO 8601
        },
        # ... histórico completo de mutações
    ],
}
```

### 5.2 Exemplo: G₀ mínimo

```python
graph_empty: dict = {
    "metadata": {
        "feature_id": "001",
        "round": 0,
        "max_rounds": 40,
        "heartbeat_threshold": 4,
        "workers": ["worker-1", "worker-2"],
        "lead": "lead-1",
        "created_at": "2026-06-19T00:00:00Z",
    },
    "nodes": [],
    "edges": [],
    "history": [],
}
```

### 5.3 Exemplo: G₀ com 3 tasks (do Cenário 1 — spec.md)

```python
graph_example: dict = {
    "metadata": {
        "feature_id": "001",
        "round": 0,
        "max_rounds": 40,
        "heartbeat_threshold": 4,
        "workers": ["w1", "w2"],
        "lead": "lead-1",
        "created_at": "2026-06-19T00:00:00Z",
    },
    "nodes": [
        {
            "id": "T001",
            "agent": None,
            "status": "pending",
            "deps": [],
            "description": "Estender schema tasks.md com graph-operators",
            "output": None,
            "rounds_inactive": 0,
            "created_at_round": 0,
            "assigned_at_round": None,
            "completed_at_round": None,
        },
        {
            "id": "T002",
            "agent": None,
            "status": "pending",
            "deps": [],
            "description": "Definir contrato LATTE: mensagens Lead↔Workers",
            "output": None,
            "rounds_inactive": 0,
            "created_at_round": 0,
            "assigned_at_round": None,
            "completed_at_round": None,
        },
        {
            "id": "T003",
            "agent": None,
            "status": "pending",
            "deps": ["T001"],
            "description": "Definir schema do coordination graph em memória",
            "output": None,
            "rounds_inactive": 0,
            "created_at_round": 0,
            "assigned_at_round": None,
            "completed_at_round": None,
        },
    ],
    "edges": [
        {"from": "T001", "to": "T003"},
    ],
    "history": [
        {
            "round": 0,
            "operator": "Discover",
            "node_id": "T001",
            "agent": "lead-1",
            "details": {"description": "Estender schema tasks.md"},
            "timestamp": "2026-06-19T00:00:00Z",
        },
        {
            "round": 0,
            "operator": "Discover",
            "node_id": "T002",
            "agent": "lead-1",
            "details": {"description": "Definir contrato LATTE"},
            "timestamp": "2026-06-19T00:00:00Z",
        },
        {
            "round": 0,
            "operator": "Discover",
            "node_id": "T003",
            "agent": "lead-1",
            "details": {"description": "Definir schema do coordination graph", "deps": ["T001"]},
            "timestamp": "2026-06-19T00:00:00Z",
        },
    ],
}
```

Neste exemplo:
- F₀ = {T001, T002} (T003 está pending mas depende de T001, que não está done ainda)
- max_workers_dispatch = min(2, 2) = 2

### 5.4 Funções auxiliares de acesso

```python
def _find_node(graph: dict, node_id: str) -> dict:
    """Retorna o nó com o ID especificado. Levanta KeyError se não encontrado."""
    for node in graph["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")

def _get_status_map(graph: dict) -> dict[str, str]:
    """Retorna um mapa node_id → status para consultas O(1)."""
    return {node["id"]: node["status"] for node in graph["nodes"]}

def _get_dependents(graph: dict, node_id: str) -> list[str]:
    """Retorna lista de nós que dependem de node_id (reverse edges)."""
    return [node["id"] for node in graph["nodes"] if node_id in node["deps"]]

def _is_terminal(graph: dict) -> bool:
    """Verifica se todos os nós estão em estado terminal (done ou verified)."""
    return all(node["status"] in ("done", "verified") for node in graph["nodes"])
```

---

## 6. Invariantes (Devem Ser Checados a Cada Mutação)

As invariantes abaixo DEVEM ser verificadas após toda mutação no grafo. Uma violação de
invariante é um erro grave (bug no orchestrator) e deve resultar em abort com mensagem
de diagnóstico.

### 6.1 I1: DAG Invariance (Acyclicidade)

```
I1: G_t é sempre um Directed Acyclic Graph (DAG).
```

**Verificação:** `is_acyclic(graph)` retorna True.

**Quando checar:** Após todo `Discover` (único operador que adiciona arestas).
Se `is_acyclic()` retornar False, o Discover é **rejeitado** e o Worker recebe
`"rejected: cycle detected"`.

**Justificativa:** O grafo representa dependências de execução. Um ciclo significaria
deadlock (duas tasks esperando uma à outra). O paper LATTE garante isso como DAG
invariance (Seção 3.2).

### 6.2 I2: Status Consistency

```
I2: Para todo nó v ∈ V_t, status(v) ∈ {pending, assigned, in_progress, done, verified}.
```

**Verificação:** Checar que todo `node["status"]` é um valor válido do conjunto S.

**Quando checar:** Após toda mutação de status.

### 6.3 I3: Single Active Assignment

```
I3: Nenhum Worker pode ter mais de uma task com status in_progress simultaneamente.
```

**Verificação:**
```python
def _check_single_assignment(graph: dict) -> bool:
    active = {}
    for node in graph["nodes"]:
        if node["status"] == "in_progress" and node["agent"] is not None:
            if node["agent"] in active:
                return False  # Worker já tem task ativa
            active[node["agent"]] = node["id"]
    return True
```

**Quando checar:** Após `Assign`, `Claim` (transição para `in_progress`).

**Justificativa:** Workers executam uma subtask por vez (context scoping — princípio D4).
Múltiplas tasks ativas quebrariam o isolamento de contexto.

### 6.4 I4: Edge Referential Integrity

```
I4: Toda aresta (u,v) ∈ E_t referencia nós existentes em V_t.
    Todo dep em node["deps"] referencia um node["id"] existente.
```

**Verificação:**
```python
def _check_edge_integrity(graph: dict) -> bool:
    node_ids = {node["id"] for node in graph["nodes"]}
    for node in graph["nodes"]:
        for dep in node["deps"]:
            if dep not in node_ids:
                return False
    for edge in graph["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            return False
    return True
```

**Quando checar:** Após toda mutação.

### 6.5 I5: Edge-Node Consistency (Bi-directional Sync)

```
I5: As arestas explícitas em graph["edges"] são consistentes com node["deps"].
    Toda aresta (u,v) em edges deve ter v com u em seus deps, e vice-versa.
```

**Verificação:**
```python
def _check_edge_node_consistency(graph: dict) -> bool:
    # Build set of (from, to) from nodes
    node_edges = set()
    for node in graph["nodes"]:
        for dep in node["deps"]:
            node_edges.add((dep, node["id"]))

    # Build set from explicit edges
    explicit_edges = set()
    for edge in graph["edges"]:
        explicit_edges.add((edge["from"], edge["to"]))

    return node_edges == explicit_edges
```

**Quando checar:** Após toda mutação estrutural.

**Justificativa:** Mantemos edges explícitos para consultas eficientes (reverse lookups,
topological sort), mas a fonte da verdade são os `deps` nos nós. Ambos devem estar
sempre em sincronia.

### 6.6 I6: Frontier Validity

```
I6: Nenhum nó no frontier F_t pode ter dependência com status diferente de done ou verified.
```

**Verificação:** Para todo v ∈ F_t, toda dependência u de v tem status(u) ∈ {done, verified}.

```python
def _check_frontier_validity(graph: dict) -> bool:
    status_map = _get_status_map(graph)
    frontier = compute_frontier(graph)
    for nid in frontier:
        node = _find_node(graph, nid)
        for dep in node["deps"]:
            if status_map.get(dep) not in ("done", "verified"):
                return False
    return True
```

**Quando checar:** No início de cada round, após `compute_frontier()`.

### 6.7 I7: Idempotent Complete

```
I7: Um nó com status done ou verified NÃO pode transitar para nenhum outro estado
    exceto done → verified (via Verify).
```

**Verificação:**
```python
def _check_terminal_immutable(graph: dict, node_id: str, new_status: str) -> bool:
    node = _find_node(graph, node_id)
    if node["status"] in ("done", "verified"):
        # Única transição permitida a partir de done é → verified
        if node["status"] == "done" and new_status == "verified":
            return True
        return False  # Qualquer outra transição é proibida
    return True  # Não é terminal, ok
```

**Quando checar:** Antes de `Complete`, `Close`, `Release` em nós done/verified.

### 6.8 I8: History Completeness

```
I8: Toda mutação no grafo deve ser registrada em graph["history"].
```

**Verificação:** Checar que `graph["history"]` contém uma entrada para cada mutação
de status, criação de nó, ou modificação de arestas.

**Quando checar:** Sanity check periódico (não a cada mutação — muito caro).
Pode ser verificado no `sdd-validate` pós-execução comparando o delta de estado com
o histórico.

---

## 7. Checklist de Validação (Resumo para Implementação)

Antes de merge de qualquer PR que modifique o grafo, verificar:

- [ ] `is_acyclic()` passa para todo G_t gerado
- [ ] `is_valid_transition()` cobre todas as transições da máquina de estados
- [ ] `compute_frontier()` retorna apenas nós pending com deps satisfeitas
- [ ] Invariantes I1-I8 são verificáveis programaticamente
- [ ] Representação dict é compatível com `json.dumps()` (todos os valores são JSON-serializáveis)
- [ ] Nós com status `done` ou `verified` nunca são reabertos (exceto `done → verified`)
- [ ] Nenhum Worker tem >1 task `in_progress`
- [ ] `graph["edges"]` e `node["deps"]` estão sempre em sincronia
- [ ] `graph["history"]` registra toda mutação com round, operator, node_id, agent e timestamp

---

## Referências

- Mieczkowski et al. (2026). *Improving the Efficiency of Language Agent Teams with
  Adaptive Task Graphs*. arXiv:2605.06320v1.
  - Definition 1: Dynamic Coordination Graph (Seção 3.1)
  - Definition 2: Frontier (Seção 3.1)
  - DAG Invariance (Seção 3.2)
  - Graph Mutation Operators: Appendix A3
  - Execution Protocol: Appendix A4.5 (Algorithm A4.5)
- Spec: `specs/features/001-latte_coordination/spec.md`
- Plan: `specs/features/001-latte_coordination/plan.md` (ADR-002: Grafo em memória)
- Tasks: `specs/features/001-latte_coordination/tasks.md` (T003: este arquivo)
