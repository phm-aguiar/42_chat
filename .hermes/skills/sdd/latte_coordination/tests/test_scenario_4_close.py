#!/usr/bin/env python3
"""
T015: Smoke test — Cenário 4: Close forçado + idempotência
===========================================================

Feature 001: LATTE Coordination.

Cenário 4 do spec.md: Close forçado + idempotência.

Fluxo testado:
  1. Criar G₀ com 1 task (T001) assignada a Dev1.
  2. Simular que Dev1 completou o trabalho mas esqueceu de emitir
     Complete — task ainda em in_progress.
  3. close(T001) força done sem transição inválida.
  4. close(T001) novamente (idempotente) — não quebra, registra
     histórico e retorna already_done=True.

Módulos utilizados:
  - lead_operators.py (assign, close)  — API baseada em dict
  - worker_operators.py (claim)        — API baseada em dict
  - frontier.py (compute_frontier)     — aceita dict

Nota: Todos os operadores trabalham com dicts puros (GraphLike).
Isso evita dependência do CoordinationGraph (orchestrator.py) que
usa imports relativos.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from copy import deepcopy

# Garante que o diretório pai (latte_coordination) está no sys.path
_PARENT_DIR = Path(__file__).resolve().parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

# ---------------------------------------------------------------------------
# Imports dos módulos LATTE (todos trabalham com dicts puros)
# ---------------------------------------------------------------------------
from lead_operators import (  # noqa: E402
    assign,
    close,
    _is_acyclic,
)
from worker_operators import (  # noqa: E402
    claim,
)
from frontier import compute_frontier  # noqa: E402


# ===========================================================================
# Helpers do teste
# ===========================================================================

def _make_node(node_id: str, status: str = "pending",
               agent: str | None = None,
               deps: list[str] | None = None,
               description: str = "") -> dict[str, Any]:
    """Cria um dict de nó com defaults do graph-schema (Seção 5.1)."""
    return {
        "id": node_id,
        "agent": agent,
        "status": status,
        "deps": list(deps or []),
        "description": description or f"Task {node_id}",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    }


def _make_G0() -> dict[str, Any]:
    """
    Constrói G₀ como dict: 1 task T001 já assignada a Dev1.

    Cenário: o Lead assignou T001 a Dev1, Dev1 deu Claim (iniciou o
    trabalho) e completou o código — mas esqueceu de emitir Complete.
    A task está em in_progress com o trabalho JÁ feito.
    """
    return {
        "metadata": {
            "feature_id": "001",
            "round": 5,
            "max_rounds": 50,
            "heartbeat_threshold": 4,
            "workers": ["Dev1", "Dev2"],
            "lead": "Lead-1",
        },
        "nodes": [
            _make_node("T001", status="in_progress", agent="Dev1",
                       description="Task crítica — trabalho concluído, "
                                   "Dev1 esqueceu de emitir Complete"),
        ],
        "edges": [],
        "history": [
            {
                "round": 1,
                "operator": "Assign",
                "node_id": "T001",
                "agent": "Lead-1",
                "details": {
                    "from_status": "pending",
                    "to_status": "assigned",
                    "to_agent": "Dev1",
                },
                "timestamp": "2026-06-19T10:00:00+00:00",
            },
            {
                "round": 1,
                "operator": "Claim",
                "node_id": "T001",
                "agent": "Dev1",
                "details": {
                    "from_status": "assigned",
                    "to_status": "in_progress",
                    "note": "assigned task started",
                },
                "timestamp": "2026-06-19T10:01:00+00:00",
            },
        ],
    }


def _find_node(g: dict[str, Any], node_id: str) -> dict[str, Any]:
    """Busca um nó por ID no grafo dict."""
    for node in g["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")


def _get_status(g: dict[str, Any], node_id: str) -> str:
    """Retorna o status de um nó."""
    return _find_node(g, node_id)["status"]


# ===========================================================================
# Teste principal
# ===========================================================================

def test_scenario_4_forced_close_and_idempotence() -> None:
    """
    Cenário 4: Close forçado + idempotência.

    Verifica que:
      - close(T001) em task in_progress força done sem erro.
      - close(T001) em task já done é idempotente (não quebra).
      - Histórico registra ambas as chamadas corretamente.
      - Agente é preservado após close.
    """
    print("=" * 72)
    print("T015: Smoke test — Cenário 4: Close forçado + idempotência")
    print("=" * 72)

    # ------------------------------------------------------------------
    # STEP 1: Criar G₀ com T001 em in_progress (Dev1 esqueceu Complete)
    # ------------------------------------------------------------------
    print("\n[STEP 1] Criando G₀: T001 in_progress, Dev1 esqueceu Complete")
    g = _make_G0()

    assert len(g["nodes"]) == 1, f"Expected 1 node, got {len(g['nodes'])}"
    assert _get_status(g, "T001") == "in_progress", \
        f"T001 should be in_progress, got {_get_status(g, 'T001')}"
    assert _find_node(g, "T001")["agent"] == "Dev1", \
        "T001 agent should be Dev1"

    initial_history_len = len(g["history"])
    print(f"    ✓ G₀ criado: {len(g['nodes'])} nó, "
          f"status={_get_status(g, 'T001')}, agent=Dev1")
    print(f"    Histórico inicial: {initial_history_len} entradas")
    print(f"    Grafo acíclico: {_is_acyclic(g)} ✓")

    # ------------------------------------------------------------------
    # STEP 2: Simular cenário — Dev1 completou mas não emitiu Complete
    # ------------------------------------------------------------------
    print("\n[STEP 2] Cenário: Dev1 completou o trabalho, mas esqueceu Complete")
    print("    Task T001 está em in_progress com trabalho JÁ concluído.")
    print("    Lead detecta situação e decide executar close(T001).")

    # A task está efetivamente concluída (ex: testes passam, código funciona)
    # mas o status no grafo ainda é in_progress. O close forçado é apropriado.

    # ------------------------------------------------------------------
    # STEP 3: close(T001) — força done
    # ------------------------------------------------------------------
    print("\n[STEP 3] Executando close(T001) para forçar done")

    g, action = close(g, "T001", lead_id="Lead-1")

    # Assert: status deve ser done
    assert _get_status(g, "T001") == "done", \
        f"T001 should be 'done' after close, got {_get_status(g, 'T001')}"

    # Assert: agente Deve ser preservado
    assert _find_node(g, "T001")["agent"] == "Dev1", \
        f"T001 agent should still be Dev1 after close, " \
        f"got {_find_node(g, 'T001')['agent']}"

    # Assert: ação emitida correta
    assert action["type"] == "close_task", \
        f"Action type should be 'close_task', got {action['type']}"
    assert action["id"] == "T001", \
        f"Action id should be 'T001', got {action['id']}"

    # Assert: ação NÃO tem already_done (primeira chamada de close)
    assert not action.get("already_done"), \
        "First close should NOT have already_done=True"

    # Assert: histórico contém a entrada Close
    history_ops = [h["operator"] for h in g["history"]]
    assert "Close" in history_ops, \
        f"History should contain 'Close' operator, got {history_ops}"

    # Conta quantas entradas Close existem (deve ser 1)
    close_entries = [h for h in g["history"] if h["operator"] == "Close"]
    assert len(close_entries) == 1, \
        f"Should have 1 Close entry, got {len(close_entries)}"

    # Verifica detalhes da entrada Close
    close_entry = close_entries[0]
    assert close_entry["node_id"] == "T001"
    assert close_entry["agent"] == "Lead-1"
    assert close_entry["details"]["from_status"] == "in_progress"
    assert close_entry["details"]["to_status"] == "done"
    assert "closed by Lead" in close_entry["details"].get("note", ""), \
        f"Close entry should note 'closed by Lead', got {close_entry['details']}"

    print(f"    ✓ close(T001) executado: status → {_get_status(g, 'T001')}")
    print(f"    ✓ Agente preservado: Dev1")
    print(f"    ✓ Ação emitida: {action}")
    print(f"    ✓ Close registrado no histórico")

    # Guarda estado pós-close para comparação
    g_after_first_close = deepcopy(g)

    # ------------------------------------------------------------------
    # STEP 4: close(T001) novamente — idempotência
    # ------------------------------------------------------------------
    print("\n[STEP 4] Executando close(T001) novamente (idempotência)")

    g2, action2 = close(g, "T001", lead_id="Lead-1")

    # Assert: status CONTINUA done (não muda para outro estado)
    assert _get_status(g2, "T001") == "done", \
        f"T001 should remain 'done' after second close, " \
        f"got {_get_status(g2, 'T001')}"

    # Assert: agente preservado
    assert _find_node(g2, "T001")["agent"] == "Dev1", \
        "T001 agent should still be Dev1 after second close"

    # Assert: ação indica idempotência
    assert action2["type"] == "close_task", \
        f"Action type should be 'close_task', got {action2['type']}"
    assert action2.get("already_done") is True, \
        f"Second close should have already_done=True, got {action2}"

    # Assert: histórico tem DUAS entradas Close
    close_entries_2 = [h for h in g2["history"] if h["operator"] == "Close"]
    assert len(close_entries_2) == 2, \
        f"Should have 2 Close entries (1 real + 1 idempotent), " \
        f"got {len(close_entries_2)}"

    # A segunda entrada deve marcar idempotência
    second_close = close_entries_2[1]
    assert second_close["details"]["from_status"] == "done"
    assert second_close["details"]["to_status"] == "done"
    assert "idempotent" in second_close["details"].get("note", ""), \
        f"Second close should note idempotence, got {second_close['details']}"

    print(f"    ✓ close(T001) idempotente: status mantido → done")
    print(f"    ✓ Agente preservado: Dev1")
    print(f"    ✓ Ação emitida: {action2}")
    print(f"    ✓ 2 entradas Close no histórico (transição + idempotente)")

    # ------------------------------------------------------------------
    # Verificações adicionais: integridade do grafo
    # ------------------------------------------------------------------
    print("\n[STEP 5] Verificações de integridade pós-close duplo")

    # O grafo deve continuar acíclico
    assert _is_acyclic(g2), "Graph should remain acyclic after double close"
    print(f"    ✓ Grafo permanece acíclico")

    # Número de nós: não deve ter mudado (close não adiciona/remove nós)
    assert len(g2["nodes"]) == 1, \
        f"Node count should be 1, got {len(g2['nodes'])}"
    print(f"    ✓ Número de nós preservado: {len(g2['nodes'])}")

    # O nó deve ter completed_at_round preenchido
    t001 = _find_node(g2, "T001")
    assert t001.get("completed_at_round") is not None, \
        "T001 should have completed_at_round set"
    print(f"    ✓ completed_at_round preenchido: {t001['completed_at_round']}")

    # rounds_inactive deve ser zerado
    assert t001.get("rounds_inactive") == 0, \
        f"rounds_inactive should be 0, got {t001.get('rounds_inactive')}"
    print(f"    ✓ rounds_inactive zerado")

    # O histórico total deve conter as operações esperadas
    all_ops = [h["operator"] for h in g2["history"]]
    assert "Assign" in all_ops, "History should contain Assign"
    assert "Claim" in all_ops, "History should contain Claim"
    assert all_ops.count("Close") == 2, \
        f"History should contain exactly 2 Close entries, " \
        f"got {all_ops.count('Close')}"
    print(f"    ✓ Histórico completo: {all_ops}")

    # Total de entradas no histórico: 2 iniciais + 2 Close = 4
    assert len(g2["history"]) == initial_history_len + 2, \
        f"History should have {initial_history_len + 2} entries " \
        f"({initial_history_len} initial + 2 Close), " \
        f"got {len(g2['history'])}"
    print(f"    ✓ Total de entradas no histórico: {len(g2['history'])}")

    # ------------------------------------------------------------------
    # Resumo do cenário
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("RESUMO — Cenário 4: Close forçado + idempotência")
    print("=" * 72)
    print(f"  Nós totais:                {len(g2['nodes'])}")
    print(f"  T001 status inicial:       in_progress")
    print(f"  T001 status pós-close¹:    done (forçado)")
    print(f"  T001 status pós-close²:    done (idempotente)")
    print(f"  T001 agent:                Dev1 (preservado)")
    print(f"  Ação close¹:               {action['type']} (already_done=False)")
    print(f"  Ação close²:               {action2['type']} (already_done=True)")
    print(f"  Entradas Close no hist:    {len(close_entries_2)}")
    print(f"  Histórico total:           {len(g2['history'])} entradas")
    print(f"  Grafo acíclico:            {_is_acyclic(g2)}")
    print("=" * 72)
    print("✓ Cenário 4 concluído com sucesso!")
    print("=" * 72)


# ===========================================================================
# Runner
# ===========================================================================

if __name__ == "__main__":
    test_scenario_4_forced_close_and_idempotence()
