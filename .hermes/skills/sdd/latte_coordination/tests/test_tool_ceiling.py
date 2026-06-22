#!/usr/bin/env python3
"""Testes de Tool Ceiling (Feature 005 — Hardening ADR-011)."""

import unittest
from latte_coordination.dispatcher import TOOLSET_MAP


class TestToolCeiling(unittest.TestCase):

    def test_toolset_map_exists(self):
        """TOOLSET_MAP está definido com papéis esperados."""
        self.assertIsInstance(TOOLSET_MAP, dict)
        self.assertGreater(len(TOOLSET_MAP), 0)

    def test_dev_has_terminal_file_patch(self):
        """Worker Dev recebe [terminal, file, patch]."""
        dev_tools = TOOLSET_MAP.get("Dev", [])
        self.assertIn("terminal", dev_tools)
        self.assertIn("file", dev_tools)
        self.assertIn("patch", dev_tools)
        self.assertEqual(len(dev_tools), 3)

    def test_qa_has_terminal_file(self):
        """Worker QA recebe [terminal, file]."""
        qa_tools = TOOLSET_MAP.get("QA", [])
        self.assertIn("terminal", qa_tools)
        self.assertIn("file", qa_tools)
        self.assertNotIn("patch", qa_tools)

    def test_devops_has_terminal_file(self):
        """Worker DevOps recebe [terminal, file]."""
        devops_tools = TOOLSET_MAP.get("DevOps", [])
        self.assertIn("terminal", devops_tools)
        self.assertIn("file", devops_tools)

    def test_default_fallback_exists(self):
        """Fallback 'default' existe."""
        default_tools = TOOLSET_MAP.get("default", [])
        self.assertIn("terminal", default_tools)
        self.assertIn("file", default_tools)

    def test_tool_count_within_ceiling(self):
        """Nenhum papel excede o ceiling de ferramentas."""
        for role, tools in TOOLSET_MAP.items():
            self.assertLessEqual(len(tools), 3,
                                 f"{role} tem {len(tools)} tools, ceiling=3")

    def test_all_toolsets_are_lists(self):
        """Todos os valores são listas de strings."""
        for role, tools in TOOLSET_MAP.items():
            self.assertIsInstance(tools, list, f"{role} não é lista")
            for t in tools:
                self.assertIsInstance(t, str, f"{role} tool não é string: {t}")


if __name__ == "__main__":
    unittest.main()
