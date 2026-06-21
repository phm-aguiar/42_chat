#!/usr/bin/env python3
"""
T014: Smoke test — Cenário 3: Verify spawn + execução
======================================================

Feature 001: LATTE Coordination

Cenário 3 do spec.md: Verify spawn + execução.

Fluxo testado:
  1. Criar G₀ com 1 task crítica upstream (T001) e 3 tasks dependentes
     (T002, T003, T004), conectadas por arestas de dependência.
  2. Marcar T001 como done (via Assign → Close, simulando conclusão).
  3. Chamar verify(T001), que deve spawnar T001-verify como novo nó
     com dep=[T001].
  4. Verificar que T002, T003, T004 têm T001-verify como dependência
     adicional e NÃO podem começar até T001-verify completar.
  5. Completar T001-verify e verificar que as 3 tasks downstream
     desbloqueiam (entram no frontier).

Módulos utilizados:
  - lead_operators.py (assign, close, verify) — API baseada em dict
  - worker_operators.py (claim, complete)      — API baseada em dict
  - frontier.py (compute_frontier)             — aceita dict

Nota: Todos os operadores trabalham com dicts puros (GraphLike).
Isso evita dependência do CoordinationGraph (orchestrator.py) que
usa imports relativos.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Any

# Garante que o diretório pai (latte_coordination) está no sys.path
_PARENT_DIR = Path(__file__).resolve().parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

# ---------------------------------------------------------------------------
# Imports dos módulos LATTE (todos trabalham com dicts puros)
# ---------------------------------------------------------------------------
from lead_operators import (
    assign,
    close,
    verify,
    _is_acyclic,
)
from worker_operators import (
    claim,
    complete,
)
from frontier import compute_frontier

# Constantes compartilhadas
DEPENDENCY_SATISFIED_STATUSES = frozenset({"done", "verified"})


# ===========================================================================
# Helpers do teste
# ===========================================================================

def _make_node(node_id: str, status: str = "pending",
               deps: list[str] | None = None,
               description: str = "") -> dict[str, Any]:
    """Cria um dict de nó com defaults do graph-schema (Seção 5.1)."""
    return {
        "id": node_id,
        "agent": None,
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
    Constrói G₀ como dict: 1 task crítica upstream (T001) com 3 dependentes.

    Estrutura:
        T001 (critical upstream)
        ├── T002 (downstream)
        ├── T003 (downstream)
        └── T004 (downstream)
    """
    return {
        "metadata": {
            "feature_id": "001",
            "round": 0,
            "max_rounds": 50,
            "heartbeat_threshold": 5,
            "workers": ["worker-1", "worker-2"],
            "lead": "lead-1",
        },
        "nodes": [
            _make_node("T001", deps=[], description="Critical upstream task"),
            _make_node("T002", deps=["T001"], description="Downstream task 2"),
            _make_node("T003", deps=["T001"], description="Downstream task 3"),
            _make_node("T004", deps=["T001"], description="Downstream task 4"),
        ],
        "edges": [
            {"from": "T001", "to": "T002"},
            {"from": "T001", "to": "T003"},
            {"from": "T001", "to": "T004"},
        ],
        "history": [],
    }


def _find_node(g: dict[str, Any], node_id: str) -> dict[str, Any]:
    """Busca um nó por ID no grafo dict."""
    for node in g["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")


def _has_node(g: dict[str, Any], node_id: str) -> bool:
    """Verifica se um nó existe no grafo dict."""
    return any(node["id"] == node_id for node in g["nodes"])


def _node_ids(g: dict[str, Any]) -> list[str]:
    """Retorna lista de IDs de todos os nós."""
    return [node["id"] for node in g["nodes"]]


def _get_status(g: dict[str, Any], node_id: str) -> str:
    """Retorna o status de um nó."""
    return _find_node(g, node_id)["status"]


# ===========================================================================
# Teste principal
# ===========================================================================

