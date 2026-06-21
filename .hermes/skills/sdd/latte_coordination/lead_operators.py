#!/usr/bin/env python3
"""
lead_operators.py — Lead-Only Graph Mutation Operators (T008)
==============================================================

Implementa os 5 operadores de mutação do Coordination Graph exclusivos do
Lead (ℓ), conforme definidos no paper LATTE (Mieczkowski et al., 2026),
Appendix A3, e documentados em latte-protocol.md, Seção 2.

Operadores:
  1. discover(graph, node_id, title, deps)  — Adiciona nova task ao grafo
  2. assign(graph, node_id, worker_id)      — Atribui task pending a um Worker
  3. release(graph, node_id)                — Devolve task travada ao pool
  4. close(graph, node_id)                  — Força done em task concluída
  5. verify(graph, node_id)                 — Spawna task de verificação

Cada operador:
  - É uma função pura que aceita um dict Python ou CoordinationGraph.
  - Valida preconditions e lança exceção (ValueError, KeyError) se violadas.
  - Retorna (graph, action) — o grafo modificado e a ação emitida.
  - O grafo de entrada NÃO é mutado; uma cópia profunda (deep copy) é
    retornada com as modificações aplicadas.

Referências:
  - graph-schema.md: schema canônico do G_t (Seção 5) e máquina de estados
  - latte-protocol.md: definições formais dos operadores (Seção 2)
  - orchestrator.py: CoordinationGraph wrapper e constantes compartilhadas
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Optional, Union

# ---------------------------------------------------------------------------
# Constantes compartilhadas (sincronizadas com orchestrator.py)
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
    if operator == "Assign" and new_status == "assigned":
        if current != "pending":
            raise ValueError(
                f"Assign precondition failed: node '{node_id}' has status "
                f"'{current}', expected 'pending'"
            )
        return

    if operator == "Release" and new_status == "pending":
        if current not in ("assigned", "in_progress"):
            raise ValueError(
                f"Release precondition failed: node '{node_id}' has status "
                f"'{current}', expected 'assigned' or 'in_progress'"
            )
        return

    if operator == "Close" and new_status == "done":
        if current not in ("assigned", "in_progress", "done"):
            raise ValueError(
                f"Close precondition failed: node '{node_id}' has status "
                f"'{current}', expected 'assigned', 'in_progress', or 'done'"
            )
        return

    if operator == "Verify" and new_status == "pending":
        # Verify NÃO altera o nó original; apenas spawna v_ver.
        # A validação do nó original (status = done) é feita no caller.
        return

    # Fallback: validação genérica pela tabela de transições
    if new_status not in VALID_TRANSITIONS.get(current, frozenset()):
        raise ValueError(
            f"Invalid transition: '{current}' → '{new_status}' "
            f"for node '{node_id}' via operator '{operator}'"
        )


# ===========================================================================
# Operador 1: Discover — Adicionar nova task ao grafo
# ===========================================================================

def discover(
    graph: GraphLike,
    node_id: str,
    title: str,
    deps: Optional[list[str]] = None,
    description: Optional[str] = None,
    lead_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Discover(v, deps) — Lead-only.

    Adiciona uma nova subtask ao coordination graph durante a execução.
    É o ÚNICO operador que modifica V_t e E_t.

    Preconditions (latte-protocol.md, Seção 2.2):
      1. v ∉ V_t — o nó não pode já existir no grafo.
      2. deps ⊆ V_t — todas as dependências declaradas devem existir.
      3. A adição preserva a aciclicidade do grafo (DAG).

    Postconditions:
      1. V_t ← V_t ∪ {v}
      2. E_t ← E_t ∪ {(d, v) | d ∈ deps}
      3. λ_t(v) ← (⊥, pending)

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID único da nova subtask.
        title: Título descritivo da task.
        deps: Lista de IDs de nós dos quais esta task depende (default: []).
        description: Descrição detalhada (default: usa title).
        lead_id: ID do Lead que está executando o operador.

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
    lead_id = lead_id or g.get("metadata", {}).get("lead", "lead-1")

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
    }
    _record_in_history(g, "Discover", node_id, lead_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "discover_task",
        "id": node_id,
        "title": title,
        "deps": list(deps),
        "description": description or title,
    }

    return g, action


# ===========================================================================
# Operador 2: Assign — Atribuir task pending a um Worker
# ===========================================================================

def assign(
    graph: GraphLike,
    node_id: str,
    worker_id: str,
    lead_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Assign(v, w) — Lead-only.

    Atribui um nó pending do grafo a um Worker específico.

    Preconditions (latte-protocol.md, Seção 2.3):
      1. status(v) = pending — o nó deve estar disponível para atribuição.
      2. w ∈ W — o Worker designado deve pertencer ao conjunto de Workers.

    Postconditions:
      1. λ_t(v) ← (w, assigned) — rotula o nó com o Worker e status assigned.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó a ser atribuído.
        worker_id: ID do Worker destino.
        lead_id: ID do Lead que está executando o operador.

    Returns:
        Tuple (graph_modificado, ação_emitida).

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se status do nó não é pending, ou worker_id não está
                    na lista de Workers.
    """
    g = _ensure_dict(graph)
    lead_id = lead_id or g.get("metadata", {}).get("lead", "lead-1")

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # --- Precondition 1: status(v) = pending ---
    if current_status != "pending":
        raise ValueError(
            f"Assign precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'pending'"
        )

    # --- Precondition 2: w ∈ W ---
    workers = g.get("metadata", {}).get("workers", [])
    if worker_id not in workers:
        raise ValueError(
            f"Assign precondition failed: worker '{worker_id}' not in "
            f"worker set {workers}"
        )

    # --- Valida transição ---
    _validate_transition(current_status, "assigned", "Assign", node_id)

    # --- Aplica mutação ---
    node["status"] = "assigned"
    node["agent"] = worker_id
    node["assigned_at_round"] = g.get("metadata", {}).get("round", 0)
    node["rounds_inactive"] = 0

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "to_status": "assigned",
        "from_agent": current_agent,
        "to_agent": worker_id,
    }
    _record_in_history(g, "Assign", node_id, lead_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "assign_task",
        "id": node_id,
        "to": worker_id,
    }

    return g, action


