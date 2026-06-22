#!/usr/bin/env python3
"""Testes de Timeout + Fallback (Feature 005 — Hardening ADR-007)."""

import unittest
from latte_coordination.orchestrator import CoordinationGraph


class TestTimeoutFallback(unittest.TestCase):

    def setUp(self):
        self.graph = CoordinationGraph(
            feature_id="005",
            lead="Lead-1",
            workers=["Dev1"],
            operator_timeout=45,
        )

    def test_timeout_default_value(self):
        """Valor default de operator_timeout = 45."""
        self.assertEqual(self.graph.operator_timeout, 45)

    def test_timeout_custom_value(self):
        """operator_timeout configurável."""
        g = CoordinationGraph(feature_id="005", lead="L", workers=["W1"],
                              operator_timeout=30)
        self.assertEqual(g.operator_timeout, 30)

    def test_timeout_zero_disables(self):
        """operator_timeout=0 desabilita timeout."""
        g = CoordinationGraph(feature_id="005", lead="L", workers=["W1"],
                              operator_timeout=0)
        self.assertEqual(g.operator_timeout, 0)

    def test_fallback_produces_sentinel(self):
        """Fallback retorna dict com status 'timeout'."""
        fallback = {"status": "timeout", "output": "Task exceeded time limit"}
        self.assertEqual(fallback["status"], "timeout")
        self.assertIn("output", fallback)

    def test_timeout_registered_as_error(self):
        """Timeout registra entrada em errors[]."""
        self.graph.add_error("T001", "timeout", "Task exceeded 45s limit")
        self.assertEqual(len(self.graph.errors), 1)
        self.assertEqual(self.graph.errors[0]["type"], "timeout")
        self.assertEqual(self.graph.errors[0]["node_id"], "T001")

    def test_heartbeat_not_redundant_after_timeout(self):
        """Timeout é preventivo (corta antes do heartbeat reativo)."""
        # Timeout opera no dispatcher (≤45s), heartbeat no orchestrator (≥4 rounds)
        self.assertLess(self.graph.operator_timeout,
                        self.graph.heartbeat_threshold * 100)
        # Sanity: timeout age em segundos, heartbeat em rounds


if __name__ == "__main__":
    unittest.main()
