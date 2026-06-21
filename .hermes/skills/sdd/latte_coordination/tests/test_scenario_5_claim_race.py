#!/usr/bin/env python3
"""
T016: Smoke Test — Edge Case #3: Claim Duplo (FIFO, primeiro vence)
=====================================================================

Feature 001: LATTE Coordination.

Edge case #3 do spec.md: Claim duplo no mesmo round — dois Workers
tentam reivindicar a mesma task. O protocolo LATTE resolve por FIFO:
o primeiro Claim processado vence; o segundo é rejeitado.

Fluxo testado:
  1. Criar G₀ com 1 task pending (T001), sem dependências.
  2. Simular Dev1 e Dev2 tentando Claim no mesmo round.
  3. Verificar que o primeiro Claim (Dev1) vence:
     task fica in_progress com agent=Dev1.
  4. Verificar que o segundo Claim (Dev2) é rejeitado:
     ValueError porque a task já foi claimed (agent=Dev1).

Lógica de Claim race documentada em latte-protocol.md:
  - Processamento sequencial dos Workers pelo orchestrator.
  - worker_operators.claim() verifica agent(v) ∈ {⊥, w}.
  - Primeiro Worker a executar claim() define agent(v) = w.
  - Segundo Worker falha na precondition agent(v) ≠ w.

Módulos utilizados:
  - worker_operators.py: claim() — API baseada em dicts
  - lead_operators.py: assign() — para pré-assignar (opcional)

O teste simula a ordem de processamento chamando claim() para Dev1
primeiro (assert sucesso) e depois para Dev2 (assert ValueError).

Nota: Assim como os testes T013 e T014, usamos dicts puros (GraphLike)
para evitar dependência do CoordinationGraph que usa imports relativos.
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

import pytest

from worker_operators import claim

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

VALID_STATUSES: frozenset[str] = frozenset({
    "pending",
    "assigned",
    "in_progress",
    "done",
    "verified",
})

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_G0_single_task(
    feature_id: str = "001",
    lead: str = "Lead-1",
    workers: list[str] | None = None,
    round_num: int = 1,
) -> dict[str, Any]:
    """
    Constrói G₀ (dict) com 1 task pending (T001), sem dependências.

    Estrutura:
        T001: pending, agent=None, deps=[]

    Args:
        feature_id: ID da feature para o metadata.
        lead: ID do Lead.
        workers: Lista de Workers disponíveis (default: ['Dev1', 'Dev2']).
        round_num: Número do round atual.

    Returns:
        Dict representando o coordination graph G₀.
    """
    if workers is None:
        workers = ["Dev1", "Dev2"]

    return {
        "metadata": {
            "feature_id": feature_id,
            "round": round_num,
            "max_rounds": 50,
            "heartbeat_threshold": 4,
            "workers": list(workers),
            "lead": lead,
        },
        "nodes": [
            {
                "id": "T001",
                "agent": None,
                "status": "pending",
                "deps": [],
                "description": "Task única — alvo do Claim race",
                "output": None,
                "rounds_inactive": 0,
                "created_at_round": 0,
                "assigned_at_round": None,
                "completed_at_round": None,
            },
        ],
        "edges": [],
        "history": [],
    }


def _find_node(graph_dict: dict[str, Any], node_id: str) -> dict[str, Any]:
    """Encontra um nó pelo ID no dict do grafo. Levanta KeyError se ausente."""
    for node in graph_dict["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(f"Node '{node_id}' not found in graph")


def _get_status(graph_dict: dict[str, Any], node_id: str) -> str:
    """Retorna o status de um nó."""
    return _find_node(graph_dict, node_id)["status"]


def _get_agent(graph_dict: dict[str, Any], node_id: str) -> str | None:
    """Retorna o agent de um nó."""
    return _find_node(graph_dict, node_id).get("agent")


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def G0_single_pending_task() -> dict[str, Any]:
    """
    Cria G₀ (dict) com 1 task pending (T001), sem dependências.

    Este é o estado inicial do cenário: uma única task disponível
    no frontier, pronta para ser reivindicada.
    """
    return _make_G0_single_task()


# ===========================================================================
# Testes
# ===========================================================================


class TestScenario5ClaimRaceFIFO:
    """
    Smoke test do Edge Case #3: Claim duplo no mesmo round (FIFO).

    Verifica que:
      - O primeiro Worker a executar claim() vence a task.
      - O segundo Worker é rejeitado com ValueError (precondition violada).
      - A task fica em in_progress com o agent do primeiro Worker.
      - A rejeição é explícita (exceção), não silenciosa.
    """

    # ------------------------------------------------------------------
    # Passo 1: G₀ criado com 1 task pending
    # ------------------------------------------------------------------

    def test_G0_has_one_pending_task(self, G0_single_pending_task):
        """
        (1) G₀ deve ter exatamente 1 nó (T001) com status 'pending'
        e agent=None.
        """
        g = G0_single_pending_task

        nodes = g["nodes"]
        assert len(nodes) == 1, (
            f"G₀ deve ter 1 nó, encontrados {len(nodes)}"
        )
        assert nodes[0]["id"] == "T001"
        assert nodes[0]["status"] == "pending"
        assert nodes[0]["agent"] is None
        assert nodes[0]["deps"] == []

        # Verifica metadata
        assert g["metadata"]["workers"] == ["Dev1", "Dev2"]
        assert g["metadata"]["round"] == 1

    # ------------------------------------------------------------------
    # Passo 2: Primeiro Claim (Dev1) vence
    # ------------------------------------------------------------------

    def test_first_claim_succeeds_dev1_wins(self, G0_single_pending_task):
        """
        (2) Dev1 executa claim(T001) primeiro → deve ter sucesso.

        Após o Claim de Dev1:
          - T001.status = 'in_progress'
          - T001.agent = 'Dev1'
          - A ação emitida é do tipo 'claim_task'
        """
        g = G0_single_pending_task

        # Dev1 tenta Claim primeiro (simula ordem FIFO de processamento)
        g_after, action = claim(g, "T001", "Dev1")

        # Verifica ação emitida
        assert action["type"] == "claim_task", (
            f"Ação deve ser 'claim_task', obtida '{action['type']}'"
        )
        assert action["id"] == "T001"
        assert action["worker"] == "Dev1"

        # Verifica estado do nó
        assert _get_status(g_after, "T001") == "in_progress", (
            f"T001 deve estar 'in_progress' após Claim de Dev1, "
            f"mas está '{_get_status(g_after, 'T001')}'"
        )
        assert _get_agent(g_after, "T001") == "Dev1", (
            f"T001.agent deve ser 'Dev1', "
            f"mas é '{_get_agent(g_after, 'T001')}'"
        )

        # Verifica que o Claim foi registrado no histórico
        history_ops = [h["operator"] for h in g_after["history"]]
        assert "Claim" in history_ops, (
            f"Histórico deve conter 'Claim', operadores: {history_ops}"
        )

        claim_entries = [h for h in g_after["history"] if h["operator"] == "Claim"]
        assert len(claim_entries) == 1
        assert claim_entries[0]["agent"] == "Dev1"
        assert claim_entries[0]["node_id"] == "T001"

    # ------------------------------------------------------------------
    # Passo 3: Segundo Claim (Dev2) é rejeitado
    # ------------------------------------------------------------------

    def test_second_claim_rejected_dev2_fails(self, G0_single_pending_task):
        """
        (3) Após Dev1 ter feito Claim com sucesso, Dev2 tenta Claim
        na mesma task → deve ser rejeitado com ValueError.

        O claim() de Dev2 falha porque:
          - T001.status = 'in_progress' (não é 'pending' nem 'assigned')
          - T001.agent = 'Dev1' (não é None nem 'Dev2')
          → Precondition 2 violada: agent(v) ∉ {⊥, Dev2}
        """
        g = G0_single_pending_task

        # --- Primeiro Claim: Dev1 vence ---
        g_after_dev1, action1 = claim(g, "T001", "Dev1")

        assert action1["type"] == "claim_task"
        assert _get_status(g_after_dev1, "T001") == "in_progress"
        assert _get_agent(g_after_dev1, "T001") == "Dev1"

        # --- Segundo Claim: Dev2 tenta e FALHA ---
        # Usa o grafo retornado pelo primeiro Claim (já modificado).
        # O claim() faz deep copy, então o original G0_single_pending_task
        # não foi afetado. Usamos g_after_dev1 como estado atual.
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g_after_dev1, "T001", "Dev2")

        # Verifica que o estado do grafo NÃO foi alterado pela tentativa
        # de Dev2 (o claim() lança exceção antes de mutar)
        assert _get_status(g_after_dev1, "T001") == "in_progress", (
            f"T001 deve permanecer 'in_progress' após Claim rejeitado de Dev2, "
            f"mas está '{_get_status(g_after_dev1, 'T001')}'"
        )
        assert _get_agent(g_after_dev1, "T001") == "Dev1", (
            f"T001.agent deve permanecer 'Dev1' após Claim rejeitado de Dev2, "
            f"mas é '{_get_agent(g_after_dev1, 'T001')}'"
        )

        # O histórico deve conter apenas 1 Claim (do Dev1)
        claim_entries = [
            h for h in g_after_dev1["history"] if h["operator"] == "Claim"
        ]
        assert len(claim_entries) == 1, (
            f"Histórico deve conter exatamente 1 Claim (Dev1), "
            f"encontrados {len(claim_entries)}"
        )
        assert claim_entries[0]["agent"] == "Dev1"

    # ------------------------------------------------------------------
    # Passo 4: Dev1 completa a task após vencer o Claim race
    # ------------------------------------------------------------------

    def test_dev1_completes_task_after_winning_claim(self, G0_single_pending_task):
        """
        (4) Fluxo completo: Dev1 vence Claim race e completa a task.

        Sequência:
          1. Dev1 Claim → T001 in_progress (Dev1)
          2. Dev2 Claim → rejeitado
          3. Dev1 Complete → T001 done (Dev1)
        """
        from worker_operators import complete as worker_complete

        g = G0_single_pending_task

        # --- Dev1 Claim (vence) ---
        g, action = claim(g, "T001", "Dev1")
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev1"

        # --- Dev2 Claim (rejeitado) ---
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g, "T001", "Dev2")

        # Estado permanece inalterado
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev1"

        # --- Dev1 Complete (conclui) ---
        g, action = worker_complete(g, "T001", "Dev1")
        assert action["type"] == "complete_task"
        assert _get_status(g, "T001") == "done"
        assert _get_agent(g, "T001") == "Dev1", (
            f"Agente deve ser preservado como 'Dev1' após Complete, "
            f"mas é '{_get_agent(g, 'T001')}'"
        )

        # Verifica histórico completo
        history_ops = [h["operator"] for h in g["history"]]
        assert "Claim" in history_ops
        assert "Complete" in history_ops
        # Verifica que não há Claim do Dev2
        claim_agents = [
            h["agent"]
            for h in g["history"]
            if h["operator"] == "Claim"
        ]
        assert claim_agents == ["Dev1"], (
            f"Apenas Dev1 deve ter Claim no histórico, "
            f"encontrados: {claim_agents}"
        )

    # ------------------------------------------------------------------
    # Edge case: inversão de ordem (Dev2 primeiro)
    # ------------------------------------------------------------------

    def test_claim_race_dev2_first_wins(self, G0_single_pending_task):
        """
        Edge case complementar: se Dev2 fizer Claim primeiro, Dev2 vence
        e Dev1 é rejeitado. O comportamento é simétrico (FIFO).
        """
        g = G0_single_pending_task

        # --- Dev2 Claim primeiro (vence) ---
        g, action = claim(g, "T001", "Dev2")
        assert action["type"] == "claim_task"
        assert action["worker"] == "Dev2"
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev2"

        # --- Dev1 Claim depois (rejeitado) ---
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g, "T001", "Dev1")

        # Estado permanece com Dev2
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev2"

    # ------------------------------------------------------------------
    # Edge case: Claim de task já assignada a outro Worker
    # ------------------------------------------------------------------

    def test_claim_assigned_to_other_worker_fails(self):
        """
        Se a task já está assignada a Dev1 (status=assigned, agent=Dev1),
        Dev2 não pode fazer Claim — mesmo cenário de race condição,
        mas com status 'assigned' em vez de 'in_progress'.
        """
        from lead_operators import assign as lead_assign

        g = _make_G0_single_task()

        # Lead assigna T001 a Dev1
        g, action = lead_assign(g, "T001", "Dev1")
        assert _get_status(g, "T001") == "assigned"
        assert _get_agent(g, "T001") == "Dev1"

        # Dev2 tenta Claim → rejeitado (agent != Dev2)
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g, "T001", "Dev2")

        # Dev1 pode fazer Claim normalmente (inicia execução)
        g, action = claim(g, "T001", "Dev1")
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev1"

    # ------------------------------------------------------------------
    # Edge case: mesmo Worker fazendo Claim duplo
    # ------------------------------------------------------------------

    def test_same_worker_claim_twice_is_idempotent_or_rejected(
        self, G0_single_pending_task
    ):
        """
        Se o mesmo Worker tenta Claim duas vezes na mesma task,
        o segundo Claim deve ser rejeitado (status já é in_progress).
        """
        g = G0_single_pending_task

        # Primeiro Claim: sucesso
        g, action = claim(g, "T001", "Dev1")
        assert _get_status(g, "T001") == "in_progress"

        # Segundo Claim pelo mesmo Worker: rejeitado
        # (status não é 'pending' nem 'assigned')
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g, "T001", "Dev1")

    # ------------------------------------------------------------------
    # Teste integrado: cenário completo com 2 tasks e race parcial
    # ------------------------------------------------------------------

    def test_two_tasks_one_race(self):
        """
        Cenário estendido: 2 tasks no frontier, Dev1 e Dev2 competem
        pela T001 (Dev1 vence), Dev2 faz Claim da T002 normalmente.

        Verifica que:
          - T001 fica com Dev1 (in_progress)
          - T002 fica com Dev2 (in_progress)
          - Dev2 é rejeitado em T001
        """
        g = {
            "metadata": {
                "feature_id": "001",
                "round": 1,
                "max_rounds": 50,
                "heartbeat_threshold": 4,
                "workers": ["Dev1", "Dev2"],
                "lead": "Lead-1",
            },
            "nodes": [
                {
                    "id": "T001",
                    "agent": None,
                    "status": "pending",
                    "deps": [],
                    "description": "Task 001 — alvo do race",
                    "output": None,
                },
                {
                    "id": "T002",
                    "agent": None,
                    "status": "pending",
                    "deps": [],
                    "description": "Task 002 — sem race",
                    "output": None,
                },
            ],
            "edges": [],
            "history": [],
        }

        # --- Race em T001: Dev1 primeiro → vence ---
        g, action = claim(g, "T001", "Dev1")
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev1"

        # Dev2 tenta T001 → rejeitado
        with pytest.raises(ValueError, match="Claim precondition failed"):
            claim(g, "T001", "Dev2")

        # --- Dev2 faz Claim de T002 (sem race) ---
        g, action = claim(g, "T002", "Dev2")
        assert _get_status(g, "T002") == "in_progress"
        assert _get_agent(g, "T002") == "Dev2"

        # Verifica estado final
        assert _get_status(g, "T001") == "in_progress"
        assert _get_agent(g, "T001") == "Dev1"
        assert _get_status(g, "T002") == "in_progress"
        assert _get_agent(g, "T002") == "Dev2"

        # Histórico: 2 Claims (Dev1 em T001, Dev2 em T002)
        claim_entries = [
            h for h in g["history"] if h["operator"] == "Claim"
        ]
        assert len(claim_entries) == 2

        claim_pairs = {(h["agent"], h["node_id"]) for h in claim_entries}
        assert claim_pairs == {("Dev1", "T001"), ("Dev2", "T002")}


# ===========================================================================
# Runner
# ===========================================================================

if __name__ == "__main__":
    print("=" * 65)
    print("T016: Smoke Test — Edge Case #3: Claim Duplo (FIFO)")
    print("=" * 65)
    pytest.main([__file__, "-v", "--tb=short"])
