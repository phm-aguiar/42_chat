#!/usr/bin/env python3
"""
T022 — Smoke test de velocidade (speed) — Feature 002: Wiki Experiential Memory.

Mede tempos reais de indexação (--full) e consulta semântica (--semantic)
com margens generosas:

  - Index (--full):   assert < 300s (5 minutos)  — esperado ~75s
  - Query (--semantic): assert < 5s               — esperado ~350ms

Estratégia:
  - Index: subprocess (model loading é desprezível vs 75s de indexação).
  - Query: time.time() com import direto dos módulos, isolando o tempo
    de carregamento do modelo do tempo real de busca.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


# ── Constantes ──────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_EXP_MEM_DIR = _PROJECT_ROOT / ".hermes" / "skills" / "wiki" / "experiential-memory"
_WIKI_DIR = _PROJECT_ROOT / "wiki"

# Margens generosas conforme spec
INDEX_TIMEOUT_S = 300   # 5 minutos (esperado ~75s)
QUERY_TIMEOUT_S  = 5    # 5 segundos (esperado ~350ms)

# Adiciona o diretório dos módulos da feature 002 ao path
if str(_EXP_MEM_DIR) not in sys.path:
    sys.path.insert(0, str(_EXP_MEM_DIR))


# ── Helpers ─────────────────────────────────────────────────────────────────

def _run_index(cwd: Path) -> tuple[float, str, str, int]:
    """
    Executa `python3 cli_index.py --full --wiki-dir WIKI_DIR`
    e retorna (elapsed_seconds, stdout, stderr, exit_code).

    Usa subprocess porque o modelo é carregado uma vez e o custo
    é desprezível frente aos ~75s de indexação.
    """
    cmd = [
        sys.executable,
        str(_EXP_MEM_DIR / "cli_index.py"),
        "--full",
        "--wiki-dir", str(_WIKI_DIR),
    ]
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=INDEX_TIMEOUT_S + 30,  # folga sobre o assert
    )
    elapsed = time.time() - t0
    return elapsed, proc.stdout, proc.stderr, proc.returncode


# ── Tests ───────────────────────────────────────────────────────────────────

def test_index_speed() -> None:
    """
    Smoke test: indexação --full deve completar em menos de 5 minutos.

    Usa o diretório wiki/ real do projeto e o banco de produção
    (~/.hermes/wiki_index.db). Roda indexação completa via subprocess
    e verifica que o tempo ficou abaixo do limite generoso de 300s.
    """
    print("\n" + "=" * 70)
    print("T022 — SMOKE TEST: Index Speed (--full)")
    print("=" * 70)
    print(f"Wiki dir  : {_WIKI_DIR}")
    print(f"Exp. mem  : {_EXP_MEM_DIR}")
    print(f"Limite    : {INDEX_TIMEOUT_S}s ({INDEX_TIMEOUT_S / 60:.0f} min)")
    print("-" * 70)

    elapsed, stdout, stderr, rc = _run_index(cwd=_EXP_MEM_DIR)

    # Últimas linhas do stdout para diagnóstico rápido
    tail = "\n".join(stdout.strip().splitlines()[-15:]) if stdout else "(vazio)"

    print(f"Exit code : {rc}")
    print(f"Tempo real: {elapsed:.1f}s")
    if stderr and rc != 0:
        print(f"STDERR (últimas 20 linhas):")
        for line in stderr.strip().splitlines()[-20:]:
            print(f"  {line}")

    assert rc == 0, (
        f"Indexação falhou com exit code {rc}.\n"
        f"STDERR: {stderr[-1000:]}\n"
        f"STDOUT: {tail}"
    )

    assert elapsed < INDEX_TIMEOUT_S, (
        f"Indexação muito lenta: {elapsed:.1f}s "
        f"(limite: {INDEX_TIMEOUT_S}s = {INDEX_TIMEOUT_S / 60:.0f} min).\n"
        f"STDOUT: {tail}"
    )

    print(f"✅ Indexação completou em {elapsed:.1f}s (< {INDEX_TIMEOUT_S}s)")
    print("=" * 70)


def test_query_speed() -> None:
    """
    Smoke test: consulta --semantic deve completar em menos de 5 segundos.

    Assume que o índice já existe (~/.hermes/wiki_index.db). Usa time.time()
    com import direto dos módulos para isolar o tempo de carregamento do
    modelo SentenceTransformer do tempo real de busca semântica.

    Fluxo:
      1. Carrega o modelo SentenceTransformer (fora da medição).
      2. Mede o tempo de search_similar() (função pura de busca).
      3. Assert < 5s (margem generosa; esperado ~350ms).
    """
    print("\n" + "=" * 70)
    print("T022 — SMOKE TEST: Query Speed (--semantic)")
    print("=" * 70)
    print(f"Limite    : {QUERY_TIMEOUT_S}s")
    print("-" * 70)

    # ── 1. Importa e carrega o modelo (fora da medição) ─────────────────
    from sentence_transformers import SentenceTransformer
    from search import search_similar
    from store import DB_PATH

    MODEL_NAME = "all-MiniLM-L6-v2"

    # Verifica se o banco existe
    if not Path(DB_PATH).exists():
        raise FileNotFoundError(
            f"Índice não encontrado em {DB_PATH}. "
            f"Execute 'python3 cli_index.py --full' primeiro."
        )

    print(f"Carregando modelo '{MODEL_NAME}' ...", end=" ", flush=True)
    t_load_start = time.time()
    model = SentenceTransformer(MODEL_NAME)
    t_load = time.time() - t_load_start
    print(f"OK ({t_load:.1f}s)")

    # ── 2. Mede o tempo real da busca ──────────────────────────────────
    query_text = "coordenação de agentes"
    top_k = 3

    print(f"Buscando: \"{query_text}\" (top_k={top_k})")
    t0 = time.time()
    results = search_similar(
        query_text=query_text,
        model=model,
        k=top_k,
    )
    elapsed = time.time() - t0

    # ── 3. Reporta ─────────────────────────────────────────────────────
    print(f"Resultados: {len(results)} encontrado(s)")
    for i, r in enumerate(results[:3], start=1):
        combined = r["similarity"] * r.get("score", 0)
        source = r.get("source", "?")
        heading = r.get("heading", "")
        print(f"  [{i}] [{combined:.3f}] {source}" + (f" > {heading}" if heading else ""))

    print(f"Tempo real (busca): {elapsed * 1000:.0f}ms")

    assert len(results) > 0, (
        f"Nenhum resultado encontrado para '{query_text}'. "
        f"O índice está vazio ou corrompido."
    )

    assert elapsed < QUERY_TIMEOUT_S, (
        f"Consulta muito lenta: {elapsed * 1000:.0f}ms "
        f"(limite: {QUERY_TIMEOUT_S}s = {QUERY_TIMEOUT_S * 1000:.0f}ms)."
    )

    print(f"✅ Consulta completou em {elapsed * 1000:.0f}ms (< {QUERY_TIMEOUT_S * 1000:.0f}ms)")
    print("=" * 70)


# ── main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("T022 — Smoke Tests de Velocidade")
    print("Feature 002: Wiki Experiential Memory\n")

    test_index_speed()
    test_query_speed()

    print("\n✅ Todos os smoke tests de velocidade passaram.")
