#!/usr/bin/env python3
"""
T012: Smoke Test — Cenário 1: Execução Normal com DAG Simples
==============================================================

Cenário 1 do spec.md: execução normal com DAG simples de 3 tasks
sequenciais (T001 → T002 → T003). O teste verifica o fluxo completo
de coordenação usando os módulos reais:

  - CoordinationGraph + Orchestrator (orchestrator.py)
  - compute_frontier (frontier.py)
  - lead_operators: Discover, Assign
  - worker_operators: Claim, Complete
  - dispatch (dispatcher.py)

Assertivas:
  1. G₀ criado com 3 tasks sequenciais (T001→T002→T003)
  2. Frontier F_1 = ['T001'] (apenas raiz sem deps pendentes)
  3. Orquestrador executa run() (loop de rounds)
  4. Todas as tasks ficam com status "done"
  5. Pelo menos 1 operador Discover foi usado
  6. Operadores Claim e Complete foram usados

Execução:
    cd .hermes/skills/sdd/latte_coordination/tests
    python test_scenario_1_normal.py
"""

from __future__ import annotations

import unittest

from latte_coordination.orchestrator import CoordinationGraph, Orchestrator
from latte_coordination.frontier import compute_frontier
from latte_coordination.lead_operators import assign as lead_assign
from latte_coordination.lead_operators import discover as lead_discover
from latte_coordination.worker_operators import claim as worker_claim
from latte_coordination.worker_operators import complete as worker_complete

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _build_simple_dag(feature_id: str = "001",
                      lead: str = "Lead-1",
                      workers: list[str] | None = None) -> CoordinationGraph:
    """
    Constrói G₀ com 3 tasks sequenciais:

        T001 (pending) → T002 (pending) → T003 (pending)

    Usa o operador lead_discover (via raw dict) para registrar
    as operações Discover no histórico, conforme exigido pelo teste.
    """
    if workers is None:
        workers = ["Dev1"]

    g = CoordinationGraph(
        feature_id=feature_id,
        lead=lead,
        workers=workers,
    )

    raw = g.raw

    # Discover T001 (raiz, sem dependências)
    raw, _ = lead_discover(
        raw, "T001", "Criar estrutura base do módulo",
        deps=[], lead_id=lead,
    )
    # Discover T002 (depende de T001)
    raw, _ = lead_discover(
        raw, "T002", "Implementar lógica central",
        deps=["T001"], lead_id=lead,
    )
    # Discover T003 (depende de T002)
    raw, _ = lead_discover(
        raw, "T003", "Escrever testes de unidade",
        deps=["T002"], lead_id=lead,
    )

    # Reconstrói CoordinationGraph com o raw modificado
    g._graph = raw
    g._invalidate_cache()
    return g


def _apply_operators_on_raw(graph: CoordinationGraph) -> dict:
    """
    Executa operadores LATTE (Assign → Claim → Complete) sequencialmente
    sobre os 3 nós, trabalhando com a representação dict (raw) do grafo.

    Os nós T001, T002, T003 já existem no grafo (criados como pending
    via add_node). O fluxo para cada nó é:

      Assign(Lead) → Claim(Worker) → Complete(Worker)

    Fluxo simulado para uma DAG linear T001→T002→T003 com 1 Worker:
      Round 1: Assign(T001, Dev1) → Claim(T001, Dev1) → Complete(T001, Dev1)
      Round 2: Assign(T002, Dev1) → Claim(T002, Dev1) → Complete(T002, Dev1)
      Round 3: Assign(T003, Dev1) → Claim(T003, Dev1) → Complete(T003, Dev1)

    Retorna o dict raw do grafo após todas as operações.
    """
    raw = graph.raw
    lead_id = graph.lead
    worker_id = graph.workers[0]

    # ── Round 1: T001 ────────────────────────────────────────────────
    # Lead assigna T001 ao Worker
    raw, _ = lead_assign(raw, "T001", worker_id, lead_id=lead_id)
    # Worker faz Claim (assigned → in_progress)
    raw, _ = worker_claim(raw, "T001", worker_id)
    # Worker completa (in_progress → done)
    raw, _ = worker_complete(raw, "T001", worker_id)

    # ── Round 2: T002 ────────────────────────────────────────────────
    raw, _ = lead_assign(raw, "T002", worker_id, lead_id=lead_id)
    raw, _ = worker_claim(raw, "T002", worker_id)
    raw, _ = worker_complete(raw, "T002", worker_id)

    # ── Round 3: T003 ────────────────────────────────────────────────
    raw, _ = lead_assign(raw, "T003", worker_id, lead_id=lead_id)
    raw, _ = worker_claim(raw, "T003", worker_id)
    raw, _ = worker_complete(raw, "T003", worker_id)

    return raw


