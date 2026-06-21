#!/usr/bin/env python3
"""
T018: Smoke Test — Compatibilidade Reversa (Legacy Mode)
=========================================================

Verifica que o orquestrador LATTE aceita um tasks.md **sem** o campo
`graph-operators` no YAML frontmatter (modo legacy), mantendo
compatibilidade reversa com arquivos tasks.md antigos.

O teste:
  1. Cria um arquivo tasks.md fictício em disco (sem graph-operators)
  2. Chama load_G0_from_tasks_md() do orchestrator
  3. Verifica que retorna um G₀ válido (sem levantar exceção)
  4. Verifica que graph_operators default = 'disabled'
  5. Verifica que heartbeat_threshold default = 4
  6. Verifica que o grafo gerado é um DAG válido com as tasks do arquivo

Execução:
    cd .hermes/skills/sdd/latte_coordination/tests
    python test_legacy_compat.py
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from latte_coordination.orchestrator import (
    CoordinationGraph,
    load_G0_from_tasks_md,
)
from latte_coordination.frontier import compute_frontier

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

# Conteúdo de um tasks.md legacy típico — SEM graph-operators no frontmatter
LEGACY_TASKS_MD = """---
feature: 001-latte_coordination
heartbeat-threshold: 5
max-rounds: 20
---

# Tasks — Feature 001: LATTE Coordination

- [ ] **T001:** Criar estrutura base do módulo
  **agent:** Lead
  **depends_on:** []

- [ ] **T002:** Implementar orquestrador principal
  **agent:** Dev1
  **depends_on:** [T001]

- [ ] **T003:** Escrever testes de unidade
  **agent:** Dev2
  **depends_on:** [T002]

- [ ] **T004:** Documentar API pública
  **agent:** Dev1
  **depends_on:** [T002]
"""

# Conteúdo mínimo — sem frontmatter algum
MINIMAL_TASKS_MD = """# Tasks — Feature 001: Minimal

- [ ] **T001:** Tarefa única
  **agent:** Lead

- [ ] **T002:** Segunda tarefa
  **agent:** Dev1
  **depends_on:** [T001]
