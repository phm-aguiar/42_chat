#!/usr/bin/env python3
"""
heartbeat.py — Heartbeat Monitoring + Straggler Detection (T005)
================================================================

Implementa o mecanismo de heartbeat do protocolo LATTE conforme definido
no paper "Improving the Efficiency of Language Agent Teams with Adaptive
Task Graphs" (Mieczkowski et al., 2026, arXiv:2605.06320).

Lógica central (Algorithm A4.5, Passo 1):
  - Cada Worker tem um contador de rounds consecutivos sem emitir ação.
  - A cada round, se o Worker emitiu ação (Claim, Complete, Discover),
    o contador é resetado para 0; caso contrário, é incrementado.
  - Se o contador atinge o threshold H (default 4), o Worker é flagged
    como straggler e o Lead é notificado no próximo round.

Integração com o Orchestrator:
  → Importado por orchestrator.py no método _heartbeat_check().
  → Função principal: check_heartbeat(graph, inactivity_counters, H=4).
  → Retorna lista de stragglers com worker_id, node_id, inactive_rounds.

Referências:
  - latte-protocol.md, Seção 6 (Heartbeat Monitoring)
  - graph-schema.md, Seção 1.2 (campos rounds_inactive nos nós)
  - plan.md, ADR-001 (rounds como unidade de heartbeat)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Operadores emitidos por Workers que resetam o heartbeat
# (Claim, Complete, Discover — Seção 3.2 do latte-protocol.md)
WORKER_ACTION_OPERATORS: frozenset[str] = frozenset({
    "Claim",
    "Complete",
    "Discover",
})

# Status de nós que indicam que o Worker ainda está ativo naquela task
# (assigned = recebeu mas ainda não começou; in_progress = trabalhando)
ACTIVE_NODE_STATUSES: frozenset[str] = frozenset({
    "assigned",
    "in_progress",
})


def check_heartbeat(
    graph: Any,
    inactivity_counters: dict[str, int],
    H: int = 4,
) -> list[dict[str, Any]]:
    """
    Verifica heartbeat de todos os Workers e detecta stragglers.

    Para cada Worker registrado no grafo:
      1. Verifica se emitiu ação (Claim, Complete, Discover) neste round.
      2. Se sim: reseta o contador de inatividade para 0.
      3. Se não: incrementa o contador de inatividade.
      4. Se contador >= H: flag como straggler, coleta os nós ativos.

    Os contadores são modificados **in-place** no dicionário recebido.

    Args:
        graph: CoordinationGraph com acesso a:
               - .workers → list[str]
               - .round → int
               - .history → list[dict] (entradas com round, agent, operator)
               - .nodes → list[dict] (nós com id, agent, status)
        inactivity_counters: dict[worker_id → rounds_inactive].
                             Modificado in-place.
        H: Threshold de rounds consecutivos sem ação para flag como
           straggler (default 4, conforme paper LATTE).

    Returns:
        Lista de stragglers detectados neste round. Cada entrada é um dict:
            {
                "worker_id": str,       # ID do Worker straggler
                "node_id": str,         # ID do nó ativo atribuído ao Worker
                "inactive_rounds": int, # Rounds consecutivos sem ação
            }

        Se não houver stragglers, retorna lista vazia.

    Raises:
        ValueError: Se H <= 0 (threshold deve ser positivo).

    Example:
        >>> counters = {"Dev1": 0, "Dev2": 3}
        >>> result = check_heartbeat(graph, counters, H=4)
        >>> # Se Dev2 não agiu neste round, counters["Dev2"] → 4
        >>> # e result conterá os nós stragglers de Dev2
    """
    if H <= 0:
        raise ValueError(
            f"Heartbeat threshold H must be positive, got {H}"
        )

    current_round: int = graph.round
    workers: list[str] = list(graph.workers)
    stragglers: list[dict[str, Any]] = []

    for worker_id in workers:
        # ----------------------------------------------------------------
        # Passo 1: Verifica se o Worker emitiu ação neste round
        # ----------------------------------------------------------------
        acted_this_round = _worker_acted_in_round(
            graph=graph,
            worker_id=worker_id,
            round_num=current_round,
        )

        # ----------------------------------------------------------------
        # Passo 2-3: Atualiza contador de inatividade
        # ----------------------------------------------------------------
        if acted_this_round:
            _reset_counter(inactivity_counters, worker_id)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "  ♡ Worker %s agiu no round %d → contador resetado",
                    worker_id, current_round,
                )
        else:
            _increment_counter(inactivity_counters, worker_id)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "  ♡ Worker %s inativo no round %d → contador=%d",
                    worker_id, current_round,
                    inactivity_counters.get(worker_id, 0),
                )

        # ----------------------------------------------------------------
        # Passo 4: Verifica threshold de straggler
        # ----------------------------------------------------------------
        inactive_rounds = inactivity_counters.get(worker_id, 0)
        if inactive_rounds >= H:
            straggler_nodes = _find_active_nodes_for_worker(
                graph=graph,
                worker_id=worker_id,
            )
            for node_id in straggler_nodes:
                stragglers.append({
                    "worker_id": worker_id,
                    "node_id": node_id,
                    "inactive_rounds": inactive_rounds,
                })
            if logger.isEnabledFor(logging.WARNING):
                logger.warning(
                    "  ⚠ Straggler detectado: Worker %s — "
                    "%d rounds inativo(s), nós ativos=%s",
                    worker_id, inactive_rounds, straggler_nodes,
                )

    return stragglers


def reset_heartbeat(
    inactivity_counters: dict[str, int],
    worker_id: str,
) -> None:
    """
    Reseta o contador de inatividade de um Worker específico.

    Útil para quando o Lead executa Release/Close em nós de um
    Worker straggler e quer dar um "clean slate" ao Worker.

    Args:
        inactivity_counters: Dicionário de contadores (modificado in-place).
        worker_id: ID do Worker cujo contador será resetado.
    """
    _reset_counter(inactivity_counters, worker_id)


# =========================================================================
# Funções auxiliares internas
# =========================================================================


def _worker_acted_in_round(
    graph: Any,
    worker_id: str,
    round_num: int,
) -> bool:
    """
    Verifica se um Worker emitiu pelo menos uma ação relevante
    (Claim, Complete, Discover) no round especificado.

    Args:
        graph: CoordinationGraph com acesso a .history.
        worker_id: ID do Worker a verificar.
        round_num: Número do round.

    Returns:
        True se o Worker agiu neste round, False caso contrário.
    """
    for entry in graph.history:
        if (
            entry.get("round") == round_num
            and entry.get("agent") == worker_id
            and entry.get("operator") in WORKER_ACTION_OPERATORS
        ):
            return True
    return False


def _find_active_nodes_for_worker(
    graph: Any,
    worker_id: str,
) -> list[str]:
    """
    Encontra os nós atualmente atribuídos a um Worker que estão
    em status ativo (assigned ou in_progress).

    Estes são os nós que o Worker deveria estar trabalhando e
    que justificam a flag de straggler.

    Args:
        graph: CoordinationGraph com acesso a .nodes.
        worker_id: ID do Worker.

    Returns:
        Lista de node IDs ativos atribuídos ao Worker.
    """
    active_nodes: list[str] = []
    for node in graph.nodes:
        if (
            node.get("agent") == worker_id
            and node.get("status") in ACTIVE_NODE_STATUSES
        ):
            active_nodes.append(node["id"])
    return active_nodes


def _reset_counter(
    counters: dict[str, int],
    worker_id: str,
) -> None:
    """Reseta o contador de inatividade de um Worker para 0 (in-place)."""
    counters[worker_id] = 0


def _increment_counter(
    counters: dict[str, int],
    worker_id: str,
) -> None:
    """Incrementa o contador de inatividade de um Worker (in-place)."""
    counters[worker_id] = counters.get(worker_id, 0) + 1


# =========================================================================
# Testes rápidos (executáveis com python -m pytest ou diretamente)
# =========================================================================

if __name__ == "__main__":
    """
    Teste manual do módulo heartbeat.py.

    Simula um CoordinationGraph mínimo e exercita check_heartbeat.
    """
    import sys
    from dataclasses import dataclass, field
    from pathlib import Path

    # Adiciona o diretório pai ao path para import relativo
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Mock mínimo de CoordinationGraph para teste standalone
    # ------------------------------------------------------------------

    @dataclass
    class MockGraph:
        """Simula a interface mínima de CoordinationGraph."""
        workers: list[str] = field(default_factory=lambda: ["Dev1", "Dev2"])
        round: int = 1
        history: list[dict] = field(default_factory=list)
        nodes: list[dict] = field(default_factory=list)

    print("=" * 60)
    print("heartbeat.py — Testes de unidade (T005)")
    print("=" * 60)

    # --- Teste 1: Worker age → contador reseta ---
    print("\n[Teste 1] Worker age → contador deve resetar")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        round=1,
        history=[
            {"round": 1, "agent": "Dev1", "operator": "Claim",
             "node_id": "T001"},
        ],
    )
    counters: dict[str, int] = {"Dev1": 3, "Dev2": 0}
    result = check_heartbeat(graph, counters, H=4)
    assert counters["Dev1"] == 0, f"Esperado 0, obtido {counters['Dev1']}"
    assert counters["Dev2"] == 1, f"Esperado 1, obtido {counters['Dev2']}"
    assert result == [], f"Esperado [], obtido {result}"
    print("  ✓ PASS: Dev1 resetado, Dev2 incrementado, sem stragglers")

    # --- Teste 2: Worker inativo atinge threshold → straggler ---
    print("\n[Teste 2] Worker inativo atinge H=4 → straggler detectado")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        round=4,
        history=[],  # Nenhuma ação neste round
        nodes=[
            {"id": "T001", "agent": "Dev2", "status": "in_progress",
             "deps": []},
        ],
    )
    counters = {"Dev1": 0, "Dev2": 3}  # Dev2 já está em 3
    result = check_heartbeat(graph, counters, H=4)
    assert counters["Dev2"] == 4, f"Esperado 4, obtido {counters['Dev2']}"
    assert len(result) == 1, f"Esperado 1 straggler, obtido {len(result)}"
    assert result[0]["worker_id"] == "Dev2"
    assert result[0]["node_id"] == "T001"
    assert result[0]["inactive_rounds"] == 4
    print(f"  ✓ PASS: {result}")

    # --- Teste 3: Múltiplos nós ativos para o mesmo Worker ---
    print("\n[Teste 3] Worker straggler com múltiplos nós ativos")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        round=5,
        history=[],
        nodes=[
            {"id": "T001", "agent": "Dev1", "status": "assigned", "deps": []},
            {"id": "T002", "agent": "Dev1", "status": "in_progress",
             "deps": ["T001"]},
        ],
    )
    counters = {"Dev1": 4, "Dev2": 0}
    result = check_heartbeat(graph, counters, H=4)
    assert len(result) == 2, f"Esperado 2 nós straggler, obtido {len(result)}"
    node_ids = {s["node_id"] for s in result}
    assert node_ids == {"T001", "T002"}, f"Esperado T001+T002, obtido {node_ids}"
    print(f"  ✓ PASS: {result}")

    # --- Teste 4: Worker sem nós ativos → straggler sem node_id? ---
    print("\n[Teste 4] Worker straggler sem nós ativos → sem entries")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        round=5,
        history=[],
        nodes=[
            # Dev1 não tem nenhum nó ativo (todos done/verified)
            {"id": "T001", "agent": "Dev1", "status": "done", "deps": []},
        ],
    )
    counters = {"Dev1": 4, "Dev2": 0}
    result = check_heartbeat(graph, counters, H=4)
    assert result == [], (
        f"Worker sem nós ativos não deve gerar straggler, obtido {result}"
    )
    print("  ✓ PASS: sem nós ativos → sem straggler entries")

    # --- Teste 5: reset_heartbeat ---
    print("\n[Teste 5] reset_heartbeat")
    counters = {"Dev1": 5, "Dev2": 2}
    reset_heartbeat(counters, "Dev1")
    assert counters["Dev1"] == 0
    assert counters["Dev2"] == 2
    print("  ✓ PASS: Dev1 resetado, Dev2 preservado")

    # --- Teste 6: H inválido ---
    print("\n[Teste 6] H <= 0 deve levantar ValueError")
    graph = MockGraph()
    counters = {"Dev1": 0}
    try:
        check_heartbeat(graph, counters, H=0)
        assert False, "Deveria ter levantado ValueError"
    except ValueError as e:
        print(f"  ✓ PASS: ValueError → {e}")

    print("\n" + "=" * 60)
    print("Todos os testes passaram ✓")
    print("=" * 60)
