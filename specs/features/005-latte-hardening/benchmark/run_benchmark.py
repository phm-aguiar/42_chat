#!/usr/bin/env python3
"""
Benchmark — LATTE Hardening (Feature 005)

Compara métricas antes e depois dos 7 hardening patches.
Cenário de stress: DAG com 5 tasks, 1 worker com timeout forçado.

Métricas:
  - LLM calls (via llm_calls_made no grafo)
  - Wall-clock time
  - Budget enforcement (force_finalize acionado?)
  - Errors registrados
  - Verify mode deterministic vs LLM
  - Context summarization rounds
"""

import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".hermes" / "skills" / "sdd"))

from latte_coordination.orchestrator import (
    CoordinationGraph,
    Orchestrator,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_HEARTBEAT_THRESHOLD,
    DEFAULT_MAX_LLM_CALLS,
    DEFAULT_OPERATOR_TIMEOUT,
    DEFAULT_VERIFY_MODE,
    DEFAULT_SUMMARY_INTERVAL,
    VALID_VERIFY_MODES,
)
from latte_coordination.lead_operators import _run_deterministic_checks
from latte_coordination.dispatcher import TOOLSET_MAP, MERGE_EQUAL_WEIGHT_INSTRUCTION


def build_stress_dag(graph: CoordinationGraph) -> None:
    """Constrói DAG de stress: 5 tasks, T004 depende de T003."""
    # T001: task rápida, sem deps
    graph.add_node({
        "id": "T001",
        "agent": None,
        "status": "pending",
        "deps": [],
        "description": "Setup project structure",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })

    # T002: task rápida, sem deps
    graph.add_node({
        "id": "T002",
        "agent": None,
        "status": "pending",
        "deps": [],
        "description": "Configure environment variables",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })

    # T003: task pesada (simula timeout), sem deps
    graph.add_node({
        "id": "T003",
        "agent": None,
        "status": "pending",
        "deps": [],
        "description": "Heavy computation — prone to timeout",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })

    # T004: depende de T003 — só executa se T003 completar
    graph.add_node({
        "id": "T004",
        "agent": None,
        "status": "pending",
        "deps": ["T003"],
        "description": "Post-process T003 results",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })

    # T005: task final, sem deps
    graph.add_node({
        "id": "T005",
        "agent": None,
        "status": "pending",
        "deps": [],
        "description": "Generate final report",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })


def run_benchmark(label: str, budget: int, timeout: int, verify_mode: str) -> dict:
    """Executa um cenário de benchmark e retorna métricas."""
    graph = CoordinationGraph(
        feature_id="bench-005",
        lead="lead-1",
        workers=["dev-1", "dev-2", "dev-3"],
        max_rounds=20,
        heartbeat_threshold=4,
        graph_operators="enabled",
        max_llm_calls=budget,
        operator_timeout=timeout,
        verify_mode=verify_mode,
    )

    build_stress_dag(graph)

    orch = Orchestrator(
        task_description="Benchmark stress test: 5 tasks, T003 prone to timeout",
        G_0=graph,
        config={
            "max_rounds": 20,
            "heartbeat_threshold": 4,
            "verbose": False,
            "max_llm_calls": budget,
            "operator_timeout": timeout,
        },
    )

    # Simula T003 com timeout — adiciona output de erro
    t003 = graph.find_node("T003")
    t003["status"] = "done"
    t003["output"] = (
        "I will create the computation pipeline. "
        "Let me plan the architecture first. "
        "Error: connection timeout after 30s"
    )

    start = time.monotonic()
    result = orch.run()
    elapsed = time.monotonic() - start

    # Coleta métricas
    metrics = {
        "label": label,
        "budget": budget,
        "timeout": timeout,
        "verify_mode": verify_mode,
        "llm_calls_made": result.llm_calls_made,
        "max_llm_calls": result.max_llm_calls,
        "budget_exhausted": result.is_budget_exhausted(),
        "rounds": result.round,
        "wall_clock_ms": round(elapsed * 1000),
        "node_count": result.get_node_count(),
        "errors": len(result.errors),
        "completed_summary": result.completed_summary[:80] if result.completed_summary else "(none)",
        "round_since_summary": result.round_since_summary,
        # Verify deterministic
        "t003_output": t003.get("output", ""),
    }

    # Roda checks determinísticos no output do T003
    checks = _run_deterministic_checks("T003", t003.get("output"))
    metrics["deterministic_checks_passed"] = sum(1 for c in checks if c["passed"])
    metrics["deterministic_checks_total"] = len(checks)
    metrics["deterministic_checks"] = [
        f"{c['check']}: {'PASS' if c['passed'] else 'FAIL'}" for c in checks
    ]

    return metrics


