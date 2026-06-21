#!/usr/bin/env python3
"""
worker_operators.py — Worker Graph Mutation Operators (T009)
=============================================================

Implementa os 3 operadores de mutação do Coordination Graph disponíveis
para Workers (w), conforme definidos no paper LATTE (Mieczkowski et al., 2026),
Appendix A3, e documentados em latte-protocol.md, Seções 2.2, 2.4 e 2.5.

Operadores:
  1. claim(graph, node_id, worker_id)    — Worker pega task do frontier F_t
  2. complete(graph, node_id, worker_id) — Worker marca task como done
  3. discover(graph, node_id, title, deps) — Worker propõe nova task (Lead avalia)

Cada operador:
  - É uma função pura que aceita um dict Python ou CoordinationGraph.
  - Valida preconditions e lança exceção (ValueError, KeyError) se violadas.
  - Retorna (graph, action) — o grafo modificado e a ação emitida.
  - O grafo de entrada NÃO é mutado; uma cópia profunda (deep copy) é
    retornada com as modificações aplicadas.

Referências:
  - graph-schema.md: schema canônico do G_t (Seção 5) e máquina de estados
  - latte-protocol.md: definições formais dos operadores (Seções 2.2, 2.4, 2.5)
  - lead_operators.py: referência de estilo e helpers compartilhados
  - orchestrator.py: CoordinationGraph wrapper
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Optional, Union

# ---------------------------------------------------------------------------
# Constantes compartilhadas (sincronizadas com lead_operators.py e orchestrator.py)
# ---------------------------------------------------------------------------

VALID_STATUSES: frozenset[str] = frozenset({
    "pending",
    "assigned",
    "in_progress",
    "done",
    "verified",
})

TERMINAL_STATUSES: frozenset[str] = frozenset({"done", "verified"})

DEPENDENCY_SATISFIED_STATUSES: frozenset[str] = frozenset({"done", "verified"})

# Transições válidas da máquina de estados (graph-schema.md, Seção 2.2)
VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending":     frozenset({"assigned", "in_progress"}),
    "assigned":    frozenset({"in_progress", "pending"}),
    "in_progress": frozenset({"done", "pending"}),
    "done":        frozenset({"verified"}),
    "verified":    frozenset(),
}


# ---------------------------------------------------------------------------
# Type alias: Graph pode ser um dict puro ou CoordinationGraph wrapper
# ---------------------------------------------------------------------------

GraphLike = Union[dict[str, Any], "CoordinationGraph"]


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _ensure_dict(graph: GraphLike) -> dict[str, Any]:
    """
    Converte o grafo para dict puro, sem modificar o original.

    Suporta tanto dict nativo quanto objetos CoordinationGraph (que expõem
    .raw ou são serializáveis via deep copy).
    """
    if isinstance(graph, dict):
        return copy.deepcopy(graph)

    # CoordinationGraph wrapper — usa .raw se disponível, senão deep copy
    if hasattr(graph, "raw"):
        return copy.deepcopy(graph.raw)

    # Fallback: deep copy genérico (funciona para CoordinationGraph)
    return copy.deepcopy(graph)


def _find_node(graph: dict[str, Any], node_id: str) -> dict[str, Any]:
    """
    Retorna o nó com o ID especificado. Levanta KeyError se não encontrado.

    Equivalente a _find_node() do graph-schema.md (Seção 5.4).
    """
    for node in graph["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")


def _has_node(graph: dict[str, Any], node_id: str) -> bool:
    """Retorna True se o nó existe no grafo."""
    return any(node["id"] == node_id for node in graph["nodes"])


def _get_status_map(graph: dict[str, Any]) -> dict[str, str]:
    """Retorna um mapa node_id → status para consultas O(1)."""
    return {node["id"]: node["status"] for node in graph["nodes"]}


def _is_in_frontier(graph: dict[str, Any], node_id: str) -> bool:
    """
    Verifica se um nó pertence ao frontier F_t.

    F_t := { v ∈ V_t | status(v) = pending ∧ ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }

    Conforme latte-protocol.md, Seção 1.2 e graph-schema.md, Seção 3.
    """
    node = _find_node(graph, node_id)
    if node["status"] != "pending":
        return False

    status_map = _get_status_map(graph)
    for dep in node.get("deps", []):
        if status_map.get(dep) not in DEPENDENCY_SATISFIED_STATUSES:
            return False

    return True


def _is_acyclic(graph: dict[str, Any]) -> bool:
    """
    Verifica se o coordination graph é um DAG usando Kahn's algorithm
    (topological sort). Retorna True se e somente se não houver ciclos.

    Equivalente a is_acyclic() do graph-schema.md (Seção 4.1).

    Complexity: O(|V| + |E|) tempo, O(|V|) espaço.
    """
    nodes = graph.get("nodes", [])
    if not nodes:
        return True

    # Build adjacency list and in-degree map
    adj: dict[str, list[str]] = {node["id"]: [] for node in nodes}
    indegree: dict[str, int] = {node["id"]: 0 for node in nodes}

    for node in nodes:
        for dep in node.get("deps", []):
            # dep → node["id"]: aresta de dependência
            if dep in adj:
                adj[dep].append(node["id"])
            indegree[node["id"]] += 1

    # Kahn's algorithm: queue nodes with indegree 0
    queue = [nid for nid, deg in indegree.items() if deg == 0]
    visited_count = 0

    while queue:
        current = queue.pop(0)  # FIFO
        visited_count += 1
        for neighbor in adj.get(current, []):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    return visited_count == len(nodes)


def _record_in_history(
    graph: dict[str, Any],
    operator: str,
    node_id: str,
    agent: str,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """
    Registra uma entrada no histórico de mutações do grafo (I8).

    Invariante I8 (graph-schema.md, Seção 6.8): toda mutação deve ser
    registrada no histórico.
    """
    entry = {
        "round": graph.get("metadata", {}).get("round", 0),
        "operator": operator,
        "node_id": node_id,
        "agent": agent,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    graph.setdefault("history", []).append(entry)


def _validate_transition(
    current: str,
    new_status: str,
    operator: str,
    node_id: str,
) -> None:
    """
    Valida se a transição de status é permitida pela máquina de estados
    e pelas preconditions específicas do operador.

    Lança ValueError se a transição for inválida.

    Baseado em is_valid_transition() do graph-schema.md (Seção 4.2).
    """
    # Validações específicas por operador (preconditions de status)
    if operator == "Claim" and new_status == "in_progress":
        if current not in ("pending", "assigned"):
            raise ValueError(
                f"Claim precondition failed: node '{node_id}' has status "
                f"'{current}', expected 'pending' or 'assigned'"
            )
        return

    if operator == "Complete" and new_status == "done":
        if current != "in_progress":
            raise ValueError(
                f"Complete precondition failed: node '{node_id}' has status "
                f"'{current}', expected 'in_progress'"
            )
        return

    # Fallback: validação genérica pela tabela de transições
    if new_status not in VALID_TRANSITIONS.get(current, frozenset()):
        raise ValueError(
            f"Invalid transition: '{current}' → '{new_status}' "
            f"for node '{node_id}' via operator '{operator}'"
        )


# ===========================================================================
# Operador 1: Claim — Worker pega task do frontier F_t (work-stealing)
# ===========================================================================

def claim(
    graph: GraphLike,
    node_id: str,
    worker_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Claim(v) — Worker-only.

    Permite que um Worker ocioso reivindique proativamente trabalho disponível
    no frontier (work-stealing) ou inicie a execução de uma task que o Lead
    já assignou para ele.

    Preconditions (latte-protocol.md, Seção 2.4):
      1. Work-stealing (pending): v ∈ F_t — o nó deve estar no frontier
         (todas as dependências satisfeitas e status = pending).
      1b. Picking up assigned: status(v) = assigned ∧ agent(v) = w —
          Worker inicia execução de task previamente assignada.
      2. agent(v) ∈ {⊥, w} — o nó deve estar unassigned (⊥) ou já
         atribuído a este mesmo Worker w.

    Postconditions:
      1. λ_t(v) ← (w, in_progress) — Worker assume o nó e inicia execução.

    Notas de implementação:
      - Mecanismo de work-stealing: Workers ociosos podem Claim tarefas do
        frontier sem esperar o Lead.
      - Claim de pending → in_progress (auto-atribuição).
      - Claim de assigned → in_progress (Worker inicia execução de task
        previamente assignada).
      - Reduz overhead de coordenação e melhora wall-clock time.
      - Claim duplo no mesmo round é resolvido por FIFO no orchestrator.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó a ser reivindicado do frontier.
        worker_id: ID do Worker que está reivindicando a task.

    Returns:
        Tuple (graph_modificado, ação_emitida) onde:
          - graph_modificado: dict com status e agente atualizados.
          - ação_emitida: dict representando a ação XML <claim_task>.

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se preconditions são violadas (nó não está no frontier,
                    ou agente não é None/nem o próprio Worker).
    """
    g = _ensure_dict(graph)

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # --- Precondition 1: v ∈ F_t (work-stealing) OU assigned ao mesmo Worker ---
    # Caso A: Work-stealing — nó pending/unassigned no frontier
    # Caso B: Worker inicia execução de task que o Lead assignou para ele
    if current_status == "pending":
        # Work-stealing: deve estar no frontier
        if not _is_in_frontier(g, node_id):
            # Status é pending, mas dependências não estão satisfeitas
            status_map = _get_status_map(g)
            unsatisfied = [
                f"{dep} (status={status_map.get(dep, '?')})"
                for dep in node.get("deps", [])
                if status_map.get(dep) not in DEPENDENCY_SATISFIED_STATUSES
            ]
            reason = (
                f"unsatisfied dependencies: {', '.join(unsatisfied)}"
                if unsatisfied
                else "unknown reason"
            )
            raise ValueError(
                f"Claim precondition failed: node '{node_id}' is not in "
                f"frontier ({reason})"
            )
    elif current_status == "assigned":
        # Picking up assigned task: só permitido para o Worker designado
        if current_agent != worker_id:
            raise ValueError(
                f"Claim precondition failed: node '{node_id}' is assigned to "
                f"agent '{current_agent}', cannot be claimed by '{worker_id}'"
            )
    else:
        raise ValueError(
            f"Claim precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'pending' or 'assigned'"
        )

    # --- Precondition 2: agent(v) ∈ {⊥, w} ---
    if current_agent is not None and current_agent != worker_id:
        raise ValueError(
            f"Claim precondition failed: node '{node_id}' is already assigned "
            f"to agent '{current_agent}', cannot be claimed by '{worker_id}'"
        )

    # --- Valida transição ---
    _validate_transition(current_status, "in_progress", "Claim", node_id)

    # --- Aplica mutação ---
    node["status"] = "in_progress"
    node["agent"] = worker_id
    if current_status == "pending":
        # Auto-atribuição: registra o round de assign como o atual
        node["assigned_at_round"] = g.get("metadata", {}).get("round", 0)
    node["rounds_inactive"] = 0

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "to_status": "in_progress",
        "from_agent": current_agent,
        "to_agent": worker_id,
        "note": "work-stealing" if current_agent is None else "assigned task started",
    }
    _record_in_history(g, "Claim", node_id, worker_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "claim_task",
        "id": node_id,
        "worker": worker_id,
    }

    return g, action


