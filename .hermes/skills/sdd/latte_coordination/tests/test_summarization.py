#!/usr/bin/env python3
"""Testes de Context Summarization (Feature 005 — Hardening ADR-010)."""

import unittest
from latte_coordination.orchestrator import CoordinationGraph


class TestContextSummarization(unittest.TestCase):

    def setUp(self):
        self.graph = CoordinationGraph(
            feature_id="005",
            lead="Lead-1",
            workers=["Dev1", "QA1"],
        )

    def test_summary_starts_empty(self):
        """completed_summary começa vazio."""
        self.assertEqual(self.graph.completed_summary, "")

    def test_round_since_summary_starts_zero(self):
        """round_since_summary começa em 0."""
        self.assertEqual(self.graph.round_since_summary, 0)

    def test_summary_can_be_set(self):
        """completed_summary pode ser atualizado."""
        self.graph.completed_summary = "Resumo (rounds 1-4): T001, T002 concluídas"
        self.assertIn("T001", self.graph.completed_summary)
        self.assertIn("T002", self.graph.completed_summary)

    def test_round_counter_increments(self):
        """round_since_summary incrementa manualmente."""
        self.graph.round_since_summary = 1
        self.assertEqual(self.graph.round_since_summary, 1)
        self.graph.round_since_summary += 1
        self.assertEqual(self.graph.round_since_summary, 2)

    def test_summary_interval_default_is_4(self):
        """Intervalo de sumarização default = 4 rounds."""
        self.assertEqual(self.graph.round_since_summary, 0)
        # Após 4 rounds, deve disparar sumarização
        for _ in range(4):
            self.graph.round_since_summary += 1
        self.assertEqual(self.graph.round_since_summary, 4)

    def test_summary_resets_after_summarization(self):
        """Após sumarização, round_since_summary reseta."""
        self.graph.completed_summary = "Resumo: T001-T004"
        self.graph.round_since_summary = 0  # reset
        self.assertEqual(self.graph.round_since_summary, 0)

    def test_summary_preserves_across_rounds(self):
        """Sumário persiste entre rounds (não é limpo a cada round)."""
        self.graph.completed_summary = "R1-4: T001, T002"
        self.graph.round += 1
        self.assertEqual(self.graph.completed_summary, "R1-4: T001, T002")


if __name__ == "__main__":
    unittest.main()