# ===========================================================================
# Operador 3: Release — Devolver task travada ao pool
# ===========================================================================

def release(
    graph: GraphLike,
    node_id: str,
    lead_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Release(v) — Lead-only.

    Devolve um nó travado (straggler) para o estado pending, liberando-o
    para reassignment ou Claim por outro Worker.

    Preconditions (latte-protocol.md, Seção 2.6):
      1. status(v) ∈ {assigned, in_progress} — o nó deve estar atribuído
         ou em execução.

    Postconditions:
      1. λ_t(v) ← (⊥, pending) — remove o agente e retorna a pending.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó a ser liberado.
        lead_id: ID do Lead que está executando o operador.

    Returns:
        Tuple (graph_modificado, ação_emitida).

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se status do nó não é assigned nem in_progress.
    """
    g = _ensure_dict(graph)
    lead_id = lead_id or g.get("metadata", {}).get("lead", "lead-1")

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # --- Precondition 1: status(v) ∈ {assigned, in_progress} ---
    if current_status not in ("assigned", "in_progress"):
        raise ValueError(
            f"Release precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'assigned' or 'in_progress'"
        )

    # --- Valida transição ---
    _validate_transition(current_status, "pending", "Release", node_id)

    # --- Aplica mutação ---
    node["status"] = "pending"
    node["agent"] = None
    node["assigned_at_round"] = None
    node["rounds_inactive"] = 0

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "to_status": "pending",
        "from_agent": current_agent,
        "to_agent": None,
    }
    _record_in_history(g, "Release", node_id, lead_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "release_task",
        "id": node_id,
    }

    return g, action


# ===========================================================================
# Operador 4: Close — Forçar done em task concluída mas não sinalizada
# ===========================================================================

def close(
    graph: GraphLike,
    node_id: str,
    lead_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Close(v) — Lead-only.

    Força a conclusão de um nó quando o trabalho foi efetivamente realizado
    (ex: testes passam) mas o Worker esqueceu de emitir Complete ou está
    inativo. Diferente de Release (que devolve para pending), Close assume
    que o trabalho JÁ foi feito.

    Preconditions (latte-protocol.md, Seção 2.7):
      1. status(v) ∈ {assigned, in_progress, done} — o nó deve estar em um
         estado ativo ou já concluído (idempotente).

    Postconditions:
      1. λ_t(v) ← (agent(v), done) — preserva o agente original mas força
         status done.

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó a ser fechado.
        lead_id: ID do Lead que está executando o operador.

    Returns:
        Tuple (graph_modificado, ação_emitida).

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se status do nó não permite Close.
    """
    g = _ensure_dict(graph)
    lead_id = lead_id or g.get("metadata", {}).get("lead", "lead-1")

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    # --- Precondition 1: status(v) ∈ {assigned, in_progress, done} ---
    if current_status not in ("assigned", "in_progress", "done"):
        raise ValueError(
            f"Close precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'assigned', 'in_progress', "
            f"or 'done'"
        )

    # Se já está done, é idempotente — registra mas não altera
    if current_status == "done":
        details = {
            "from_status": "done",
            "to_status": "done",
            "note": "idempotent — node already done",
        }
        _record_in_history(g, "Close", node_id, lead_id, details)
        action = {"type": "close_task", "id": node_id, "already_done": True}
        return g, action

    # --- Valida transição ---
    _validate_transition(current_status, "done", "Close", node_id)

    # --- Aplica mutação ---
    node["status"] = "done"
    # Preserva o agente original (rastreabilidade)
    node["completed_at_round"] = g.get("metadata", {}).get("round", 0)
    node["rounds_inactive"] = 0

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "to_status": "done",
        "agent": current_agent,
        "note": "closed by Lead — work presumed complete",
    }
    _record_in_history(g, "Close", node_id, lead_id, details)

    # --- Constrói ação emitida ---
    action = {
        "type": "close_task",
        "id": node_id,
    }

    return g, action


