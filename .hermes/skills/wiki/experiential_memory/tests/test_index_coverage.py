"""
T017 — Smoke test de cobertura: 100% docs indexados.

Verifica se todos os documentos .md da wiki estão representados
como DISTINCT source no índice SQLite.

Contexto: Feature 002 - Wiki Experiential Memory.
"""

import sys
from pathlib import Path

# ── Ajuste de import path ───────────────────────────────────────────────
# Permite importar store.py do pacote experiential_memory
_HERE = Path(__file__).resolve().parent
_PKG = _HERE.parent  # .hermes/skills/wiki/experiential_memory/
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from store import get_stats

# ── Constantes ───────────────────────────────────────────────────────────
# Caminho absoluto da wiki (raiz do projeto 42_Framework)
_PROJECT_ROOT = Path(__file__).resolve().parents[5]  # sobe 5 níveis até 42_Framework/
WIKI_DIR = _PROJECT_ROOT / "wiki"


def count_wiki_md() -> int:
    """Conta arquivos .md na wiki via Path.rglob (recursivo)."""
    return sum(1 for _ in WIKI_DIR.rglob("*.md"))


def count_indexed_sources() -> int:
    """Conta DISTINCT source no SQLite usando store.get_stats()."""
    stats = get_stats()
    return stats["total_sources"]


def test_full_coverage():
    """
    Smoke test: todos os .md da wiki devem estar indexados.

    Assert: COUNT(DISTINCT source) == COUNT(wiki/**/*.md).
    """
    wiki_count = count_wiki_md()
    indexed_count = count_indexed_sources()

    assert wiki_count == indexed_count, (
        f"Cobertura incompleta: {wiki_count} docs na wiki, "
        f"mas apenas {indexed_count} sources distintos no índice. "
        f"Faltam {wiki_count - indexed_count} docs."
    )


def test_coverage_is_100_percent():
    """Verifica que a cobertura é exatamente 100%."""
    wiki_count = count_wiki_md()
    indexed_count = count_indexed_sources()

    if wiki_count > 0:
        coverage = indexed_count / wiki_count
        assert coverage == 1.0, (
            f"Cobertura: {coverage:.1%} ({indexed_count}/{wiki_count}). "
            f"Esperado: 100%."
        )
    else:
        # Se não há docs na wiki, cobertura é vacuamente 100%
        assert indexed_count == 0, (
            f"Wiki vazia mas índice tem {indexed_count} sources — inconsistente."
        )


# ── Execução direta (útil para smoke manual) ────────────────────────────
if __name__ == "__main__":
    wiki = count_wiki_md()
    indexed = count_indexed_sources()
    coverage = (indexed / wiki * 100) if wiki > 0 else 100.0

    print(f"Wiki  .md files: {wiki}")
    print(f"Indexed sources: {indexed}")
    print(f"Coverage:        {coverage:.1f}%")

    if wiki == indexed:
        print("\n✅ 100% coverage — todos os docs indexados.")
        sys.exit(0)
    else:
        print(f"\n❌ Cobertura incompleta! Faltam {wiki - indexed} docs.")
        sys.exit(1)