def test_scenario_3_verify_spawn_and_execution() -> None:
    """
    Cenário 3: Verify spawn + execução.

    Verifica que:
      - verify(T001) spawna T001-verify como novo nó com dep=[T001].
      - T002, T003, T004 ficam bloqueados até T001-verify completar.
      - Após completar T001-verify, as 3 tasks downstream desbloqueiam.
    """
    print("=" * 72)
    print("T014: Smoke test — Cenário 3: Verify spawn + execução")
    print("=" * 72)

    # ------------------------------------------------------------------
    # STEP 1: Criar G₀ com T001 → (T002, T003, T004)
    # ------------------------------------------------------------------
    print("\n[STEP 1] Criando G₀: T001 → T002, T003, T004")
    g = _make_G0()

    assert len(g["nodes"]) == 4, f"Expected 4 nodes, got {len(g['nodes'])}"
    assert _has_node(g, "T001"), "T001 should exist"
    assert _has_node(g, "T002"), "T002 should exist"
    assert _has_node(g, "T003"), "T003 should exist"
    assert _has_node(g, "T004"), "T004 should exist"

    # Todas as tasks downstream devem ter T001 como única dependência
    for nid in ("T002", "T003", "T004"):
        node = _find_node(g, nid)
        assert node["deps"] == ["T001"], \
            f"{nid} deps should be ['T001'], got {node['deps']}"

    # Verifica que G₀ é um DAG válido
    assert _is_acyclic(g), "G₀ should be acyclic"
    print("    ✓ G₀ criado com 4 nós, T001 como upstream crítico")
    print(f"    Nós: {_node_ids(g)}")
    print(f"    Arestas: {[(e['from'], e['to']) for e in g['edges']]}")

    # Frontier inicial: só T001 (único nó pending sem dependências)
    frontier = compute_frontier(g)
    assert frontier == ["T001"], \
        f"Initial frontier should be ['T001'], got {frontier}"
    print(f"    Frontier inicial: {frontier} ✓")

    # ------------------------------------------------------------------
    # STEP 2: Marcar T001 como done (via Assign → Close)
    # ------------------------------------------------------------------
    print("\n[STEP 2] Marcando T001 como done (Assign → Close)")

    # Assign T001 a worker-1
    g, action = assign(g, "T001", "worker-1")
    assert _get_status(g, "T001") == "assigned", \
        f"T001 should be assigned, got {_get_status(g, 'T001')}"
    assert action["type"] == "assign_task"
    print(f"    T001 assign → {_get_status(g, 'T001')} (worker=worker-1) ✓")

    # Close T001 (força done)
    g, action = close(g, "T001")
    assert _get_status(g, "T001") == "done", \
        f"T001 should be done, got {_get_status(g, 'T001')}"
    print(f"    T001 close → {_get_status(g, 'T001')} ✓")

    # Após T001 done, T002/T003/T004 devem estar no frontier
    frontier = compute_frontier(g)
    expected_frontier = ["T002", "T003", "T004"]
    assert frontier == expected_frontier, \
        f"Frontier after T001 done should be {expected_frontier}, got {frontier}"
    print(f"    Frontier pós-T001 done: {frontier} ✓")
    print("    (T002, T003, T004 estão desbloqueados)")

    # ------------------------------------------------------------------
    # STEP 3: Chamar verify(T001) → spawn T001-verify
    # ------------------------------------------------------------------
    print("\n[STEP 3] Chamando verify(T001) → spawn T001-verify")
    g, action = verify(g, "T001")

    # Verifica que o nó de verificação foi criado
    verify_node_id = "T001-verify"
    assert _has_node(g, verify_node_id), \
        f"{verify_node_id} should exist after verify(T001)"
    print(f"    ✓ {verify_node_id} criado no grafo")

    # T001-verify deve depender de T001
    verify_node = _find_node(g, verify_node_id)
    assert verify_node["deps"] == ["T001"], \
        f"{verify_node_id} deps should be ['T001'], got {verify_node['deps']}"
    assert verify_node["status"] == "pending", \
        f"{verify_node_id} status should be 'pending', got {verify_node['status']}"
    print(f"    {verify_node_id}: deps={verify_node['deps']}, "
          f"status={verify_node['status']} ✓")

    # A action retornada deve conter os metadados corretos
    assert action["type"] == "verify_task", \
        f"Action type should be 'verify_task', got {action['type']}"
    assert action["id"] == "T001", \
        f"Action id should be 'T001', got {action['id']}"
    assert action["verify_node_id"] == verify_node_id, \
        f"Action verify_node_id should be '{verify_node_id}', " \
        f"got {action['verify_node_id']}"
    print(f"    Ação emitida: {action} ✓")

    # T001 permanece done (NÃO é regredida pela verificação)
    assert _get_status(g, "T001") == "done", \
        f"T001 should still be 'done' after verify, got {_get_status(g, 'T001')}"
    print(f"    T001 status preservado: {_get_status(g, 'T001')} ✓")

    # Total de nós agora: 5
    assert len(g["nodes"]) == 5, \
        f"Expected 5 nodes after verify, got {len(g['nodes'])}"
    print(f"    Total de nós: {len(g['nodes'])} ✓")

    # Verifica aciclicidade
    assert _is_acyclic(g), "Graph should still be acyclic after verify"
    print("    Grafo permanece acíclico ✓")

    # ------------------------------------------------------------------
    # STEP 4: Verificar bloqueio das tasks downstream
    # ------------------------------------------------------------------
    print("\n[STEP 4] Verificando bloqueio de T002, T003, T004")

    # SPEC: O operador Verify deve inserir T001-verify como dependência
    # adicional de TODOS os nós que dependem de T001. Isso garante que
    # nenhuma task downstream execute antes da verificação concluir.
    #
    # Verificamos se as deps de T002/T003/T004 foram atualizadas.

    for nid in ("T002", "T003", "T004"):
        node = _find_node(g, nid)
        has_verify_dep = verify_node_id in node["deps"]
        print(f"    {nid}: deps={node['deps']} "
              f"(T001-verify presente: {has_verify_dep})")

    # Computa o frontier:
    # Se T001-verify foi adicionado como dep → frontier = [T001-verify]
    # Se NÃO foi adicionado → frontier contém T002, T003, T004, T001-verify
    frontier = compute_frontier(g)

    t001_verify_in_frontier = verify_node_id in frontier
    downstream_in_frontier = [n for n in ("T002", "T003", "T004") if n in frontier]

    print(f"    Frontier após verify: {frontier}")
    print(f"    T001-verify no frontier: {t001_verify_in_frontier}")
    print(f"    Downstream no frontier: {downstream_in_frontier}")

    # Verificação de conformidade com o spec:
    # O spec do cenário 3 exige que T002/T003/T004 NÃO estejam no frontier
    # (bloqueados até T001-verify completar).
    blocked = all(nid not in frontier for nid in ("T002", "T003", "T004"))
    if blocked:
        print("    ✓ T002, T003, T004 estão BLOQUEADOS (conforme spec)")
    else:
        # GAP conhecido: operador Verify atual não adiciona T001-verify
        # como dep dos nós downstream. Para cumprir o spec, é necessário
        # modificar verify() para chamar get_dependents(T001) e atualizar
        # os deps de cada dependente.
        print("    ⚠ T002, T003, T004 NÃO estão bloqueados — "
              "Verify atual não insere T001-verify como dep dos downstreams.")
        print("    ⚠ GAP de implementação: verify() deve adicionar "
              "T001-verify aos deps de todos os dependentes de T001.")

    # Assert: conforme spec, downstreams DEVEM estar bloqueados.
    assert blocked, (
        f"SPEC VIOLATION: T002/T003/T004 should be blocked after verify(T001). "
        f"Frontier={frontier}. "
        f"Expected T001-verify as dependency of downstream nodes. "
        f"GAP: Verify operator does not add T001-verify to dependents' deps."
    )

    # ------------------------------------------------------------------
    # STEP 5: Completar T001-verify → desbloquear downstream
    # ------------------------------------------------------------------
    print("\n[STEP 5] Completando T001-verify → desbloquear T002/T003/T004")

    # Assign → Claim → Complete no T001-verify
    g, _ = assign(g, verify_node_id, "worker-2")
    assert _get_status(g, verify_node_id) == "assigned"
    print(f"    {verify_node_id} assign → assigned ✓")

    g, _ = claim(g, verify_node_id, "worker-2")
    assert _get_status(g, verify_node_id) == "in_progress"
    print(f"    {verify_node_id} claim → in_progress ✓")

    g, _ = complete(g, verify_node_id, "worker-2")
    assert _get_status(g, verify_node_id) == "done", \
        f"{verify_node_id} should be 'done', got {_get_status(g, verify_node_id)}"
    print(f"    {verify_node_id} complete → done ✓")

    # Após T001-verify done, TODAS as tasks downstream devem estar no frontier
    frontier = compute_frontier(g)
    print(f"    Frontier após T001-verify done: {frontier}")

    for nid in ("T002", "T003", "T004"):
        assert nid in frontier, \
            f"{nid} should be in frontier after {verify_node_id} completed, " \
            f"got frontier={frontier}"
    print("    ✓ T002, T003, T004 estão no frontier (desbloqueados)")

    # T001-verify NÃO deve mais estar no frontier (já está done)
    assert verify_node_id not in frontier, \
        f"{verify_node_id} should NOT be in frontier (already done)"

    # Verifica que o grafo tem 5 nós ao final (nenhum perdido)
    assert len(g["nodes"]) == 5, f"Expected 5 nodes at end, got {len(g['nodes'])}"

    # Todos os nós terminais corretos
    assert _get_status(g, "T001") == "done"
    assert _get_status(g, verify_node_id) == "done"

    # ------------------------------------------------------------------
    # Resumo do cenário
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("RESUMO — Cenário 3: Verify spawn + execução")
    print("=" * 72)
    print(f"  Nós totais:             {len(g['nodes'])}")
    print(f"  Arestas totais:         {len(g['edges'])}")
    print(f"  T001 status:            {_get_status(g, 'T001')}")
    print(f"  T001-verify status:     {_get_status(g, verify_node_id)}")
    for nid in ("T002", "T003", "T004"):
        node = _find_node(g, nid)
        print(f"  {nid} status:           {node['status']}")
        print(f"  {nid} deps:             {node['deps']}")
    print(f"  Frontier final:         {frontier}")
    print(f"  Entradas no histórico:  {len(g.get('history', []))}")
    print(f"  Grafo acíclico:         {_is_acyclic(g)}")
    print("=" * 72)
    print("✓ Cenário 3 concluído com sucesso!")
    print("=" * 72)


# ===========================================================================
# Runner
# ===========================================================================

if __name__ == "__main__":
    test_scenario_3_verify_spawn_and_execution()