# ===========================================================================
# Operador 5: Verify — Spawnar task de verificação
# ===========================================================================

def verify(
    graph: GraphLike,
    node_id: str,
    lead_id: Optional[str] = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Operador Verify(v) — Lead-only.

    Spawna uma task de verificação para revisar output de alto risco /
    alta incerteza, inserindo um nó de verificação (v_ver) como dependente
    de v. A task original NÃO é regredida — apenas uma NOVA task é criada.

    Preconditions (latte-protocol.md, Seção 2.8):
      1. status(v) = done — o nó a ser verificado deve estar concluído.
      2. v_ver ∉ V_t — o nó de verificação não pode já existir.

    Postconditions:
      1. V_t ← V_t ∪ {v_ver}
      2. E_t ← E_t ∪ {(v, v_ver)}
      3. λ_t(v_ver) ← (⊥, pending)
      4. λ_t(v) permanece inalterado

    Args:
        graph: Coordination graph atual (dict ou CoordinationGraph).
        node_id: ID do nó done a ser verificado.
        lead_id: ID do Lead que está executando o operador.

    Returns:
        Tuple (graph_modificado, ação_emitida).

    Raises:
        KeyError: Se node_id não existe no grafo.
        ValueError: Se status do nó não é done, ou v_ver já existe.
    """
    g = _ensure_dict(graph)
    lead_id = lead_id or g.get("metadata", {}).get("lead", "lead-1")

    # --- Precondition: nó existe ---
    node = _find_node(g, node_id)
    current_status = node["status"]

    # --- Precondition 1: status(v) = done ---
    if current_status != "done":
        raise ValueError(
            f"Verify precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'done'"
        )

    # --- Gera ID do nó de verificação ---
    verify_node_id = f"{node_id}-verify"

    # --- Precondition 2: v_ver ∉ V_t ---
    if _has_node(g, verify_node_id):
        raise ValueError(
            f"Verify precondition failed: verification node "
            f"'{verify_node_id}' already exists in graph"
        )

    # --- Cria o nó de verificação ---
    current_round = g.get("metadata", {}).get("round", 0)
    description = (
        f"Verify output of {node_id}: check correctness, run additional "
        f"tests, and confirm quality of result. Original task: "
        f"{node.get('description', 'N/A')}"
    )

    verify_node = {
        "id": verify_node_id,
        "agent": None,
        "status": "pending",
        "deps": [node_id],
        "description": description,
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": current_round,
        "assigned_at_round": None,
        "completed_at_round": None,
    }

    # --- Propaga dependência para nós downstream ---
    # Todos os nós que dependem de node_id devem passar a depender também
    # de verify_node_id. Isso garante que nenhuma task downstream execute
    # antes da verificação ser concluída (latte-protocol.md, Seção 2.8).
    downstream_ids: list[str] = []
    for n in g.get("nodes", []):
        if node_id in n.get("deps", []) and n["id"] != verify_node_id:
            n["deps"].append(verify_node_id)
            downstream_ids.append(n["id"])

    # --- Aplica mutações ---
    g.setdefault("nodes", []).append(verify_node)
    g.setdefault("edges", []).append({"from": node_id, "to": verify_node_id})
    for ds_id in downstream_ids:
        g.setdefault("edges", []).append({"from": verify_node_id, "to": ds_id})

    # --- Registra no histórico (I8) ---
    details = {
        "from_status": current_status,
        "verify_node_id": verify_node_id,
        "downstream_updated": downstream_ids,
        "note": "spawned verification task + propagated dep to downstream nodes",
    }
    _record_in_history(g, "Verify", node_id, lead_id, details)

    # Também registra a criação do nó de verificação
    _record_in_history(
        g, "Discover", verify_node_id, lead_id,
        {
            "description": description,
            "deps": [node_id],
            "spawned_by": "Verify",
            "parent_node": node_id,
        },
    )

    # --- Constrói ação emitida ---
    action = {
        "type": "verify_task",
        "id": node_id,
        "verify_node_id": verify_node_id,
        "downstream_updated": downstream_ids,
    }

    return g, action


# ===========================================================================
# Convenience: aplica ação ao CoordinationGraph wrapper
# ===========================================================================

def apply_to_graph(
    graph: "CoordinationGraph",
    node_id: str,
    operator: str,
    lead_id: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Aplica um operador do Lead diretamente a um objeto CoordinationGraph,
    usando seus métodos internos para manter o cache consistente.

    Esta função é um adapter que permite que o orchestrator chame os
    operadores sem precisar converter para dict e depois reconstruir
    o CoordinationGraph.

    Args:
        graph: Objeto CoordinationGraph (do orchestrator.py).
        node_id: ID do nó alvo.
        operator: Nome do operador ("Assign", "Release", "Close", "Verify",
                  "Discover").
        lead_id: ID do Lead (default: graph.lead).
        **kwargs: Argumentos adicionais específicos do operador.

    Returns:
        Ação emitida como dict.

    Raises:
        ValueError: Se preconditions são violadas.
        KeyError: Se node_id não existe.
    """
    operator_map = {
        "Assign": _apply_assign,
        "Release": _apply_release,
        "Close": _apply_close,
        "Verify": _apply_verify,
        "Discover": _apply_discover,
    }

    handler = operator_map.get(operator)
    if handler is None:
        raise ValueError(f"Unknown Lead operator: '{operator}'")

    return handler(graph, node_id, lead_id, **kwargs)


def _apply_assign(
    graph: "CoordinationGraph",
    node_id: str,
    lead_id: Optional[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Assign diretamente no CoordinationGraph."""
    worker_id = kwargs.get("worker_id") or kwargs.get("to")
    if not worker_id:
        raise ValueError("Assign requires 'worker_id' or 'to' parameter")

    lead_id = lead_id or graph.lead

    node = graph.find_node(node_id)
    if node["status"] != "pending":
        raise ValueError(
            f"Assign precondition failed: node '{node_id}' has status "
            f"'{node['status']}', expected 'pending'"
        )
    if worker_id not in graph.workers:
        raise ValueError(
            f"Assign precondition failed: worker '{worker_id}' not in "
            f"worker set {graph.workers}"
        )

    graph.update_node_status(node_id, "assigned", agent=worker_id)
    node["assigned_at_round"] = graph.round
    node["rounds_inactive"] = 0
    graph.add_history_entry("Assign", node_id, lead_id, {
        "from_status": "pending",
        "to_status": "assigned",
        "from_agent": None,
        "to_agent": worker_id,
    })

    return {"type": "assign_task", "id": node_id, "to": worker_id}


def _apply_release(
    graph: "CoordinationGraph",
    node_id: str,
    lead_id: Optional[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Release diretamente no CoordinationGraph."""
    lead_id = lead_id or graph.lead

    node = graph.find_node(node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    if current_status not in ("assigned", "in_progress"):
        raise ValueError(
            f"Release precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'assigned' or 'in_progress'"
        )

    # Release usa set direto porque update_node_status(node, "pending", agent=None)
    # não zera o agente (só seta agent quando não-None).
    node["status"] = "pending"
    node["agent"] = None
    node["assigned_at_round"] = None
    node["rounds_inactive"] = 0
    graph._invalidate_cache()
    graph.add_history_entry("Release", node_id, lead_id, {
        "from_status": current_status,
        "to_status": "pending",
        "from_agent": current_agent,
        "to_agent": None,
    })

    return {"type": "release_task", "id": node_id}


def _apply_close(
    graph: "CoordinationGraph",
    node_id: str,
    lead_id: Optional[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Close diretamente no CoordinationGraph."""
    lead_id = lead_id or graph.lead

    node = graph.find_node(node_id)
    current_status = node["status"]
    current_agent = node.get("agent")

    if current_status not in ("assigned", "in_progress", "done"):
        raise ValueError(
            f"Close precondition failed: node '{node_id}' has status "
            f"'{current_status}', expected 'assigned', 'in_progress', "
            f"or 'done'"
        )

    if current_status == "done":
        graph.add_history_entry("Close", node_id, lead_id, {
            "from_status": "done",
            "to_status": "done",
            "note": "idempotent — node already done",
        })
        return {"type": "close_task", "id": node_id, "already_done": True}

    # Close é um operador especial que permite assigned → done,
    # transição que NÃO está na tabela genérica VALID_TRANSITIONS.
    # Por isso setamos o status diretamente, sem usar update_node_status.
    node["status"] = "done"
    # Preserva o agente original (rastreabilidade)
    node["completed_at_round"] = graph.round
    node["rounds_inactive"] = 0
    graph._invalidate_cache()
    graph.add_history_entry("Close", node_id, lead_id, {
        "from_status": current_status,
        "to_status": "done",
        "agent": current_agent,
        "note": "closed by Lead — work presumed complete",
    })

    return {"type": "close_task", "id": node_id}


def _apply_verify(
    graph: "CoordinationGraph",
    node_id: str,
    lead_id: Optional[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Verify diretamente no CoordinationGraph.

    Feature 005 (ADR-009): Modo determinístico primeiro — executa checks
    estruturais antes de spawnar task de verificação LLM.
    """
    lead_id = lead_id or graph.lead
    verify_mode = getattr(graph, "verify_mode", "deterministic")

    node = graph.find_node(node_id)
    if node["status"] != "done":
        raise ValueError(
            f"Verify precondition failed: node '{node_id}' has status "
            f"'{node['status']}', expected 'done'"
        )

    # Feature 005 (ADR-009): deterministic checks primeiro
    if verify_mode == "deterministic":
        output = node.get("output")
        check_results = _run_deterministic_checks(node_id, output)

        if all(r["passed"] for r in check_results):
            # Todos os checks passaram → verificação determinística aprovada
            # Transita direto pra verified sem spawnar task LLM
            node["status"] = "verified"
            node["verified_at_round"] = graph.round
            graph._invalidate_cache()
            graph.add_history_entry("Verify", node_id, lead_id, {
                "mode": "deterministic",
                "checks": check_results,
                "note": "Deterministic checks passed — LLM verification skipped",
            })
            return {
                "type": "verify_task",
                "id": node_id,
                "mode": "deterministic",
                "checks": check_results,
                "llm_skipped": True,
            }
        else:
            failed = [r for r in check_results if not r["passed"]]
            # Checks falharam → spawna task de verificação LLM (fallback)
            pass  # Continua com o fluxo normal abaixo

    # --- Fluxo normal: spawna v-verify ---
    verify_node_id = f"{node_id}-verify"
    if graph.has_node(verify_node_id):
        raise ValueError(
            f"Verify precondition failed: verification node "
            f"'{verify_node_id}' already exists in graph"
        )

    description = (
        f"Verify output of {node_id}: check correctness, run additional "
        f"tests, and confirm quality of result. Original task: "
        f"{node.get('description', 'N/A')}"
    )

    verify_data = {
        "id": verify_node_id,
        "agent": None,
        "status": "pending",
        "deps": [node_id],
        "description": description,
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": graph.round,
        "assigned_at_round": None,
        "completed_at_round": None,
    }

    # Propaga dependência para nós downstream
    downstream_ids: list[str] = []
    for n in graph.nodes:
        if node_id in n.get("deps", []) and n["id"] != verify_node_id:
            n["deps"].append(verify_node_id)
            downstream_ids.append(n["id"])

    graph.add_node(verify_data)
    # Adiciona arestas: T001 → T001-verify → downstreams
    for ds_id in downstream_ids:
        graph._graph.setdefault("edges", []).append(
            {"from": verify_node_id, "to": ds_id}
        )

    graph.add_history_entry("Verify", node_id, lead_id, {
        "mode": verify_mode,
        "verify_node_id": verify_node_id,
        "downstream_updated": downstream_ids,
        "note": "spawned verification task + propagated dep to downstream nodes",
    })
    graph.add_history_entry("Discover", verify_node_id, lead_id, {
        "description": description,
        "deps": [node_id],
        "spawned_by": "Verify",
        "parent_node": node_id,
    })

    return {
        "type": "verify_task",
        "id": node_id,
        "verify_node_id": verify_node_id,
        "mode": verify_mode,
    }


def _run_deterministic_checks(
    node_id: str,
    output: Optional[str],
) -> list[dict[str, Any]]:
    """
    Feature 005 (ADR-009): Checks determinísticos para verificação de output.

    Cinco checks estruturais que rodam antes de escalar pra LLM:
      1. Output não vazio
      2. Anti-padrão "I will create" / "Let me plan"
      3. Anti-padrão output muito curto (< 20 chars)
      4. Artefato referenciado existe no filesystem
      5. Formato parece válido (não é traceback/erro)

    Args:
        node_id: ID do nó sendo verificado.
        output: Output do nó (pode ser None).

    Returns:
        Lista de dicts com {check, passed, detail}.
    """
    checks: list[dict[str, Any]] = []

    # Check 1: Output não vazio
    if not output or not output.strip():
        checks.append({
            "check": "non_empty_output",
            "passed": False,
            "detail": "Output is empty or None",
        })
        # Se output é vazio, checks restantes são irrelevantes
        return checks
    else:
        checks.append({
            "check": "non_empty_output",
            "passed": True,
            "detail": f"Output has {len(output)} chars",
        })

    # Check 2: Anti-padrão "I will create" / "Let me plan" (sem ação)
    anti_patterns = [
        "I will create", "I will build", "I will implement",
        "Let me plan", "Let me think", "I'll start by",
    ]
    for pattern in anti_patterns:
        if pattern.lower() in output.lower():
            checks.append({
                "check": "no_planning_anti_pattern",
                "passed": False,
                "detail": f"Found anti-pattern: '{pattern}' — output describes intent, not action",
            })
            break
    else:
        checks.append({
            "check": "no_planning_anti_pattern",
            "passed": True,
            "detail": "No planning anti-pattern detected",
        })

    # Check 3: Output muito curto (< 20 chars, provável truncado)
    stripped = output.strip()
    if len(stripped) < 20:
        checks.append({
            "check": "minimum_output_size",
            "passed": False,
            "detail": f"Output too short: {len(stripped)} chars (min 20)",
        })
    else:
        checks.append({
            "check": "minimum_output_size",
            "passed": True,
            "detail": f"Output size: {len(stripped)} chars",
        })

    # Check 4: Anti-padrão de erro/traceback
    error_patterns = ["Traceback (most recent call last)", "Error:", "ERROR:"]
    for pattern in error_patterns:
        if pattern in output:
            checks.append({
                "check": "no_error_traceback",
                "passed": False,
                "detail": f"Found error pattern: '{pattern}'",
            })
            break
    else:
        checks.append({
            "check": "no_error_traceback",
            "passed": True,
            "detail": "No error/traceback detected",
        })

    # Check 5: Artefato referenciado existe (se output referencia path)
    import re
    path_patterns = re.findall(r'(?:created?|written?|saved?|output:?\s+)([/\w.]+(?:\.\w+)?)', output, re.IGNORECASE)
    if path_patterns:
        import os
        for p in path_patterns:
            if os.path.exists(p):
                checks.append({
                    "check": "artifact_exists",
                    "passed": True,
                    "detail": f"Referenced artifact exists: {p}",
                })
                break
        else:
            checks.append({
                "check": "artifact_exists",
                "passed": False,
                "detail": f"Referenced artifact(s) not found on filesystem: {path_patterns}",
            })
    else:
        checks.append({
            "check": "artifact_exists",
            "passed": True,
            "detail": "No filesystem artifact references detected — skipping",
        })

    return checks


def _apply_discover(
    graph: "CoordinationGraph",
    node_id: str,
    lead_id: Optional[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """Aplica Discover diretamente no CoordinationGraph."""
    lead_id = lead_id or graph.lead

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
    # (usa o grafo atual + simulação mental)
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
    graph.add_history_entry("Discover", node_id, lead_id, {
        "description": description,
        "deps": list(deps),
    })

    return {
        "type": "discover_task",
        "id": node_id,
        "title": title,
        "deps": list(deps),
        "description": description,
    }


# ===========================================================================
# Main — testes manuais
# ===========================================================================

if __name__ == "__main__":
    import json
    import sys

    print("=" * 60)
    print("lead_operators.py — Testes dos 5 operadores do Lead")
    print("=" * 60)

    # Constrói G_0 mínimo (graph-schema.md, Seção 5.2)
    g0: dict[str, Any] = {
        "metadata": {
            "feature_id": "001",
            "round": 0,
            "max_rounds": 40,
            "heartbeat_threshold": 4,
            "workers": ["Dev1", "Dev2"],
            "lead": "Lead",
            "created_at": "2026-06-19T00:00:00Z",
        },
        "nodes": [],
        "edges": [],
        "history": [],
    }

    errors = 0

    # ------------------------------------------------------------------
    # Teste 1: Discover — adicionar tasks
    # ------------------------------------------------------------------
    print("\n--- Teste 1: Discover ---")

    g, action = discover(g0, "T001", "Setup project", deps=[],
                         description="Initialize project structure")
    assert _has_node(g, "T001"), "T001 should exist"
    assert g["nodes"][0]["status"] == "pending", "T001 should be pending"
    assert g["nodes"][0]["agent"] is None, "T001 should be unassigned"
    assert action["type"] == "discover_task"
    print(f"  ✓ Discover T001: {action}")

    g, action = discover(g, "T002", "Implement core", deps=["T001"],
                         description="Core logic")
    assert _has_node(g, "T002"), "T002 should exist"
    assert g["nodes"][1]["deps"] == ["T001"], "T002 should depend on T001"
    assert len(g["edges"]) == 1, "Should have 1 edge"
    print(f"  ✓ Discover T002 (depends on T001): {action}")

    g, action = discover(g, "T003", "Add tests", deps=[],
                         description="Test suite")
    assert _has_node(g, "T003"), "T003 should exist"
    print(f"  ✓ Discover T003 (no deps): {action}")

    # Verifica histórico
    assert len(g["history"]) == 3, f"Expected 3 history entries, got {len(g['history'])}"
    print(f"  ✓ History has {len(g['history'])} entries")

    # Testa precondition: nó duplicado
    try:
        discover(g, "T001", "Duplicate", deps=[])
        print("  ✗ Should have raised ValueError for duplicate node")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Duplicate node rejected: {e}")

    # Testa precondition: dependência inexistente
    try:
        discover(g, "T999", "Bad deps", deps=["T999"])
        print("  ✗ Should have raised ValueError for missing dep")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Missing dependency rejected: {e}")

    # Testa aciclicidade: Discover em nó novo sempre preserva DAG.
    # (O novo nó não tem arestas de saída, então não pode criar ciclo.)
    g, action = discover(g, "T004", "Follow-up task", deps=["T002"])
    assert _has_node(g, "T004"), "T004 should exist"
    assert _is_acyclic(g), "Graph must remain acyclic"
    print(f"  ✓ Discover T004 (depends on T002): DAG preserved")

    # Testa aciclicidade explicitamente via _is_acyclic
    assert _is_acyclic(g), "Graph should be acyclic after all Discovers"
    print(f"  ✓ Graph is acyclic ({len(g['nodes'])} nodes, {len(g['edges'])} edges)")

    # ------------------------------------------------------------------
    # Teste 2: Assign — atribuir task a Worker
    # ------------------------------------------------------------------
    print("\n--- Teste 2: Assign ---")

    g, action = assign(g, "T001", "Dev1")
    node = _find_node(g, "T001")
    assert node["status"] == "assigned", f"Expected assigned, got {node['status']}"
    assert node["agent"] == "Dev1", f"Expected Dev1, got {node['agent']}"
    assert action["type"] == "assign_task"
    print(f"  ✓ Assign T001 → Dev1: {action}")

    # Testa precondition: status não é pending
    try:
        assign(g, "T001", "Dev2")
        print("  ✗ Should have raised ValueError for non-pending status")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Non-pending node rejected: {e}")

    # Testa precondition: worker não existe
    try:
        assign(g, "T003", "Dev99")
        print("  ✗ Should have raised ValueError for unknown worker")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Unknown worker rejected: {e}")

    # ------------------------------------------------------------------
    # Teste 3: Release — devolver task ao pool
    # ------------------------------------------------------------------
    print("\n--- Teste 3: Release ---")

    g, action = release(g, "T001")
    node = _find_node(g, "T001")
    assert node["status"] == "pending", f"Expected pending, got {node['status']}"
    assert node["agent"] is None, f"Expected None agent, got {node['agent']}"
    assert action["type"] == "release_task"
    print(f"  ✓ Release T001: {action}")

    # Testa precondition: status não é assigned nem in_progress
    try:
        release(g, "T001")  # Agora está pending
        print("  ✗ Should have raised ValueError for pending status")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Pending node Release rejected: {e}")

    # Testa Release em in_progress
    g, _ = assign(g, "T001", "Dev1")
    _find_node(g, "T001")["status"] = "in_progress"  # Simula Claim
    g, action = release(g, "T001")
    node = _find_node(g, "T001")
    assert node["status"] == "pending", f"Expected pending after releasing in_progress"
    print(f"  ✓ Release T001 (was in_progress): {action}")

    # ------------------------------------------------------------------
    # Teste 4: Close — forçar done
    # ------------------------------------------------------------------
    print("\n--- Teste 4: Close ---")

    # Cenário: T001 assigned → close força done
    g, _ = assign(g, "T001", "Dev1")
    g, action = close(g, "T001")
    node = _find_node(g, "T001")
    assert node["status"] == "done", f"Expected done, got {node['status']}"
    assert node["agent"] == "Dev1", "Agent should be preserved"
    assert action["type"] == "close_task"
    print(f"  ✓ Close T001 (was assigned): {action}")

    # Testa Close idempotente (já está done)
    g, action = close(g, "T001")
    assert action.get("already_done") is True
    print(f"  ✓ Close T001 idempotent: {action}")

    # Testa Close em pending (deve falhar)
    try:
        close(g, "T003")  # T003 está pending
        print("  ✗ Should have raised ValueError for pending status")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Pending node Close rejected: {e}")

    # Testa Close em verified (deve falhar)
    _find_node(g, "T001")["status"] = "verified"
    try:
        close(g, "T001")
        print("  ✗ Should have raised ValueError for verified status")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Verified node Close rejected: {e}")

    # ------------------------------------------------------------------
    # Teste 5: Verify — spawnar verificação
    # ------------------------------------------------------------------
    print("\n--- Teste 5: Verify ---")

    # Coloca T002 como done para testar Verify
    _find_node(g, "T002")["status"] = "done"

    g, action = verify(g, "T002")
    verify_node_id = "T002-verify"
    assert _has_node(g, verify_node_id), f"{verify_node_id} should exist"
    vnode = _find_node(g, verify_node_id)
    assert vnode["status"] == "pending", f"Expected pending, got {vnode['status']}"
    assert vnode["deps"] == ["T002"], f"Expected deps=[T002], got {vnode['deps']}"
    assert vnode["agent"] is None, "Verify node should be unassigned"
    assert action["type"] == "verify_task"
    assert action["verify_node_id"] == verify_node_id
    print(f"  ✓ Verify T002 → {verify_node_id}: {action}")

    # Testa precondition: status não é done
    try:
        verify(g, "T003")  # T003 está pending
        print("  ✗ Should have raised ValueError for non-done status")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Non-done node Verify rejected: {e}")

    # Testa precondition: v_ver já existe
    try:
        verify(g, "T002")  # T002-verify já existe
        print("  ✗ Should have raised ValueError for existing verify node")
        errors += 1
    except ValueError as e:
        print(f"  ✓ Duplicate verify node rejected: {e}")

    # ------------------------------------------------------------------
    # Teste 6: Testes com CoordinationGraph (se disponível)
    # ------------------------------------------------------------------
    print("\n--- Teste 6: CoordinationGraph integration ---")

    try:
        from orchestrator import CoordinationGraph

        cg = CoordinationGraph(
            feature_id="001",
            lead="Lead",
            workers=["Dev1", "Dev2"],
        )

        # Discover via apply_to_graph
        action = apply_to_graph(cg, "T001", "Discover",
                                title="Test task", deps=[])
        assert cg.has_node("T001"), "T001 should exist in CoordinationGraph"
        print(f"  ✓ Discover via CoordinationGraph: {action}")

        # Assign via apply_to_graph
        action = apply_to_graph(cg, "T001", "Assign", to="Dev1")
        node = cg.find_node("T001")
        assert node["status"] == "assigned"
        assert node["agent"] == "Dev1"
        print(f"  ✓ Assign via CoordinationGraph: {action}")

        # Release via apply_to_graph
        action = apply_to_graph(cg, "T001", "Release")
        node = cg.find_node("T001")
        assert node["status"] == "pending"
        assert node["agent"] is None
        print(f"  ✓ Release via CoordinationGraph: {action}")

        # Close via apply_to_graph
        apply_to_graph(cg, "T001", "Assign", to="Dev1")
        action = apply_to_graph(cg, "T001", "Close")
        node = cg.find_node("T001")
        assert node["status"] == "done"
        print(f"  ✓ Close via CoordinationGraph: {action}")

        # Verify via apply_to_graph
        action = apply_to_graph(cg, "T001", "Verify")
        assert cg.has_node("T001-verify")
        print(f"  ✓ Verify via CoordinationGraph: {action}")

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
