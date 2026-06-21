#!/usr/bin/env python3
"""
T013: Smoke Test — Cenário 2: Straggler Detection + Release
=============================================================

Feature 001: LATTE Coordination.

Cenário 2 do spec.md:
  1. Criar G₀ com 2 tasks paralelas (T001, T002) sem dependências entre si.
  2. Simular que T001 fica stuck — Worker "Dev1" não responde por H=4 rounds.
  3. Verificar que o heartbeat detecta o straggler.
  4. Verificar que Release é chamado.
  5. Verificar que a task é reassinada e eventualmente completada.

Como não temos Workers reais, usamos mocks/substitutes da unittest.mock para
simular o comportamento dos agents. Testamos os componentes de forma integrada:

  - heartbeat.py: check_heartbeat() → detecta straggler
  - lead_operators.py: release() → libera task do straggler
  - lead_operators.py: assign() → reassina task a outro Worker
  - worker_operators.py: claim() / complete() → Worker completa task

Nota: Evitamos importar CoordinationGraph (orchestrator.py) porque ele usa
imports relativos que quebram devido ao hífen no nome do diretório
"latte_coordination". Usamos dicts puros para todas as operações de grafo
(aceitos por lead_operators e worker_operators) e um mock dataclass para
check_heartbeat (que acessa atributos .workers, .round, .history, .nodes).

Arquitetura do teste:
  - Usa dicts Python como G_t (compatível com GraphLike).
  - Injeta histórico simulado para controlar o comportamento do heartbeat.
  - Chama check_heartbeat(), release(), assign(), claim(), complete()
    diretamente com os parâmetros corretos.
  - Verifica estado do grafo após cada passo.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Garante que o diretório pai está no path para imports absolutos
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

# heartbeats.py, frontier.py, lead_operators.py, worker_operators.py
# NÃO usam imports relativos → seguros para import absoluto.
from heartbeat import check_heartbeat, reset_heartbeat  # noqa: E402
from lead_operators import release, assign  # noqa: E402
from worker_operators import claim, complete  # noqa: E402


# =========================================================================
# Mock de CoordinationGraph para check_heartbeat()
# =========================================================================
# check_heartbeat() acessa graph.workers, graph.round, graph.history,
# graph.nodes como ATRIBUTOS (não como chaves de dict). Usamos um
# dataclass simples em vez de importar CoordinationGraph (que depende
# de imports relativos quebrados pelo hífen em "latte_coordination").


@dataclass
class MockGraph:
    """Simula a interface mínima que check_heartbeat espera de um grafo."""
    workers: list[str] = field(default_factory=lambda: ["Dev1", "Dev2"])
    round: int = 1
    history: list[dict] = field(default_factory=list)
    nodes: list[dict] = field(default_factory=list)


# =========================================================================
# Helpers
# =========================================================================


def _make_graph_dict(
    feature_id: str = "001",
    lead: str = "Lead",
    workers: list[str] | None = None,
    round_num: int = 0,
    nodes: list[dict] | None = None,
    history: list[dict] | None = None,
    heartbeat_threshold: int = 4,
    max_rounds: int = 40,
) -> dict:
    """
    Constrói um dict de coordination graph (estrutura graph-schema.md).

    Retorna um dict puro, compatível com lead_operators e worker_operators
    (que aceitam Union[dict, CoordinationGraph]).
    """
    if workers is None:
        workers = ["Dev1", "Dev2"]
    g: dict = {
        "metadata": {
            "feature_id": feature_id,
            "round": round_num,
            "max_rounds": max_rounds,
            "heartbeat_threshold": heartbeat_threshold,
            "workers": list(workers),
            "lead": lead,
        },
        "nodes": list(nodes) if nodes else [],
        "edges": _build_edges(nodes) if nodes else [],
        "history": list(history) if history else [],
    }
    return g


def _build_edges(nodes: list[dict]) -> list[dict]:
    """Constrói a lista de arestas a partir dos deps dos nós."""
    edges: list[dict] = []
    for node in nodes:
        for dep in node.get("deps", []):
            edges.append({"from": dep, "to": node["id"]})
    return edges


def _make_mock_graph(
    graph_dict: dict,
    round_num: int,
) -> MockGraph:
    """
    Converte um dict de grafo em MockGraph para uso com check_heartbeat().

    check_heartbeat() espera atributos .workers, .round, .history, .nodes.
    """
    metadata = graph_dict.get("metadata", {})
    return MockGraph(
        workers=list(metadata.get("workers", ["Dev1", "Dev2"])),
        round=round_num,
        history=list(graph_dict.get("history", [])),
        nodes=list(graph_dict.get("nodes", [])),
    )


def _add_history(graph_dict: dict, entry: dict) -> None:
    """Adiciona uma entrada de histórico ao dict do grafo (in-place)."""
    graph_dict.setdefault("history", []).append(entry)


# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture
def G0_two_parallel_tasks() -> dict:
    """
    Cria G₀ (dict) com 2 tasks paralelas sem dependências entre si.

    Estrutura:
      T001: pending (será assignada a Dev1, ficará stuck)
      T002: pending (será assignada a Dev2, completará normalmente)
    """
    return _make_graph_dict(
        round_num=0,
        nodes=[
            {
                "id": "T001",
                "agent": None,
                "status": "pending",
                "deps": [],
                "description": "Task 001 — vai ficar stuck",
                "output": None,
            },
            {
                "id": "T002",
                "agent": None,
                "status": "pending",
                "deps": [],
                "description": "Task 002 — completa normalmente",
                "output": None,
            },
        ],
    )


# =========================================================================
# Teste principal: Cenário 2 completo (straggler detection + Release)
# =========================================================================


class TestScenario2StragglerDetectionAndRelease:
    """
    Smoke test do cenário 2: detecção de straggler via heartbeat + Release.

    Fluxo:
      Round 1: Lead assigna T001 → Dev1, T002 → Dev2.
               Dev1 e Dev2 dão Claim (inicia execução).
      Round 2: Dev2 completa T002. Dev1 NÃO age.
      Round 3: Dev1 NÃO age.
      Round 4: Dev1 NÃO age.
      Round 5: Dev1 NÃO age (4 rounds consecutivos sem ação → H=4 atingido).
               Heartbeat detecta straggler Dev1 no nó T001.
               Lead executa Release em T001 (volta a pending).
               Lead assigna T001 a Dev2 (agora idle).
               Dev2 dá Claim + Complete em T001.
    """

    # ------------------------------------------------------------------
    # Passo 1: setup G₀ com 2 tasks paralelas
    # ------------------------------------------------------------------

    def test_setup_G0_has_two_parallel_tasks(self, G0_two_parallel_tasks):
        """Passo 1: G₀ deve ter T001 e T002 como pending, sem dependências."""
        g = G0_two_parallel_tasks
        nodes = g["nodes"]
        assert len(nodes) == 2
        assert nodes[0]["id"] == "T001"
        assert nodes[0]["status"] == "pending"
        assert nodes[0]["deps"] == []
        assert nodes[1]["id"] == "T002"
        assert nodes[1]["status"] == "pending"
        assert nodes[1]["deps"] == []
        assert g["metadata"]["workers"] == ["Dev1", "Dev2"]
        assert g["metadata"]["heartbeat_threshold"] == 4

    # ------------------------------------------------------------------
    # Passo 2-3: simular que T001 fica stuck e heartbeat detecta
    # ------------------------------------------------------------------

    def test_heartbeat_detects_straggler_after_H_rounds(self):
        """
        Passo 2-3: Simula Worker Dev1 sem ação por H=4 rounds e verifica
        que heartbeat detecta o straggler.
        """
        # Estado: T001 in_progress com Dev1, T002 done com Dev2.
        # Dev1 não emitiu ação desde round 1.
        graph_dict = _make_graph_dict(
            round_num=5,
            nodes=[
                {
                    "id": "T001",
                    "agent": "Dev1",
                    "status": "in_progress",
                    "deps": [],
                    "description": "Task 001 — stuck",
                    "output": None,
                },
                {
                    "id": "T002",
                    "agent": "Dev2",
                    "status": "done",
                    "deps": [],
                    "description": "Task 002 — done",
                    "output": "resultado T002",
                },
            ],
            history=[
                # Round 1: Assign + Claim para ambas
                {"round": 1, "agent": "Lead", "operator": "Assign",
                 "node_id": "T001"},
                {"round": 1, "agent": "Dev1", "operator": "Claim",
                 "node_id": "T001"},
                {"round": 1, "agent": "Lead", "operator": "Assign",
                 "node_id": "T002"},
                {"round": 1, "agent": "Dev2", "operator": "Claim",
                 "node_id": "T002"},
                # Round 2: Dev2 completa T002
                {"round": 2, "agent": "Dev2", "operator": "Complete",
                 "node_id": "T002"},
                # Rounds 2-5: Dev1 NÃO age (sem entradas no histórico)
            ],
        )

        # Contador de inatividade: Dev1 já está em 4 rounds sem ação
        # (agiu no round 1, depois rounds 2, 3, 4, 5 → 4 rounds inativos)
        counters: dict[str, int] = {"Dev1": 4, "Dev2": 0}

        # Converte para MockGraph (check_heartbeat espera atributos, não dict)
        mock_g = _make_mock_graph(graph_dict, round_num=5)

        # Verifica heartbeat
        stragglers = check_heartbeat(mock_g, counters, H=4)

        # Deve detectar Dev1 como straggler no nó T001
        assert len(stragglers) == 1, (
            f"Esperado 1 straggler, obtido {len(stragglers)}: {stragglers}"
        )
        assert stragglers[0]["worker_id"] == "Dev1"
        assert stragglers[0]["node_id"] == "T001"
        assert stragglers[0]["inactive_rounds"] >= 4

    # ------------------------------------------------------------------
    # Passo 4: verificar que Release é chamado (libera task do straggler)
    # ------------------------------------------------------------------

    def test_release_frees_stuck_task(self):
        """
        Passo 4: Após detecção do straggler, Lead executa Release(v)
        em T001, devolvendo-a ao estado pending.
        """
        # Estado inicial: T001 em in_progress com Dev1
        graph_dict = _make_graph_dict(
            round_num=5,
            nodes=[
                {
                    "id": "T001",
                    "agent": "Dev1",
                    "status": "in_progress",
                    "deps": [],
                    "description": "Task 001 — stuck",
                    "output": None,
                },
                {
                    "id": "T002",
                    "agent": "Dev2",
                    "status": "done",
                    "deps": [],
                    "description": "Task 002 — done",
                    "output": "resultado T002",
                },
            ],
        )

        # Lead executa Release em T001
        # release() retorna (graph_dict, action_dict)
        result_dict, action = release(graph_dict, "T001", lead_id="Lead")

        # Verifica ação emitida
        assert action["type"] == "release_task"
        assert action["id"] == "T001"

        # Verifica que o nó voltou a pending e perdeu o agent
        t001 = _find_node(result_dict, "T001")
        assert t001["status"] == "pending"
        assert t001["agent"] is None

        # O histórico deve conter a entrada de Release
        history_ops = [h["operator"] for h in result_dict["history"]]
        assert "Release" in history_ops

    # ------------------------------------------------------------------
    # Passo 5: reassignação + completação da task liberada
    # ------------------------------------------------------------------

    def test_reassigned_task_gets_completed(self):
        """
        Passo 5: Após Release, T001 é reassinada a Dev2 e completada.

        Sequência:
          1. Release T001 → volta a pending
          2. Assign T001 → Dev2
          3. Claim T001 por Dev2 → in_progress
          4. Complete T001 por Dev2 → done
          5. Grafo completo: ambos T001 e T002 em done
        """
        # Estado após Release: T001 pending, T002 done
        graph_dict = _make_graph_dict(
            round_num=6,
            nodes=[
                {
                    "id": "T001",
                    "agent": None,          # Liberado pelo Release
                    "status": "pending",
                    "deps": [],
                    "description": "Task 001 — reassigned",
                    "output": None,
                },
                {
                    "id": "T002",
                    "agent": "Dev2",
                    "status": "done",
                    "deps": [],
                    "description": "Task 002 — done",
                    "output": "resultado T002",
                },
            ],
            history=[
                {"round": 5, "agent": "Lead", "operator": "Release",
                 "node_id": "T001"},
            ],
        )

        # --- Passo A: Assign T001 → Dev2 (Lead) ---
        g1, action = assign(graph_dict, "T001", "Dev2", lead_id="Lead")
        assert action["type"] == "assign_task"
        assert action["id"] == "T001"
        assert action["to"] == "Dev2"
        t001 = _find_node(g1, "T001")
        assert t001["status"] == "assigned"
        assert t001["agent"] == "Dev2"

        # --- Passo B: Claim T001 por Dev2 (inicia execução) ---
        g2, action2 = claim(g1, "T001", "Dev2")
        assert action2["type"] == "claim_task"
        t001_2 = _find_node(g2, "T001")
        assert t001_2["status"] == "in_progress"
        assert t001_2["agent"] == "Dev2"

        # --- Passo C: Complete T001 por Dev2 ---
        g3, action3 = complete(g2, "T001", "Dev2")
        assert action3["type"] == "complete_task"
        t001_3 = _find_node(g3, "T001")
        assert t001_3["status"] == "done"
        assert t001_3["agent"] == "Dev2"

        # --- Verificação final: ambas tasks done ---
        statuses = {n["id"]: n["status"] for n in g3["nodes"]}
        assert statuses["T001"] == "done"
        assert statuses["T002"] == "done"

    # ------------------------------------------------------------------
    # Teste integrado: fluxo completo do cenário 2
    # ------------------------------------------------------------------

    def test_full_scenario_2_flow(self):
        """
        Teste integrado do cenário 2 completo.

        Simula todos os rounds do cenário:
          R1: Assign T001→Dev1, T002→Dev2. Claim ambas.
          R2: Dev2 completa T002. Dev1 não age.
          R3: Dev1 não age.
          R4: Dev1 não age.
          R5: Dev1 não age → heartbeat detecta straggler (H=4).
              Lead executa Release em T001.
          R6: Lead reassigna T001 a Dev2.
              Dev2 faz Claim + Complete em T001.
              Grafo fica terminal.
        """
        LEAD = "Lead"
        WORKERS = ["Dev1", "Dev2"]
        H = 4

        # --- Setup: G₀ com 2 tasks paralelas (dict) ---
        graph_dict = _make_graph_dict(
            round_num=0,
            workers=WORKERS,
            lead=LEAD,
            nodes=[
                {"id": "T001", "agent": None, "status": "pending",
                 "deps": [], "description": "Task 001", "output": None},
                {"id": "T002", "agent": None, "status": "pending",
                 "deps": [], "description": "Task 002", "output": None},
            ],
        )

        counters: dict[str, int] = {}

        # ----------------------------------------------------------------
        # Round 1: Lead assigna + Workers dão Claim
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 1
        graph_dict, _ = assign(graph_dict, "T001", "Dev1", lead_id=LEAD)
        graph_dict, _ = assign(graph_dict, "T002", "Dev2", lead_id=LEAD)
        graph_dict, _ = claim(graph_dict, "T001", "Dev1")
        graph_dict, _ = claim(graph_dict, "T002", "Dev2")
        # NOTA: assign(), claim(), complete(), release() já registram
        # histórico automaticamente via _record_in_history(). Não
        # adicionamos entradas manuais para evitar duplicação.

        mock_g = _make_mock_graph(graph_dict, round_num=1)
        stragglers_r1 = check_heartbeat(mock_g, counters, H=H)
        assert stragglers_r1 == [], (
            f"Round 1 não deve ter stragglers: {stragglers_r1}"
        )

        # ----------------------------------------------------------------
        # Round 2: Dev2 completa T002. Dev1 não age.
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 2
        graph_dict, _ = complete(graph_dict, "T002", "Dev2")
        # complete() já registra histórico automaticamente

        mock_g = _make_mock_graph(graph_dict, round_num=2)
        stragglers_r2 = check_heartbeat(mock_g, counters, H=H)
        assert stragglers_r2 == [], (
            f"Round 2 não deve ter stragglers (Dev1 inativo só 1 round): "
            f"{stragglers_r2}"
        )
        # counters["Dev1"] deve ser 1 (inativo no round 2)
        assert counters.get("Dev1", 0) == 1, (
            f"Dev1 deveria estar com 1 round inativo: {counters}"
        )

        # ----------------------------------------------------------------
        # Round 3: Ninguém age (Dev1 continua stuck, Dev2 já terminou)
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 3
        # Sem novas entradas no histórico (ninguém agiu)

        mock_g = _make_mock_graph(graph_dict, round_num=3)
        stragglers_r3 = check_heartbeat(mock_g, counters, H=H)
        assert stragglers_r3 == [], (
            f"Round 3 não deve ter stragglers (Dev1 inativo 2 rounds): "
            f"{stragglers_r3}"
        )
        assert counters.get("Dev1", 0) == 2

        # ----------------------------------------------------------------
        # Round 4: Ninguém age
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 4

        mock_g = _make_mock_graph(graph_dict, round_num=4)
        stragglers_r4 = check_heartbeat(mock_g, counters, H=H)
        assert stragglers_r4 == [], (
            f"Round 4 não deve ter stragglers (Dev1 inativo 3 rounds): "
            f"{stragglers_r4}"
        )
        assert counters.get("Dev1", 0) == 3

        # ----------------------------------------------------------------
        # Round 5: Dev1 atinge H=4 rounds inativos → straggler!
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 5

        mock_g = _make_mock_graph(graph_dict, round_num=5)
        stragglers_r5 = check_heartbeat(mock_g, counters, H=H)
        assert len(stragglers_r5) == 1, (
            f"Round 5 deve ter 1 straggler: {stragglers_r5}"
        )
        assert stragglers_r5[0]["worker_id"] == "Dev1"
        assert stragglers_r5[0]["node_id"] == "T001"
        assert stragglers_r5[0]["inactive_rounds"] >= 4
        assert counters.get("Dev1", 0) >= 4

        # ----------------------------------------------------------------
        # Lead executa Release em T001
        # ----------------------------------------------------------------
        graph_dict, release_action = release(graph_dict, "T001", lead_id=LEAD)
        assert release_action["type"] == "release_task"
        # Verifica que T001 voltou a pending
        t001 = _find_node(graph_dict, "T001")
        assert t001["status"] == "pending"
        assert t001["agent"] is None

        # Reseta heartbeat do Dev1 (clean slate após Release)
        reset_heartbeat(counters, "Dev1")
        assert counters["Dev1"] == 0

        # ----------------------------------------------------------------
        # Round 6: Reassign + Claim + Complete
        # ----------------------------------------------------------------
        graph_dict["metadata"]["round"] = 6

        # Assign T001 → Dev2
        graph_dict, _ = assign(graph_dict, "T001", "Dev2", lead_id=LEAD)

        # Claim T001 por Dev2
        graph_dict, _ = claim(graph_dict, "T001", "Dev2")

        # Complete T001 por Dev2
        graph_dict, _ = complete(graph_dict, "T001", "Dev2")
        # assign(), claim(), complete() já registram histórico

        # ----------------------------------------------------------------
        # Verificações finais
        # ----------------------------------------------------------------
        statuses = {n["id"]: n["status"] for n in graph_dict["nodes"]}
        assert statuses["T001"] == "done", (
            f"T001 deveria estar done: {statuses}"
        )
        assert statuses["T002"] == "done", (
            f"T002 deveria estar done: {statuses}"
        )

        agents = {n["id"]: n["agent"] for n in graph_dict["nodes"]}
        assert agents["T001"] == "Dev2", (
            f"T001 deveria estar com Dev2: {agents}"
        )
        assert agents["T002"] == "Dev2", (
            f"T002 deveria estar com Dev2: {agents}"
        )

        # Verifica que Release está no histórico
        history_ops = [h["operator"] for h in graph_dict["history"]]
        assert "Release" in history_ops, (
            f"Release deveria estar no histórico: {history_ops}"
        )

        # Verifica que todos os operadores esperados estão presentes
        for expected_op in ("Assign", "Claim", "Complete", "Release"):
            assert expected_op in history_ops, (
                f"'{expected_op}' deveria estar no histórico: {history_ops}"
            )

        # Verifica que o Dev2 completou ambas as tasks
        complete_entries = [
            h for h in graph_dict["history"]
            if h["operator"] == "Complete"
        ]
        assert len(complete_entries) == 2, (
            f"Esperado 2 completions: {complete_entries}"
        )


# =========================================================================
# Testes de borda (edge cases do cenário 2)
# =========================================================================


class TestScenario2EdgeCases:
    """Casos de borda relacionados ao cenário 2."""

    def test_straggler_with_no_active_nodes_does_not_generate_entry(self):
        """
        Se um Worker está inativo por H rounds mas não tem nós ativos
        (todos já done/verified), não deve gerar straggler entry.
        """
        graph_dict = _make_graph_dict(
            round_num=5,
            nodes=[
                {"id": "T001", "agent": "Dev1", "status": "done",
                 "deps": [], "description": "Done", "output": None},
            ],
        )
        mock_g = _make_mock_graph(graph_dict, round_num=5)
        counters = {"Dev1": 4}
        stragglers = check_heartbeat(mock_g, counters, H=4)
        assert stragglers == [], (
            f"Worker sem nós ativos não deve gerar straggler: {stragglers}"
        )

    def test_release_only_on_assigned_or_in_progress(self):
        """Release só deve funcionar em nós com status assigned ou in_progress."""
        graph_dict = _make_graph_dict(
            round_num=5,
            nodes=[
                {"id": "T001", "agent": None, "status": "done",
                 "deps": [], "description": "Already done",
                 "output": "result"},
            ],
        )
        with pytest.raises(ValueError, match="Release precondition failed"):
            release(graph_dict, "T001", lead_id="Lead")

    def test_heartbeat_resets_after_worker_acts(self):
        """Após Release e reassign, se Worker age, heartbeat deve resetar."""
        graph_dict = _make_graph_dict(
            round_num=6,
            nodes=[
                {"id": "T001", "agent": "Dev1", "status": "in_progress",
                 "deps": [], "description": "Task 001", "output": None},
            ],
            history=[
                {"round": 6, "agent": "Dev1", "operator": "Claim",
                 "node_id": "T001"},
            ],
        )
        mock_g = _make_mock_graph(graph_dict, round_num=6)
        counters = {"Dev1": 4}  # estava em 4, mas agiu neste round
        stragglers = check_heartbeat(mock_g, counters, H=4)
        assert counters["Dev1"] == 0, (
            f"Contador deveria ser 0 após ação, está {counters['Dev1']}"
        )
        assert stragglers == [], (
            f"Não deve haver stragglers se Worker agiu: {stragglers}"
        )

    def test_multiple_stragglers_in_same_round(self):
        """Se múltiplos Workers estão inativos, todos devem ser detectados."""
        graph_dict = _make_graph_dict(
            round_num=5,
            nodes=[
                {"id": "T001", "agent": "Dev1", "status": "in_progress",
                 "deps": [], "description": "Stuck 1", "output": None},
                {"id": "T002", "agent": "Dev2", "status": "in_progress",
                 "deps": [], "description": "Stuck 2", "output": None},
            ],
        )
        mock_g = _make_mock_graph(graph_dict, round_num=5)
        counters = {"Dev1": 5, "Dev2": 5}
        stragglers = check_heartbeat(mock_g, counters, H=4)
        assert len(stragglers) == 2, (
            f"Esperado 2 stragglers: {stragglers}"
        )
        worker_ids = {s["worker_id"] for s in stragglers}
        assert worker_ids == {"Dev1", "Dev2"}


# =========================================================================
# Helpers
# =========================================================================


def _find_node(graph_dict: dict, node_id: str) -> dict:
    """Encontra um nó pelo ID no dict do grafo. Levanta KeyError se ausente."""
    for node in graph_dict["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")


# =========================================================================
# Execução direta (python -m pytest ou python test_scenario_2_straggler.py)
# =========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
