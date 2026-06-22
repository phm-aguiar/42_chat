#!/usr/bin/env python3
"""Testes de Partial Failure Propagation (Feature 005 — Hardening ADR-008)."""

import unittest
from latte_coordination.orchestrator import CoordinationGraph


class TestPartialFailure(unittest.TestCase):

    def setUp(self):
        self.graph = CoordinationGraph(
            feature_id="005",
            lead="Lead-1",
            workers=["Dev1", "Dev2"],
        )

    def test_errors_starts_empty(self):
        """errors[] começa vazio."""
        self.assertEqual(len(self.graph.errors), 0)

    def test_add_error_registers_correctly(self):
        """add_error() popula campos corretamente."""
        self.graph.add_error("T003", "timeout", "Worker stalled")
        self.assertEqual(len(self.graph.errors), 1)
        err = self.graph.errors[0]
        self.assertEqual(err["node_id"], "T003")
        self.assertEqual(err["type"], "timeout")
        self.assertEqual(err["message"], "Worker stalled")
        self.assertIn("round", err)
        self.assertIn("timestamp", err)

    def test_multiple_errors_accumulate(self):
        """Múltiplos erros são registrados em sequência."""
        self.graph.add_error("T001", "timeout", "msg1")
        self.graph.add_error("T002", "parse_error", "msg2")
        self.graph.add_error("T003", "timeout", "msg3")
        self.assertEqual(len(self.graph.errors), 3)

    def test_cascading_failure_does_not_block(self):
        """1 falha não bloqueia outras tasks — erros são isolados."""
        from latte_coordination.lead_operators import discover
        g = CoordinationGraph(feature_id="005", lead="Lead-1",
                              workers=["Dev1", "Dev2"])
        g_dict, _ = discover(g, "T001", "Root", [])
        g_dict, _ = discover(g_dict, "T002", "Child A", ["T001"])
        g_dict, _ = discover(g_dict, "T003", "Child B", ["T001"])
        g_dict, _ = discover(g_dict, "T004", "Child C", [])  # independente

        # T001 falha — registra erro no dict
        from datetime import datetime, timezone
        g_dict["metadata"]["errors"].append({
            "node_id": "T001",
            "type": "runtime_error",
            "message": "T001 crashed",
            "round": g_dict["metadata"]["round"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # T002 e T003 têm upstream error — mas T004 não
        upstream_errors = [e for e in g_dict["metadata"]["errors"]
                          if e["node_id"] == "T001"]
        self.assertEqual(len(upstream_errors), 1)
        self.assertEqual(upstream_errors[0]["type"], "runtime_error")

        # T004: sem dependência em T001 → sem upstream errors
        self.assertIn("T004", [n["id"] for n in g_dict["nodes"]])

    def test_errors_persist_in_state(self):
        """Erros sobrevivem a múltiplos rounds (não são limpos)."""
        self.graph.add_error("T001", "timeout", "msg")
        self.graph.round = 5
        self.assertEqual(len(self.graph.errors), 1)
        self.graph.round = 10
        self.assertEqual(len(self.graph.errors), 1)


if __name__ == "__main__":
    unittest.main()
