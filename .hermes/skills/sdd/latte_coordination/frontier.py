#!/usr/bin/env python3
"""
frontier.py — Frontier Computation (T006)
=========================================

Implementa `compute_frontier(graph) -> list[str]` conforme Definition 2 do
paper LATTE (Mieczkowski et al., 2026, arXiv:2605.06320).

F_t := { v ∈ V_t | status(v) = pending
         ∧ ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }

A função recebe o coordination graph (como dict raw ou objeto CoordinationGraph)
e retorna a lista ordenada de node IDs que estão no frontier — tasks prontas
para execução porque todas as suas dependências foram satisfeitas.

Ordenação:
    - Por número de dependências (menos → mais), priorizando tasks com menos
      blockers para maximizar throughput.
    - Desempate alfabético por node ID (ordenação estável e determinística).

Referências:
    - graph-schema.md, Seção 3 (Definição formal do Frontier)
    - graph-schema.md, Seção 4.3 (compute_frontier)
    - plan.md, ADR-001 (rounds discretos)
"""

from __future__ import annotations

import logging
from typing import Any, Union

logger = logging.getLogger(__name__)

# Status que satisfazem dependência para o frontier (Definition 2 estendida:
# paper usa só "done", mas na prática "verified" também libera dependentes)
DEPENDENCY_SATISFIED_STATUSES: frozenset[str] = frozenset({"done", "verified"})


def compute_frontier(graph: Union[dict, Any]) -> list[str]:
    """
    Calcula o frontier F_t — conjunto de nós pending com todas as
    dependências satisfeitas.

    F_t := { v ∈ V_t | status(v) = pending
             ∧ ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }

    Args:
        graph: Coordination graph atual. Aceita:
               - dict raw (estrutura do graph-schema.md, Seção 5.1)
               - objeto CoordinationGraph (orchestrator.py) — acessado via .raw

    Returns:
        Lista ordenada de node IDs no frontier.
        Ordenação: por número de dependências (menos → mais),
        desempate alfabético.

    Complexity:
        O(|V| + |E|) — uma passada sobre os nós para construir o mapa de
        status e outra para filtrar o frontier.

    Raises:
        TypeError: Se o grafo não tem estrutura reconhecível (nem dict com
                   chave 'nodes', nem atributo 'raw' ou 'nodes').

    Examples:
        >>> g = {"nodes": [{"id": "T1", "status": "pending", "deps": []},
        ...                {"id": "T2", "status": "pending", "deps": ["T1"]}]}
        >>> compute_frontier(g)
        ['T1']

        >>> # Com CoordinationGraph:
        >>> cg = CoordinationGraph(...)
        >>> frontier = compute_frontier(cg)
    """
    # Normalizar acesso ao grafo: aceita CoordinationGraph ou dict raw
    if isinstance(graph, dict):
        nodes: list[dict] = graph["nodes"]
    elif hasattr(graph, "raw"):
        # CoordinationGraph wrapper (orchestrator.py)
        nodes = graph.raw["nodes"]
    elif hasattr(graph, "nodes"):
        # Pode ter propriedade .nodes (CoordinationGraph)
        nodes = graph.nodes
    else:
        raise TypeError(
            f"compute_frontier: objeto recebido não é um coordination graph "
            f"reconhecível. Tipo={type(graph).__name__}. "
            f"Esperado: dict com chave 'nodes' ou CoordinationGraph."
        )

    # Construir mapa de status look-up O(1)
    status_map: dict[str, str] = {node["id"]: node["status"] for node in nodes}

    # Construir índice de nós para ordenação por número de deps
    node_index: dict[str, dict] = {node["id"]: node for node in nodes}

    frontier: list[str] = []

    for node in nodes:
        if node["status"] != "pending":
            continue

        # Verificar que todas as dependências estão satisfeitas
        deps_satisfied = all(
            status_map.get(dep) in DEPENDENCY_SATISFIED_STATUSES
            for dep in node["deps"]
        )

        if deps_satisfied:
            frontier.append(node["id"])

    # Ordenação estável: menos deps primeiro, desempate alfabético
    frontier.sort(key=lambda nid: (
        len(node_index[nid]["deps"]),
        nid,
    ))

    logger.debug("F_t = %s", frontier)
    return frontier
