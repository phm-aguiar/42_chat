#!/usr/bin/env python3
"""
T006 — cli_query.py: CLI para consulta semântica ao índice wiki.

Busca chunks similares via cosine similarity e exibe resultados formatados.

Uso:
    hermes wiki query --semantic "texto da consulta" --top-k N
    hermes wiki query --semantic "texto da consulta" --hybrid --top-k N
"""

import argparse
import sys
import time
from pathlib import Path

from search import search_similar

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(
        "Erro: sentence-transformers não está instalado.\n"
        "Instale com: pip install sentence-transformers",
        file=sys.stderr,
    )
    sys.exit(1)

from store import DB_PATH as _DB_PATH_STR

# ── Constantes ──────────────────────────────────────────────────────────────

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = Path(_DB_PATH_STR)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _format_duration(seconds: float) -> str:
    """Formata duração em formato legível."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        m, s = divmod(seconds, 60)
        return f"{int(m)}m {s:.0f}s"


def _truncate(text: str, max_chars: int = 150) -> str:
    """Trunca texto em max_chars caracteres, adicionando '...' se necessário."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def _combined_score(similarity: float, score: float) -> float:
    """Calcula score combinado = score * similarity."""
    return score * similarity


# ── Query ───────────────────────────────────────────────────────────────────

def query_wiki(
    semantic_text: str,
    top_k: int,
    model: "SentenceTransformer",
    hybrid: bool = False,
) -> list[dict]:
    """
    Executa busca semântica e retorna resultados.

    Args:
        semantic_text: Texto da consulta.
        top_k: Número máximo de resultados.
        model: Instância carregada do SentenceTransformer.
        hybrid: Se True, ativa modo híbrido (cosine + BM25).

    Returns:
        Lista de resultados (dicionários) retornada por search_similar.
    """
    return search_similar(
        query_text=semantic_text,
        model=model,
        k=top_k,
        hybrid=hybrid,
    )


# ── Exibição ────────────────────────────────────────────────────────────────

def print_results(results: list[dict], elapsed: float, hybrid: bool = False) -> None:
    """
    Exibe os resultados da busca formatados.

    Formato (semantic):
        [combined_score] source > heading: primeiros 150 chars do content...

    Formato (hybrid):
        [cosine cos + bm25 bm25 = hybrid_score hybrid] source > heading: primeiros 150 chars do content...
    """
    if not results:
        print("\nNenhum resultado encontrado para esta consulta.")
        return

    print(f"\n{'=' * 70}")
    mode_label = "HÍBRIDA" if hybrid else "SEMÂNTICA"
    print(f"RESULTADOS DA BUSCA {mode_label}  ({len(results)} encontrado(s) em {_format_duration(elapsed)})")
    print(f"{'=' * 70}\n")

    for i, r in enumerate(results, start=1):
        source = r.get("source", "(sem fonte)")
        heading = r.get("heading", "")
        content_preview = _truncate(r.get("content", ""), 150)

        if hybrid:
            # Modo híbrido: exibe cosine + bm25 = hybrid_score
            cos_raw = r.get("similarity", 0.0)
            bm25_raw = r.get("bm25_score", 0.0)
            hybrid_score = r.get("hybrid_score", 0.0)
            sim_pct = cos_raw * 100

            print(f"[{cos_raw:.3f} cos + {bm25_raw:.3f} bm25 = {hybrid_score:.3f} hybrid] {source}", end="")
            if heading:
                print(f" > {heading}", end="")
            print()
        else:
            # Modo semântico: exibe combined_score
            combined = _combined_score(r["similarity"], r["score"])
            sim_pct = r["similarity"] * 100

            print(f"[{combined:.3f}] {source}", end="")
            if heading:
                print(f" > {heading}", end="")
            print()

        # Linha 2: content preview
        print(f"    {content_preview}")
        if sim_pct < 10.0:
            print(f"    ⚠️  similaridade baixa: {sim_pct:.1f}%")
        print()


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consulta semântica ao índice wiki.",
    )
    parser.add_argument(
        "--semantic",
        type=str,
        required=True,
        help="Texto da consulta em linguagem natural.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Número máximo de resultados (padrão: 5).",
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        default=False,
        help="Modo híbrido: combina cosine similarity (semântica) com BM25 "
             "(lexical). Exibe scores individuais e combinado.",
    )
    args = parser.parse_args()

    # Verifica se o índice (banco) existe
    if not DB_PATH.exists():
        print(
            "Índice não encontrado. Execute:\n"
            "  python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full --wiki-dir wiki/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Verifica se há chunks com embedding no banco
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"
        ).fetchone()[0]
    finally:
        conn.close()

    if count == 0:
        print(
            "Índice vazio (sem embeddings). Execute:\n"
            "  python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full --wiki-dir wiki/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Carrega o modelo
    print(f"Carregando modelo '{MODEL_NAME}' ...", end=" ", flush=True)
    model = SentenceTransformer(MODEL_NAME)
    print("OK")

    # Executa a query
    mode_str = " (modo híbrido)" if args.hybrid else ""
    print(f"Buscando: \"{args.semantic}\"{mode_str}")
    start_time = time.time()
    results = query_wiki(
        semantic_text=args.semantic,
        top_k=args.top_k,
        model=model,
        hybrid=args.hybrid,
    )
    elapsed = time.time() - start_time

    # Exibe resultados
    print_results(results, elapsed, hybrid=args.hybrid)


if __name__ == "__main__":
    main()