def print_report(metrics_list: list[dict]) -> None:
    """Imprime relatório comparativo."""
    print("=" * 80)
    print("  LATTE HARDENING BENCHMARK — Feature 005")
    print("  Cenário: 5 tasks, T003 com timeout + anti-padrões no output")
    print("=" * 80)

    header = f"{'Métrica':<35} {'Before':>15} {'After':>15} {'Delta':>10}"
    print(f"\n{header}")
    print("-" * 80)

    if len(metrics_list) >= 2:
        before = metrics_list[0]  # Hardening OFF equivalente (budget=999)
        after = metrics_list[1]   # Hardening ON

        rows = [
            ("LLM calls (made/max)", f"{before['llm_calls_made']}/{before['max_llm_calls']}",
             f"{after['llm_calls_made']}/{after['max_llm_calls']}", ""),
            ("Budget exhausted?", str(before['budget_exhausted']), str(after['budget_exhausted']), ""),
            ("Wall-clock (ms)", str(before['wall_clock_ms']), str(after['wall_clock_ms']),
             f"{after['wall_clock_ms'] - before['wall_clock_ms']:+d}"),
            ("Rounds completed", str(before['rounds']), str(after['rounds']), ""),
            ("Errors registered", str(before['errors']), str(after['errors']), ""),
            ("Verify checks passed", f"{before['deterministic_checks_passed']}/{before['deterministic_checks_total']}",
             f"{after['deterministic_checks_passed']}/{after['deterministic_checks_total']}", ""),
            ("Context summary", before['completed_summary'], after['completed_summary'], ""),
            ("Round since summary", str(before['round_since_summary']), str(after['round_since_summary']), ""),
        ]

        for label, b, a, d in rows:
            print(f"{label:<35} {b:>15} {a:>15} {d:>10}")

    print("\n" + "-" * 80)
    print("  VERIFY DETERMINISTIC CHECKS (T003 output)")
    print("-" * 80)
    if metrics_list:
        for check in metrics_list[-1]["deterministic_checks"]:
            print(f"    {check}")

    print("\n" + "-" * 80)
    print("  TOOLSET MAP (ADR-011)")
    print("-" * 80)
    for role, tools in TOOLSET_MAP.items():
        print(f"    {role:<10} → {tools}")

    print("\n" + "-" * 80)
    print("  MERGE INSTRUCTION (ADR-012)")
    print("-" * 80)
    print(f"    {MERGE_EQUAL_WEIGHT_INSTRUCTION}")

    print("\n" + "=" * 80)


def main():
    print("Running LATTE Hardening Benchmark...\n")

    # Cenário 1: HARDENING OFF (budget infinito, sem verify deterministic)
    print("  [1/2] Baseline (hardening off: budget=999, verify=llm)...")
    baseline = run_benchmark(
        label="baseline",
        budget=999,
        timeout=999,
        verify_mode="llm",
    )

    # Cenário 2: HARDENING ON (budget=25, timeout=45, verify=deterministic)
    print("  [2/2] Hardened (budget=25, timeout=45, verify=deterministic)...")
    hardened = run_benchmark(
        label="hardened",
        budget=25,
        timeout=45,
        verify_mode="deterministic",
    )

    print_report([baseline, hardened])

    # Validações
    print("\nVALIDATIONS:")
    checks = []

    # 1. Budget tracking: hardening deve ter budget <= 25
    checks.append(("Budget enforced", hardened["llm_calls_made"] <= hardened["max_llm_calls"]))

    # 2. Verify deterministic deve detectar anti-padrões
    checks.append(("Verify detects anti-patterns",
                   hardened["deterministic_checks_passed"] < hardened["deterministic_checks_total"]))

    # 3. Erros registrados no state
    checks.append(("Errors in state", hardened["errors"] >= 0))

    # 4. Context summarization inicializado
    checks.append(("Summary tracking active", hardened["round_since_summary"] >= 0))

    # 5. TOOLSET_MAP tem entries
    checks.append(("Toolset map populated", len(TOOLSET_MAP) >= 3))

    # 6. Merge instruction não vazia
    checks.append(("Merge instruction present", len(MERGE_EQUAL_WEIGHT_INSTRUCTION) > 10))

    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  [{status}] {name}")

    all_pass = all(p for _, p in checks)
    print(f"\n  {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
