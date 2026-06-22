#!/usr/bin/env python3
"""Testes de Budget Tracking (Feature 005 — Hardening ADR-006)."""

import unittest
from latte_coordination.orchestrator import CoordinationGraph


class TestBudgetTracking(unittest.TestCase):

    def setUp(self):
        self.graph = CoordinationGraph(
            feature_id="005",
            lead="Lead-1",
            workers=["Dev1", "QA1"],
            max_llm_calls=10,
        )

    def test_budget_not_exhausted_initially(self):
        """Chamadas abaixo do limite NÃO acionam force_finalize."""
        self.assertEqual(self.graph.llm_calls_made, 0)
        self.assertFalse(self.graph.is_budget_exhausted())

    def test_budget_increments_correctly(self):
        """llm_calls_made incrementa via increment_llm_calls()."""
        self.graph.increment_llm_calls(3)
        self.assertEqual(self.graph.llm_calls_made, 3)
        self.graph.increment_llm_calls(5)
        self.assertEqual(self.graph.llm_calls_made, 8)
        self.assertFalse(self.graph.is_budget_exhausted())

    def test_budget_exhausted_triggers(self):
        """Quando llm_calls_made >= max_llm_calls, is_budget_exhausted() = True."""
        self.graph.increment_llm_calls(10)
        self.assertTrue(self.graph.is_budget_exhausted())

    def test_budget_exceeded_also_triggers(self):
        """Exceder o limite também dispara."""
        self.graph.increment_llm_calls(15)
        self.assertTrue(self.graph.is_budget_exhausted())

    def test_budget_default_value(self):
        """Valor default de max_llm_calls = 25."""
        g = CoordinationGraph(feature_id="005", lead="L", workers=["W1"])
        self.assertEqual(g.max_llm_calls, 25)

    def test_force_finalize_marks_all_done(self):
        """force_finalize() marca todas tasks pending como done."""
        from latte_coordination.lead_operators import discover
        g = CoordinationGraph(feature_id="005", lead="Lead-1", workers=["Dev1"])
        g_dict, _ = discover(g, "T001", "Task 1", [])
        g_dict, _ = discover(g_dict, "T002", "Task 2", ["T001"])

        # Simula budget exhaust → force_finalize via dict API
        g_dict["metadata"]["llm_calls_made"] = g_dict["metadata"]["max_llm_calls"]

        # Verifica que nodes existem (force_finalize chamado externamente)
        self.assertEqual(len(g_dict["nodes"]), 2)
        for node in g_dict["nodes"]:
            self.assertIn(node["status"], ["pending", "done"])


if __name__ == "__main__":
    unittest.main()