"""


def _is_valid_dag(graph: CoordinationGraph) -> bool:
    """
    Verifica que o grafo é um DAG válido (acíclico).

    Usa DFS com coloração (WHITE/GRAY/BLACK) para detecção de ciclos.
    Retorna True se o grafo for acíclico.
    """
    nodes = {n["id"]: n for n in graph.nodes}
    edges = {n["id"]: n.get("deps", []) for n in graph.nodes}

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {nid: WHITE for nid in nodes}

    def dfs(nid: str) -> bool:
        color[nid] = GRAY
        for dep in edges.get(nid, []):
            if dep not in color:
                continue  # dependência externa (não está no grafo)
            if color[dep] == GRAY:
                return False  # ciclo detectado
            if color[dep] == WHITE:
                if not dfs(dep):
                    return False
        color[nid] = BLACK
        return True

    for nid in nodes:
        if color[nid] == WHITE:
            if not dfs(nid):
                return False
    return True


# ──────────────────────────────────────────────────────────────────────────────
# TestCase
# ──────────────────────────────────────────────────────────────────────────────

class TestLegacyCompat(unittest.TestCase):
    """Smoke test T018: Compatibilidade reversa — tasks.md sem graph-operators."""

    def setUp(self):
        """Cria arquivos tasks.md temporários para cada cenário de teste."""
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_path = Path(self._tmpdir.name)

    def tearDown(self):
        """Remove diretório temporário."""
        self._tmpdir.cleanup()

    def _write_tasks_md(self, content: str, filename: str = "tasks.md") -> Path:
        """Escreve conteúdo em um arquivo tasks.md no diretório temporário."""
        path = self.tmpdir_path / filename
        path.write_text(content, encoding="utf-8")
        return path

    # ── Testes principais ─────────────────────────────────────────────────

    def test_load_legacy_tasks_md_without_graph_operators(self):
        """
        (1)+(3) Cria tasks.md fictício SEM graph-operators e carrega G₀.

        Verifica que load_G0_from_tasks_md() NÃO levanta exceção e
        retorna um CoordinationGraph válido.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)

        # Deve carregar sem ValueError (legacy mode é aceito)
        g0 = load_G0_from_tasks_md(tasks_path)

        # Verifica que o retorno é um CoordinationGraph
        self.assertIsInstance(
            g0, CoordinationGraph,
            "load_G0_from_tasks_md() deve retornar um CoordinationGraph"
        )

    def test_graph_operators_default_disabled(self):
        """
        (4) Verifica que graph_operators default = 'disabled' no modo legacy.

        Carrega um tasks.md sem graph-operators e confere que o campo
        graph_operators no grafo é 'disabled'.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        self.assertEqual(
            g0.graph_operators, "disabled",
            f"graph_operators deve ser 'disabled' no modo legacy, "
            f"mas é '{g0.graph_operators}'"
        )

    def test_heartbeat_threshold_default(self):
        """
        (5) Verifica que heartbeat-threshold default = 4 quando ausente.

        Usa um tasks.md mínimo (sem heartbeat-threshold no frontmatter)
        e confere que o default é 4.
        """
        tasks_path = self._write_tasks_md(MINIMAL_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        self.assertEqual(
            g0.heartbeat_threshold, 4,
            f"heartbeat_threshold default deve ser 4, "
            f"mas é {g0.heartbeat_threshold}"
        )

    def test_heartbeat_threshold_from_frontmatter(self):
        """
        Verifica que heartbeat-threshold do frontmatter é respeitado.

        O LEGACY_TASKS_MD define heartbeat-threshold: 5.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        self.assertEqual(
            g0.heartbeat_threshold, 5,
            f"heartbeat_threshold deve ser 5 (do frontmatter), "
            f"mas é {g0.heartbeat_threshold}"
        )

    def test_graph_is_valid_dag(self):
        """
        (6) Verifica que o grafo gerado é um DAG válido com as tasks do arquivo.

        - O grafo deve conter todas as tasks declaradas
        - O grafo deve ser acíclico (DAG válido)
        - As dependências devem estar corretas
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        # ── Verifica presença de todas as tasks ──────────────────────
        expected_tasks = {"T001", "T002", "T003", "T004"}
        actual_tasks = {n["id"] for n in g0.nodes}
        self.assertEqual(
            actual_tasks, expected_tasks,
            f"Tasks esperadas {expected_tasks}, obtidas {actual_tasks}"
        )

        # ── Verifica que é um DAG (acíclico) ────────────────────────
        self.assertTrue(
            _is_valid_dag(g0),
            "O grafo deve ser um DAG válido (acíclico)"
        )

        # ── Verifica contagem de nós e arestas ──────────────────────
        self.assertEqual(g0.get_node_count(), 4,
                         "Deve haver 4 nós (T001..T004)")
        # T001→T002, T002→T003, T002→T004 = 3 arestas
        self.assertEqual(g0.get_edge_count(), 3,
                         "Deve haver 3 arestas (T001→T002, T002→T003, T002→T004)")

    def test_dependencies_are_correct(self):
        """
        Verifica que as dependências inferidas estão corretas.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        expected_deps = {
            "T001": [],           # sem dependências (raiz)
            "T002": ["T001"],     # depende de T001
            "T003": ["T002"],     # depende de T002
            "T004": ["T002"],     # depende de T002
        }

        for node in g0.nodes:
            nid = node["id"]
            actual_deps = sorted(node.get("deps", []))
            expected = sorted(expected_deps.get(nid, []))
            self.assertEqual(
                actual_deps, expected,
                f"Dependências de {nid}: esperado {expected}, obtido {actual_deps}"
            )

    def test_frontier_works_on_legacy_dag(self):
        """
        Verifica que compute_frontier funciona corretamente no DAG legacy.

        A raiz (T001) deve ser o único nó no frontier inicial.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        frontier = compute_frontier(g0)
        self.assertEqual(
            frontier, ["T001"],
            f"Frontier inicial deve ser ['T001'], obtido {frontier}"
        )

    def test_agents_are_correct(self):
        """
        Verifica que os agentes são extraídos corretamente do tasks.md legacy.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        expected_agents = {
            "T001": "Lead",
            "T002": "Dev1",
            "T003": "Dev2",
            "T004": "Dev1",
        }

        for node in g0.nodes:
            nid = node["id"]
            self.assertEqual(
                node.get("agent"), expected_agents.get(nid),
                f"Agent de {nid}: esperado '{expected_agents.get(nid)}', "
                f"obtido '{node.get('agent')}'"
            )

    def test_all_nodes_start_pending(self):
        """
        Verifica que todos os nós começam com status 'pending'.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        for node in g0.nodes:
            self.assertEqual(
                node["status"], "pending",
                f"Nó {node['id']} deve estar 'pending', "
                f"mas está '{node['status']}'"
            )

    def test_workers_detected(self):
        """
        Verifica que os workers são detectados a partir dos agentes das tasks.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        # Dev1 e Dev2 devem ser detectados como workers
        self.assertIn("Dev1", g0.workers,
                      "Dev1 deve estar na lista de workers")
        self.assertIn("Dev2", g0.workers,
                      "Dev2 deve estar na lista de workers")
        # Lead não deve estar na lista de workers
        self.assertNotIn("Lead", g0.workers,
                         "Lead não deve estar na lista de workers")

    def test_lead_is_detected(self):
        """
        Verifica que o Lead é detectado a partir das tasks.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        self.assertEqual(g0.lead, "Lead",
                         f"Lead deve ser 'Lead', mas é '{g0.lead}'")

    def test_minimal_tasks_md(self):
        """
        Teste com tasks.md mínimo (sem frontmatter) — regressão.
        """
        tasks_path = self._write_tasks_md(MINIMAL_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        self.assertEqual(g0.get_node_count(), 2,
                         "Deve haver 2 nós no grafo mínimo")
        self.assertEqual(g0.graph_operators, "disabled",
                         "graph_operators deve ser 'disabled'")
        self.assertTrue(_is_valid_dag(g0),
                        "Grafo mínimo deve ser um DAG válido")

    def test_discover_history_entries(self):
        """
        Verifica que entradas Discover foram registradas no histórico
        para cada task carregada do tasks.md legacy.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        discover_ops = [
            h for h in g0.history if h["operator"] == "Discover"
        ]
        self.assertEqual(
            len(discover_ops), 4,
            f"Deve haver 4 Discover (1 por task), "
            f"encontrados {len(discover_ops)}"
        )

    def test_max_rounds_from_frontmatter(self):
        """
        Verifica que max_rounds do frontmatter é respeitado.
        """
        tasks_path = self._write_tasks_md(LEGACY_TASKS_MD)
        g0 = load_G0_from_tasks_md(tasks_path)

        # LEGACY_TASKS_MD define max-rounds: 20
        self.assertEqual(
            g0.max_rounds, 20,
            f"max_rounds deve ser 20 (do frontmatter), "
            f"mas é {g0.max_rounds}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("T018: Smoke Test — Compatibilidade Reversa (Legacy Mode)")
    print("=" * 65)
    unittest.main(verbosity=2)