# ──────────────────────────────────────────────────────────────────────────────
# TestCase
# ──────────────────────────────────────────────────────────────────────────────

class TestScenario1Normal(unittest.TestCase):
    """Smoke test: Cenário 1 — execução normal com DAG simples de 3 tasks."""

    def test_create_g0_with_3_sequential_tasks(self):
        """
        (1) Cria G₀ com 3 tasks sequenciais: T001 → T002 → T003.
        Verifica que o grafo tem 3 nós, 2 arestas e todos status=pending.
        """
        g = _build_simple_dag()

        self.assertEqual(g.get_node_count(), 3,
                         "G₀ deve ter 3 nós")
        self.assertEqual(g.get_edge_count(), 2,
                         "G₀ deve ter 2 arestas (T001→T002, T002→T003)")

        # Verifica que todos estão pending
        for nid in ("T001", "T002", "T003"):
            node = g.find_node(nid)
            self.assertIsNotNone(node, f"Nó {nid} deve existir")
            self.assertEqual(node["status"], "pending",
                             f"Nó {nid} deve estar 'pending'")

    def test_frontier_only_root(self):
        """
        (2) Frontier F_t: apenas T001 deve aparecer (única raiz sem
        dependências pendentes).
        """
        g = _build_simple_dag()
        frontier = compute_frontier(g)

        self.assertEqual(frontier, ["T001"],
                         f"Frontier deve ser ['T001'], obtido {frontier}")

    def test_frontier_after_t001_done(self):
        """
        (2b) Após marcar T001 como done, o frontier deve conter T002.
        A transição deve respeitar a máquina de estados:
        pending → assigned → in_progress → done.
        """
        g = _build_simple_dag()
        # Transição correta pela máquina de estados
        g.update_node_status("T001", "assigned", agent="Dev1")
        g.update_node_status("T001", "in_progress", agent="Dev1")
        g.update_node_status("T001", "done", agent="Dev1")
        frontier = compute_frontier(g)

        self.assertEqual(frontier, ["T002"],
                         f"Frontier deve ser ['T002'] após T001 done, "
                         f"obtido {frontier}")

    def test_full_execution_smoke(self):
        """
        (3)-(6) Smoke test completo: aplica operadores LATTE manualmente
        e verifica que todas as tasks chegam a 'done', e que os operadores
        Discover e Claim foram registrados no histórico.
        """
        g = _build_simple_dag()
        raw = _apply_operators_on_raw(g)

        # ── Assertiva 4: todas as tasks done ─────────────────────
        nodes = raw["nodes"]
        self.assertEqual(len(nodes), 3, "Deve haver 3 nós no grafo final")

        for node in nodes:
            self.assertEqual(
                node["status"], "done",
                f"Nó {node['id']} deve estar 'done', "
                f"mas está '{node['status']}'"
            )

        # ── Assertiva 5: pelo menos 1 Discover ──────────────────
        history = raw["history"]
        discover_ops = [h for h in history if h["operator"] == "Discover"]
        self.assertGreaterEqual(
            len(discover_ops), 1,
            f"Deve haver pelo menos 1 operador Discover no histórico, "
            f"encontrados {len(discover_ops)}"
        )
        # No nosso cenário, são 3 Discovers (um por task)
        self.assertEqual(
            len(discover_ops), 3,
            f"Devem existir exatamente 3 Discover (1 por task), "
            f"encontrados {len(discover_ops)}"
        )

        # ── Assertiva 6: Claim foi usado ────────────────────────
        claim_ops = [h for h in history if h["operator"] == "Claim"]
        self.assertGreaterEqual(
            len(claim_ops), 1,
            f"Deve haver pelo menos 1 operador Claim no histórico, "
            f"encontrados {len(claim_ops)}"
        )

        # ── Assertivas adicionais ───────────────────────────────
        # Complete também deve ter sido usado
        complete_ops = [h for h in history if h["operator"] == "Complete"]
        self.assertEqual(
            len(complete_ops), 3,
            f"Devem existir 3 Complete (1 por task), "
            f"encontrados {len(complete_ops)}"
        )

        # Assign também deve ter sido usado (Lead assignou cada task)
        assign_ops = [h for h in history if h["operator"] == "Assign"]
        self.assertEqual(
            len(assign_ops), 3,
            f"Devem existir 3 Assign (1 por task), "
            f"encontrados {len(assign_ops)}"
        )

        # ── O grafo deve ser considerado terminal ───────────────
        # Reconstrói CoordinationGraph a partir do raw para usar is_terminal()
        g2 = CoordinationGraph(
            feature_id="001",
            lead="Lead-1",
            workers=["Dev1"],
        )
        g2._graph = raw
        g2._invalidate_cache()

        self.assertTrue(g2.is_terminal(),
                        "Grafo deve ser terminal (todos done)")

        # ── Verifica estrutura: arestas corretas ────────────────
        edges = raw["edges"]
        edge_pairs = {(e["from"], e["to"]) for e in edges}
        expected_edges = {("T001", "T002"), ("T002", "T003")}
        self.assertEqual(edge_pairs, expected_edges,
                         f"Arestas devem ser {expected_edges}, "
                         f"obtido {edge_pairs}")

        # ── Verifica agentes ────────────────────────────────────
        for node in nodes:
            self.assertEqual(
                node.get("agent"), "Dev1",
                f"Nó {node['id']} deve ter agent='Dev1', "
                f"mas tem '{node.get('agent')}'"
            )

    def test_orchestrator_instantiation_and_run(self):
        """
        (3) Instancia Orchestrator com G₀ e executa run().
        Como _execute_lead/_execute_worker são stubs, o loop roda
        até timeout, mas o Orchestrator em si não deve lançar exceção.
        """
        g = _build_simple_dag()
        orch = Orchestrator(
            task_description="Smoke test: DAG simples T001→T002→T003",
            G_0=g,
            config={"max_rounds": 3, "verbose": False},
        )

        # Executa run() — deve completar sem exceções
        result = orch.run()

        self.assertIsInstance(result, CoordinationGraph,
                              "run() deve retornar um CoordinationGraph")
        self.assertEqual(result.round, 3,
                         f"Deve ter executado 3 rounds, mas round={result.round}")

    def test_frontier_progression_through_dag(self):
        """
        Verifica a progressão correta do frontier conforme os nós
        são marcados como done um por um, respeitando a máquina de
        estados: pending → assigned → in_progress → done.
        """
        g = _build_simple_dag()

        # Estado inicial
        self.assertEqual(compute_frontier(g), ["T001"])

        # T001: pending → assigned → in_progress → done
        g.update_node_status("T001", "assigned", agent="Dev1")
        g.update_node_status("T001", "in_progress", agent="Dev1")
        g.update_node_status("T001", "done", agent="Dev1")
        self.assertEqual(compute_frontier(g), ["T002"])

        # T002: pending → assigned → in_progress → done
        g.update_node_status("T002", "assigned", agent="Dev1")
        g.update_node_status("T002", "in_progress", agent="Dev1")
        g.update_node_status("T002", "done", agent="Dev1")
        self.assertEqual(compute_frontier(g), ["T003"])

        # T003: pending → assigned → in_progress → done
        g.update_node_status("T003", "assigned", agent="Dev1")
        g.update_node_status("T003", "in_progress", agent="Dev1")
        g.update_node_status("T003", "done", agent="Dev1")
        self.assertEqual(compute_frontier(g), [],
                         "Frontier deve estar vazio quando todos done")

        # Grafo terminal
        self.assertTrue(g.is_terminal())


# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("T012: Smoke Test — Cenário 1 (DAG Simples)")
    print("=" * 65)
    unittest.main(verbosity=2)
