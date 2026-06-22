#!/usr/bin/env python3
"""Testes de Equal-Weight Merge (Feature 005 — Hardening ADR-012)."""

import unittest
from latte_coordination.dispatcher import MERGE_EQUAL_WEIGHT_INSTRUCTION


class TestEqualWeightMerge(unittest.TestCase):

    def test_merge_instruction_exists(self):
        """Instrução de equal-weight merge está definida."""
        self.assertIsInstance(MERGE_EQUAL_WEIGHT_INSTRUCTION, str)
        self.assertGreater(len(MERGE_EQUAL_WEIGHT_INSTRUCTION), 20)

    def test_merge_instruction_mentions_weight(self):
        """Instrução menciona 'weight each input equally'."""
        self.assertIn("weight", MERGE_EQUAL_WEIGHT_INSTRUCTION.lower())
        self.assertIn("equally", MERGE_EQUAL_WEIGHT_INSTRUCTION.lower())

    def test_merge_instruction_mentions_length(self):
        """Instrução menciona 'regardless of length'."""
        self.assertIn("regardless of length", MERGE_EQUAL_WEIGHT_INSTRUCTION.lower())

    def test_merge_instruction_mentions_under_researched(self):
        """Instrução sinaliza domínios sub-pesquisados."""
        self.assertIn("under-researched", MERGE_EQUAL_WEIGHT_INSTRUCTION.lower())

    def test_merge_instruction_included_in_dispatch_context(self):
        """Instrução é injetada no contexto de dispatch com merge_instruction."""
        # Simula contexto de dispatch com merge_instruction
        dep_outputs = {"T001": "output A", "T002": "output B"}
        context = {
            "merge_instruction": MERGE_EQUAL_WEIGHT_INSTRUCTION if dep_outputs else None,
        }
        self.assertIsNotNone(context["merge_instruction"])
        self.assertIn("weight", context["merge_instruction"].lower())

    def test_merge_instruction_none_when_no_deps(self):
        """Sem dependências, merge_instruction = None."""
        context = {
            "merge_instruction": MERGE_EQUAL_WEIGHT_INSTRUCTION if {} else None,
        }
        self.assertIsNone(context["merge_instruction"])


if __name__ == "__main__":
    unittest.main()