# ===========================================================================
# Operador 2: Complete — Worker marca task como done
# ===========================================================================

def complete(
    graph: GraphLike,
    node_id: str,
    worker_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Complete(v) — Worker-only.

    Worker sinaliza que concluiu com sucesso a execução de sua subtask.

    Preconditions (latte-protocol.md, Seção 2.5):
      1. status(v) = in_progress — o Worker deve estar ativamente
         executando a task.
      2. agent(v) = w — somente o Worker designado pode marcar como
         concluído.

    Postconditions:
      1. λ_t(v) ← (w, done) — mantém o agente e altera status para done.

    Notas de implementação:
      - Worker só deve emitir Complete após verificar que testes passam.
      - Se testes falham, Worker deve usar Discover para criar follow-up
        fix task, NÃO marcar como done.
      - É o mecanismo normal de progresso — desbloqueia dependentes.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó a ser concluído.
        worker_id: ID do Worker que está completando a task.

    Returns:
        Tuple (graph_modificado, ação_emitida) onde:
          - graph_modificado: dict com status atualizado para done.
          - ação_emitida: dict representando a ação XML <complete_task>.

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se preconditions são violadas (status não é in_progress,
                    ou agente não é o Worker).
    """
    g = _ensure_dict(graph)

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # --- Precondition 1: status(v) = in_progress ---
    if current_status != "in_progress":
        raise ValueError(
            f"Complete precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'in_progress'"
        )

    # --- Precondition 2: agent(v) = w ---
    if current_agent != worker_id:
        raise ValueError(
            f"Complete precondition failed: node '{node_id}' is assigned to "
            f"agent '{current_agent}', not '{worker_id}'. Only the assigned "
            f"Worker can mark a task as complete."
        )

    # --- Valida transição ---
    _validate_transition(current_status, "done", "Complete", node_id)

    # --- Aplica mutação ---
    node["status"] = "done"
    # Preserva o agente original para rastreabilidade
    node["completed_at_round"] = g.get("metadata", {}).get("round", 0)
    node["rounds_inactive"] = 0

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "to_status": "done",
        "agent": worker_id,
        "note": "completed by Worker",
    }
    _record_in_history(g, "Complete", node_id, worker_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "complete_task",
        "id": node_id,
        "worker": worker_id,
    }

    return g, action


# ===========================================================================
# Operador 3: Discover — Worker propõe nova task (Lead avalia depois)
# ===========================================================================

def discover(
    graph: GraphLike,
    node_id: str,
    title: str,
    deps: Optional[list[str]] = None,
    description: Optional[str] = None,
    worker_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Discover(v, deps) — Worker (proposal).

    Worker propõe uma nova subtask descoberta durante a execução.
    A proposta é avaliada pelo Lead, que faz merge no grafo.

    Preconditions (latte-protocol.md, Seção 2.2):
      1. v ∉ V_t — o nó não pode já existir no grafo.
      2. deps ⊆ V_t — todas as dependências declaradas devem existir.
      3. A adição preserva a aciclicidade do grafo (DAG).

    Postconditions:
      1. V_t ← V_t ∪ {v}
      2. E_t ← E_t ∪ {(d, v) | d ∈ deps}
      3. λ_t(v) ← (⊥, pending)

    Notas de implementação:
      - Workers podem propor Discover; o Lead avalia e faz merge.
      - Discover é o operador mais frequente (36% dos trials no paper).
      - Worker deve propor Discover para criar follow-up fix tasks quando
        testes falham, em vez de marcar como done incompleto.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID único da nova subtask proposta.
        title: Título descritivo da task.
        deps: Lista de IDs de nós dos quais esta task depende (default: []).
        description: Descrição detalhada (default: usa title).
        worker_id: ID do Worker que está propondo a task.

    Returns:
        Tuple (graph_modificado, ação_emitida) onde:
          - graph_modificado: dict com o novo nó e arestas adicionados.
          - ação_emitida: dict representando a ação XML <discover_task>.

    Raises:
        ValueError: Se node_id já existe, deps contém IDs inexistentes,
                    ou a adição criaria um ciclo.
    """
    g = _ensure_dict(graph)
    deps = deps or []
    worker_id = worker_id or "worker-unknown"

    # --- Precondition 1: v ∉ V_t ---
    if _has_node(g, node_id):
        raise ValueError(
            f"Discover precondition failed: node '{node_id}' already exists"
        )

    # --- Precondition 2: deps ⊆ V_t ---
    for dep in deps:
        if not _has_node(g, dep):
            raise ValueError(
                f"Discover precondition failed: dependency '{dep}' not found "
                f"in graph (required by node '{node_id}')"
            )

    # --- Precondition 3: aciclicidade ---
    # Simula a adição do nó e verifica se o grafo candidato é um DAG
    candidate = copy.deepcopy(g)
    new_node = {
        "id": node_id,
        "agent": None,
        "status": "pending",
        "deps": list(deps),
        "description": description or title,
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": candidate.get("metadata", {}).get("round", 0),
        "assigned_at_round": None,
        "completed_at_round": None,
    }
    candidate.setdefault("nodes", []).append(new_node)
    for dep in deps:
        candidate.setdefault("edges", []).append({"from": dep, "to": node_id})

    if not _is_acyclic(candidate):
        raise ValueError(
            f"Discover precondition failed: adding node '{node_id}' with "
            f"deps {deps} would create a cycle in the graph"
        )

    # --- Aplica mutações no grafo real ---
    g.setdefault("nodes", []).append(new_node)
    for dep in deps:
        g.setdefault("edges", []).append({"from": dep, "to": node_id})

    # --- Registra no histórico (I8) ---
    details = {
        "description": description or title,
        "deps": list(deps),
        "proposed_by": worker_id,
        "note": "Worker proposal — Lead must evaluate and confirm merge",
    }
    _record_in_history(g, "Discover", node_id, worker_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "discover_task",
        "id": node_id,
        "title": title,
        "deps": list(deps),
        "description": description or title,
        "proposed_by": worker_id,
        "note": "Worker proposal",
    }

    return g, action


# ===========================================================================
# Convenience: aplica ação ao CoordinationGraph wrapper
# ===========================================================================

def apply_to_graph(
    graph: "CoordinationGraph",
    node_id: str,
    operator: str,
    worker_id: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Aplica um operador do Worker diretamente a um objeto CoordinationGraph,
    usando seus métodos internos para manter o cache consistente.

    Esta função é um adapter que permite que o orchestrator chame os
    operadores sem precisar converter para dict e depois reconstruir
    o CoordinationGraph.

    Args:
        graph: Objeto CoordinationGraph (do orchestrator.py).
        node_id: ID do nó alvo.
        operator: Nome do operador ("Claim", "Complete", "Discover").
        worker_id: ID do Worker (default: tenta extrair de kwargs).
        **kwargs: Argumentos adicionais específicos do operador.

    Returns:
        Ação emitida como dict.

    Raises:
        ValueError: Se preconditions são violadas ou operador desconhecido.
        KeyError: Se node_id não existe.
    """
    operator_map = {
        "Claim": _apply_claim,
        "Complete": _apply_complete,
        "Discover": _apply_discover,
    }

    handler = operator_map.get(operator)
    if handler is None:
        raise ValueError(f"Unknown Worker operator: '{operator}'")

    worker_id = worker_id or kwargs.get("worker_id") or "worker-unknown"
    return handler(graph, node_id, worker_id, **kwargs)


def _apply_claim(
    graph: "CoordinationGraph",
    node_id: str,
    worker_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Claim diretamente no CoordinationGraph."""
    node = graph.find_node(node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # Precondition: v ∈ F_t (work-stealing) OU assigned ao mesmo Worker
    if current_status == "pending":
        # Work-stealing: deve estar no frontier
        frontier = graph.frontier if hasattr(graph, "frontier") else graph.compute_frontier()
        if node_id not in frontier:
            status_map = {n["id"]: n["status"] for n in graph.nodes}
            unsatisfied = [
                f"{dep} (status={status_map.get(dep, '?')})"
                for dep in node.get("deps", [])
                if status_map.get(dep) not in ("done", "verified")
            ]
            reason = (
                f"unsatisfied dependencies: {', '.join(unsatisfied)}"
                if unsatisfied
                else "unknown reason"
            )
            raise ValueError(
                f"Claim precondition failed: node '{node_id}' is not in "
                f"frontier ({reason})"
            )
    elif current_status == "assigned":
        # Picking up assigned task: só permitido para o Worker designado
        if current_agent != worker_id:
            raise ValueError(
                f"Claim precondition failed: node '{node_id}' is assigned to "
                f"agent '{current_agent}', cannot be claimed by '{worker_id}'"
            )
    else:
        raise ValueError(
            f"Claim precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'pending' or 'assigned'"
        )

    # Precondition: agent(v) ∈ {None, w}
    if current_agent is not None and current_agent != worker_id:
        raise ValueError(
            f"Claim precondition failed: node '{node_id}' is already assigned "
            f"to agent '{current_agent}', cannot be claimed by '{worker_id}'"
        )

    graph.update_node_status(node_id, "in_progress", agent=worker_id)
    if current_status == "pending":
        node["assigned_at_round"] = graph.round
    node["rounds_inactive"] = 0
    graph.add_history_entry("Claim", node_id, worker_id, {
        "from_status": current_status,
        "to_status": "in_progress",
        "from_agent": current_agent,
        "to_agent": worker_id,
        "note": "work-stealing" if current_agent is None else "assigned task started",
    })

    return {"type": "claim_task", "id": node_id, "worker": worker_id}


def _apply_complete(
    graph: "CoordinationGraph",
    node_id: str,
    worker_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Complete diretamente no CoordinationGraph."""
    node = graph.find_node(node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    if current_status != "in_progress":
        raise ValueError(
            f"Complete precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'in_progress'"
        )

    if current_agent != worker_id:
        raise ValueError(
            f"Complete precondition failed: node '{node_id}' is assigned to "
            f"agent '{current_agent}', not '{worker_id}'"
        )

    graph.update_node_status(node_id, "done")
    node["completed_at_round"] = graph.round
    node["rounds_inactive"] = 0
    graph.add_history_entry("Complete", node_id, worker_id, {
        "from_status": current_status,
        "to_status": "done",
        "agent": worker_id,
        "note": "completed by Worker",
    })

    return {"type": "complete_task", "id": node_id, "worker": worker_id}


def _apply_discover(
    graph: "CoordinationGraph",
    node_id: str,
    worker_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Discover (Worker proposal) diretamente no CoordinationGraph."""
    if graph.has_node(node_id):
        raise ValueError(
            f"Discover precondition failed: node '{node_id}' already exists"
        )

    title = kwargs.get("title", node_id)
    deps = kwargs.get("deps") or kwargs.get("dependencies") or []
    description = kwargs.get("description", title)

    # Valida dependências
    for dep in deps:
        if not graph.has_node(dep):
            raise ValueError(
                f"Discover precondition failed: dependency '{dep}' not found"
            )

    # Verifica aciclicidade antes de adicionar
    candidate_nodes = list(graph.nodes)
    candidate_edges = list(graph.edges)
    candidate_nodes.append({
        "id": node_id,
        "agent": None,
        "status": "pending",
        "deps": list(deps),
        "description": description,
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": graph.round,
        "assigned_at_round": None,
        "completed_at_round": None,
    })
    for dep in deps:
        candidate_edges.append({"from": dep, "to": node_id})

    candidate = {"nodes": candidate_nodes, "edges": candidate_edges}
    if not _is_acyclic(candidate):
        raise ValueError(
            f"Discover precondition failed: adding node '{node_id}' with "
            f"deps {deps} would create a cycle"
        )

    node_data = {
        "id": node_id,
        "agent": None,
        "status": "pending",
        "deps": list(deps),
        "description": description,
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": graph.round,
        "assigned_at_round": None,
        "completed_at_round": None,
    }

    graph.add_node(node_data)
    graph.add_history_entry("Discover", node_id, worker_id, {
        "description": description,
        "deps": list(deps),
        "proposed_by": worker_id,
        "note": "Worker proposal — Lead must evaluate and confirm merge",
    })

    return {
        "type": "discover_task",
        "id": node_id,
        "title": title,
        "deps": list(deps),
        "description": description,
        "proposed_by": worker_id,
        "note": "Worker proposal",
    }


# ===========================================================================
# Main — testes manuais
# ===========================================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("worker_operators.py — Testes dos 3 operadores do Worker")
    print("=" * 60)

    # Constrói G_0 com algumas tasks (graph-schema.md, Seção 5.3)
    g0: dict[str, Any] = {
        "metadata": {
            "feature_id": "001",
            "round": 1,
            "max_rounds": 40,
            "heartbeat_threshold": 4,
            "workers": ["Dev1", "Dev2"],
            "lead": "Lead",
            "created_at": "2026-06-19T00:00:00Z",
        },
        "nodes": [
            {
                "id": "T001",
                "agent": None,
                "status": "pending",
                "deps": [],
                "description": "Setup project structure",
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
                "deps": ["T001"],
                "description": "Implement core logic",
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
                "deps": [],
                "description": "Add test suite",
                "output": None,
                "rounds_inactive": 0,
                "created_at_round": 0,
                "assigned_at_round": None,
                "completed_at_round": None,
            },
            {
                "id": "T004",
                "agent": "Dev1",
                "status": "assigned",
                "deps": [],
                "description": "Assigned task for Dev1",
                "output": None,
                "rounds_inactive": 0,
                "created_at_round": 0,
                "assigned_at_round": 1,
                "completed_at_round": None,
            },
        ],
        "edges": [
            {"from": "T001", "to": "T002"},
        ],
        "history": [],
    }

    errors = 0

    # ------------------------------------------------------------------
    # Teste 1: Claim — Work-stealing do frontier
    # ------------------------------------------------------------------
    print("\n--- Teste 1: Claim (Work-stealing) ---")

    # Cenário: T001 e T003 estão no frontier (pending, sem deps não satisfeitas)
    # T002 NÃO está no frontier (depende de T001, que não está done)
    # T004 está assigned ao Dev1 — pode ser claimed pelo Dev1 mas não por Dev2

    # Claim 1a: Dev1 claim T001 do frontier (pending, unassigned)
    g, action = claim(g0, "T001", "Dev1")
    node = _find_node(g, "T001")
    assert node["status"] == "in_progress", f"Expected in_progress, got {node['status']}"
    assert node["agent"] == "Dev1", f"Expected Dev1, got {node['agent']}"
    assert action["type"] == "claim_task"
    print(f"  ✓ Claim T001 (pending→in_progress) por Dev1: {action}")

    # Claim 1b: Dev1 claim T004 (assigned, same worker)
    g2, action = claim(g0, "T004", "Dev1")
    node = _find_node(g2, "T004")
    assert node["status"] == "in_progress", f"Expected in_progress, got {node['status']}"
    assert node["agent"] == "Dev1"
    print(f"  ✓ Claim T004 (assigned→in_progress) por Dev1 (same worker): {action}")

    # Claim 1c: Dev2 tenta claim T004 (assigned a outro worker) → deve falhar
    try:
        claim(g0, "T004", "Dev2")
        print("  ✗ Should have raised ValueError — assigned to different worker")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Claim T004 por Dev2 rejeitado (outro agente): {str(e)[:80]}...")

    # Claim 1d: Dev1 tenta claim T002 (não está no frontier — depende de T001 pending)
    try:
        claim(g0, "T002", "Dev1")
        print("  ✗ Should have raised ValueError — not in frontier")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Claim T002 rejeitado (não está no frontier): {str(e)[:80]}...")

    # Verifica histórico
    assert len(g["history"]) == 1, f"Expected 1 history entry, got {len(g['history'])}"
    print(f"  ✓ History has {len(g['history'])} entry (Claim)")

    # ------------------------------------------------------------------
    # Teste 2: Complete — Worker marca task como done
    # ------------------------------------------------------------------
    print("\n--- Teste 2: Complete ---")

    # Prepara: T001 in_progress pelo Dev1
    g_claim, _ = claim(g0, "T001", "Dev1")

    # Complete 2a: Dev1 completa T001 (in_progress, mesmo agente)
    g, action = complete(g_claim, "T001", "Dev1")
    node = _find_node(g, "T001")
    assert node["status"] == "done", f"Expected done, got {node['status']}"
    assert node["agent"] == "Dev1", "Agent should be preserved"
    assert node["completed_at_round"] == 1
    assert action["type"] == "complete_task"
    print(f"  ✓ Complete T001 por Dev1: {action}")

    # Complete 2b: Dev2 tenta completar T001 (agente errado) → deve falhar
    g_claim2, _ = claim(g0, "T003", "Dev1")  # T003 in_progress por Dev1
    try:
        complete(g_claim2, "T003", "Dev2")
        print("  ✗ Should have raised ValueError — wrong agent")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Complete T003 por Dev2 rejeitado (agente errado): {str(e)[:80]}...")

    # Complete 2c: tenta completar nó pending → deve falhar
    try:
        complete(g0, "T003", "Dev1")
        print("  ✗ Should have raised ValueError — not in_progress")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Complete T003 (pending) rejeitado: {str(e)[:80]}...")

    # Complete 2d: tenta completar nó done (idempotente? Não, deve falhar)
    try:
        complete(g, "T001", "Dev1")  # T001 já está done
        print("  ✗ Should have raised ValueError — already done")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Complete T001 (já done) rejeitado: {str(e)[:80]}...")

    # Verifica histórico
    assert len(g["history"]) == 2, f"Expected 2 history entries, got {len(g['history'])}"
    print(f"  ✓ History has {len(g['history'])} entries (Claim + Complete)")

    # ------------------------------------------------------------------
    # Teste 3: Discover — Worker propõe nova task
    # ------------------------------------------------------------------
    print("\n--- Teste 3: Discover (Worker proposal) ---")

    # Discover 3a: Worker propõe nova task sem dependências
    g, action = discover(g0, "T005", "Add documentation", deps=[],
                         description="Write docs for API", worker_id="Dev1")
    assert _has_node(g, "T005"), "T005 should exist"
    node = _find_node(g, "T005")
    assert node["status"] == "pending", "T005 should be pending"
    assert node["agent"] is None, "T005 should be unassigned"
    assert node["deps"] == []
    assert action["type"] == "discover_task"
    assert action["proposed_by"] == "Dev1"
    print(f"  ✓ Discover T005 (sem deps) por Dev1: {action}")

    # Discover 3b: Worker propõe task com dependência existente
    g, action = discover(g, "T006", "Write integration tests", deps=["T005"],
                         description="Integration tests", worker_id="Dev1")
    assert _has_node(g, "T006"), "T006 should exist"
    node = _find_node(g, "T006")
    assert node["deps"] == ["T005"]
    assert len(g["edges"]) == 2, f"Expected 2 edges, got {len(g['edges'])}"
    print(f"  ✓ Discover T006 (depende de T005) por Dev1: {action}")

    # Discover 3c: nó duplicado → deve falhar
    try:
        discover(g, "T005", "Duplicate", deps=[], worker_id="Dev2")
        print("  ✗ Should have raised ValueError for duplicate node")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Duplicate node rejeitado: {e}")

    # Discover 3d: dependência inexistente → deve falhar
    try:
        discover(g, "T999", "Bad deps", deps=["NONEXISTENT"], worker_id="Dev1")
        print("  ✗ Should have raised ValueError for missing dep")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Missing dependency rejeitado: {e}")

    # Discover 3e: aciclicidade preservada
    assert _is_acyclic(g), "Graph must remain acyclic"
    print(f"  ✓ Graph is acyclic ({len(g['nodes'])} nodes, {len(g['edges'])} edges)")

    # Verifica histórico
    assert len(g["history"]) == 2, f"Expected 2 history entries, got {len(g['history'])}"
    print(f"  ✓ History has {len(g['history'])} entries (2x Discover proposals)")

    # ------------------------------------------------------------------
    # Teste 4: Integração Claim + Complete (workflow completo)
    # ------------------------------------------------------------------
    print("\n--- Teste 4: Workflow Claim → Complete ---")

    g4 = copy.deepcopy(g0)
    # Dev1 claim T001
    g4, _ = claim(g4, "T001", "Dev1")
    assert _find_node(g4, "T001")["status"] == "in_progress"
    assert _find_node(g4, "T001")["agent"] == "Dev1"

    # Agora simula que T001 foi completado, desbloqueando T002
    g4["nodes"][0]["status"] = "done"  # T001
    g4["nodes"][0]["agent"] = "Dev1"

    # Dev2 claim T002 (agora deve estar no frontier porque T001 está done)
    g4, _ = claim(g4, "T002", "Dev2")
    assert _find_node(g4, "T002")["status"] == "in_progress"
    assert _find_node(g4, "T002")["agent"] == "Dev2"

    # Dev2 completa T002
    g4, _ = complete(g4, "T002", "Dev2")
    assert _find_node(g4, "T002")["status"] == "done"
    print(f"  ✓ Workflow completo: Claim T001 → done → Claim T002 → Complete T002")

    # ------------------------------------------------------------------
    # Teste 5: Testes com CoordinationGraph (se disponível)
    # ------------------------------------------------------------------
    print("\n--- Teste 5: CoordinationGraph integration ---")

    try:
        from orchestrator import CoordinationGraph

        cg = CoordinationGraph(
            feature_id="001",
            lead="Lead",
            workers=["Dev1", "Dev2"],
        )

        # Discover via apply_to_graph (Worker proposal)
        action = apply_to_graph(cg, "T001", "Discover",
                                title="Test task", deps=[],
                                worker_id="Dev1")
        assert cg.has_node("T001"), "T001 should exist in CoordinationGraph"
        print(f"  ✓ Discover via CoordinationGraph: {action}")

        # Claim via apply_to_graph
        action = apply_to_graph(cg, "T001", "Claim", worker_id="Dev1")
        node = cg.find_node("T001")
        assert node["status"] == "in_progress"
        assert node["agent"] == "Dev1"
        print(f"  ✓ Claim via CoordinationGraph: {action}")

        # Complete via apply_to_graph
        action = apply_to_graph(cg, "T001", "Complete", worker_id="Dev1")
        node = cg.find_node("T001")
        assert node["status"] == "done"
        print(f"  ✓ Complete via CoordinationGraph: {action}")

        print("  ✓ Todos os testes de integração com CoordinationGraph passaram!")

    except ImportError:
        print("  ℹ orchestrator.CoordinationGraph não disponível — pulando testes de integração")
    except Exception as e:
        import traceback
        print(f"  ✗ Erro nos testes de integração: {e}")
        traceback.print_exc()
        errors += 1

    # ------------------------------------------------------------------
    # Resumo
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    if errors == 0:
        print("✅ Todos os testes passaram!")
    else:
        print(f"❌ {errors} teste(s) falharam!")
    print("=" * 60)
    sys.exit(0 if errors == 0 else 1)
