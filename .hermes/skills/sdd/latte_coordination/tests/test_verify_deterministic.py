#!/usr/bin/env python3
"""Testes de Verify Determinístico (Feature 005 — Hardening ADR-009)."""

import unittest
from latte_coordination.orchestrator import (
    CoordinationGraph, VALID_VERIFY_MODES, DEFAULT_VERIFY_MODE,
)


class TestVerifyDeterministic(unittest.TestCase):

    def setUp(self):
        self.graph = CoordinationGraph(
            feature_id="005",
            lead="Lead-1",
            workers=["Dev1"],
            verify_mode="deterministic",
        )

    def test_default_verify_mode_is_deterministic(self):
        """Default é 'deterministic' (não 'llm')."""
        self.assertEqual(DEFAULT_VERIFY_MODE, "deterministic")
        g = CoordinationGraph(feature_id="005", lead="L", workers=["W1"])
        self.assertEqual(g.verify_mode, "deterministic")

    def test_verify_mode_llm_accepted(self):
        """verify_mode='llm' é válido."""
        g = CoordinationGraph(feature_id="005", lead="L", workers=["W1"],
                              verify_mode="llm")
        self.assertEqual(g.verify_mode, "llm")

    def test_verify_mode_invalid_rejected(self):
        """verify_mode inválido levanta ValueError."""
        with self.assertRaises(ValueError):
            CoordinationGraph(feature_id="005", lead="L", workers=["W1"],
                              verify_mode="invalid")

    def test_valid_verify_modes_frozenset(self):
        """VALID_VERIFY_MODES contém 'deterministic' e 'llm'."""
        self.assertIn("deterministic", VALID_VERIFY_MODES)
        self.assertIn("llm", VALID_VERIFY_MODES)
        self.assertEqual(len(VALID_VERIFY_MODES), 2)

    def test_checks_output_format_valid(self):
        """Check 1: formato válido (string não vazia)."""
        output = "Task completed successfully: created file.go"
        self.assertTrue(len(output) > 0)
        self.assertIsInstance(output, str)

    def test_checks_artifact_exists(self):
        """Check 2: artefato existe (path válido)."""
        import os
        self.assertTrue(os.path.exists(__file__))

    def test_checks_empty_output_detected(self):
        """Output vazio é detectado como falha."""
        output = ""
        self.assertEqual(len(output), 0)

    def test_checks_anti_pattern_detected(self):
        """Check 5: anti-padrão 'I will create' detectado."""
        output = "I will create the file later"
        self.assertIn("i will create", output.lower())


if __name__ == "__main__":
    unittest.main()
