#!/usr/bin/env python3
"""
T015 — cli_distill.py: CLI para destilação de chunks canônicos.

Clusteriza chunks por similaridade semântica, gera padrões canônicos via LLM
e atualiza o índice SQLite com os novos chunks (embedding + inserção) e
downscoring (score=0) dos chunks originais de cada cluster.

Uso:
    hermes wiki distill [--threshold 0.85] [--dry-run]
"""

import argparse
import hashlib
import os
import sqlite3
import sys
import time

# ── Importa módulos da feature 002 ──────────────────────────────────────────
# Executados a partir do diretório do módulo (imports diretos como os outros CLI)

from cluster import cluster_chunks
from distill import distill_clusters
from store import DB_PATH, create_tables, insert_chunk

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(
        "Erro: sentence-transformers não está instalado.\n"
        "Instale com: pip install sentence-transformers",
        file=sys.stderr,
    )
    sys.exit(1)


# ── Constantes ──────────────────────────────────────────────────────────────

MODEL_NAME = "all-MiniLM-L6-v2"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    """Retorna o hash SHA256 hex de uma string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _format_duration(seconds: float) -> str:
    """Formata duração em formato legível."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(seconds, 60)
    return f"{int(m)}m {s:.0f}s"


def _format_size(size_bytes: int) -> str:
    """Formata tamanho em bytes para formato legível."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ── Destilação ──────────────────────────────────────────────────────────────

def distill_index(
    similarity_threshold: float,
    model: "SentenceTransformer",
    dry_run: bool = False,
) -> dict:
    """
    Executa clusterização + destilação + atualização do índice.

    Fluxo:
    1. Clusteriza todos os chunks com embedding via cluster_chunks().
    2. Para cada cluster, gera um chunk canônico via distill_clusters() (LLM).
    3. Insere cada chunk canônico no SQLite com embedding (SentenceTransformer).
    4. Marca os chunks originais de cada cluster com score=0 (não deleta).

    Args:
        similarity_threshold: Limiar para clusterização gulosa (padrão: 0.85).
        model: Instância do SentenceTransformer já carregada.
        dry_run: Se True, apenas simula sem escrever no banco.

    Returns:
        Dicionário com estatísticas: clusters, before, canonical, after,
        downscored.
    """
    # ── 1. Clusterização ─────────────────────────────────────────────────
    print(f"Clusterizando chunks (threshold={similarity_threshold})...")
    clusters = cluster_chunks(similarity_threshold=similarity_threshold)

    if not clusters:
        print("  ⚠️  Nenhum cluster encontrado (sem chunks com embedding?).")
        return {
            "clusters": 0,
            "before": 0,
            "canonical": 0,
            "after": 0,
            "downscored": 0,
        }

    total_before = sum(len(c) for c in clusters)
    print(f"  {len(clusters)} clusters formados "
          f"({total_before} chunks total)")

    # ── 2. Destilação ────────────────────────────────────────────────────
    print("Destilando padrões canônicos via LLM...")
    canonicals = distill_clusters(clusters)
    print(f"  {len(canonicals)} padrões canônicos gerados")

    # ── dry-run: apenas preview ──────────────────────────────────────────
    if dry_run:
        print(f"\n{'─' * 60}")
        print("[DRY-RUN] Operações que seriam realizadas:")
        print(f"{'─' * 60}\n")

        for i, c in enumerate(canonicals):
            print(f"  ➤ Inserir: {c['heading']} "
                  f"(score={c['score']:.3f}, "
                  f"de {c['_original_cluster_size']} chunks)")
            sources = ", ".join(c["_original_sources"][:3])
            if len(c["_original_sources"]) > 3:
                sources += " ..."
            print(f"      Fontes: {sources}")
            preview = c["content"][:120].replace("\n", " ")
            print(f"      Preview: {preview}...")
            print()

        print(f"  ➤ Marcar {total_before} chunks originais com score=0")
        print(f"{'─' * 60}")

        return {
            "clusters": len(clusters),
            "before": total_before,
            "canonical": len(canonicals),
            "after": total_before + len(canonicals),
            "downscored": total_before,
        }

    # ── 3. Insere chunks canônicos no SQLite ─────────────────────────────
    inserted = 0
    for i, canonical in enumerate(canonicals):
        content = canonical["content"]
        chunk_hash = _sha256(content)

        # Gera embedding para o conteúdo canônico
        embedding_bytes = None
        if content:
            try:
                embedding_arr = model.encode(
                    content,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
                embedding_bytes = embedding_arr.tobytes()
            except Exception as exc:
                print(f"  ⚠️  Falha ao gerar embedding para "
                      f"'{canonical['heading']}': {exc}")

        # Monta dicionário compatível com store.insert_chunk()
        # distill_clusters() retorna 'heading'; store espera 'heading_path'
        chunk_dict = {
            "source": canonical["source"],
            "heading_path": canonical["heading"],
            "content": content,
            "content_hash": chunk_hash,
            "char_count": len(content),
            "tags": canonical.get("tags", []),
        }

        insert_chunk(chunk_dict, embedding_bytes)
        inserted += 1

    print(f"  {inserted} chunks canônicos inseridos no índice")

    # ── 4. Marca chunks originais com score=0 ────────────────────────────
    downscored = 0
    conn = sqlite3.connect(DB_PATH)
    try:
        for cluster in clusters:
            for chunk in cluster:
                chunk_id = chunk.get("id")
                if chunk_id is not None:
                    conn.execute(
                        "UPDATE chunks SET score = 0.0, "
                        "last_updated = datetime('now') "
                        "WHERE id = ?",
                        (chunk_id,),
                    )
                    downscored += 1
        conn.commit()
    finally:
        conn.close()

    print(f"  {downscored} chunks originais marcados com score=0")

    return {
        "clusters": len(clusters),
        "before": total_before,
        "canonical": len(canonicals),
        "after": total_before + len(canonicals),
        "downscored": downscored,
    }


# ── Relatório ───────────────────────────────────────────────────────────────

def print_report(stats: dict, dry_run: bool, elapsed: float) -> None:
    """Exibe relatório final da destilação."""
    print()
    print("=" * 60)
    print("RELATÓRIO DE DESTILAÇÃO")
    print("=" * 60)

    if dry_run:
        print("⚠️  MODO DRY-RUN — NENHUM DADO FOI ESCRITO NO BANCO")

    print(f"  Clusters formados       : {stats['clusters']}")
    print(f"  Chunks antes            : {stats['before']}")
    print(f"  Padrões canônicos       : {stats['canonical']}")
    print(f"  Chunks no banco (total) : {stats['after']}")
    print(f"  Chunks com score=0      : {stats['downscored']}")

    if stats["before"] > 0:
        reduction = (1 - stats["canonical"] / stats["before"]) * 100
        direction = "redução" if reduction >= 0 else "expansão"
        print(f"  % de {direction}          : {abs(reduction):.1f}%")

    print(f"  Tempo total             : {_format_duration(elapsed)}")

    # Estatísticas do banco (apenas se não for dry-run)
    if not dry_run:
        try:
            from store import get_stats
            db_stats = get_stats()
            print(f"  Total chunks no banco   : {db_stats['total_chunks']}")
            print(f"  Chunks com embedding    : {db_stats['chunks_with_embedding']}")
            print(f"  Tamanho do banco        : "
                  f"{_format_size(db_stats['db_size_bytes'])}")
        except Exception as exc:
            print(f"  (stats do banco indisponíveis: {exc})")

    print("=" * 60)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Destila chunks canônicos a partir de clusters semânticos "
                    "da memória experiencial wiki.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Limiar de similaridade para clusterização (padrão: 0.85). "
             "Usado apenas no modo guloso (fallback sem sklearn).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas simula a destilação, sem escrever no banco.",
    )
    args = parser.parse_args()

    # Verifica se o banco existe
    if not os.path.exists(DB_PATH):
        print(
            "Índice não encontrado. Execute 'hermes wiki index --full' primeiro.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Inicializa o banco (cria tabelas/índices se não existirem)
    if not args.dry_run:
        create_tables()

    # Carrega o modelo SentenceTransformer
    print(f"Carregando modelo '{MODEL_NAME}' ...", end=" ", flush=True)
    model = SentenceTransformer(MODEL_NAME)
    print("OK")
    print()

    start_time = time.time()

    # Executa a destilação
    stats = distill_index(
        similarity_threshold=args.threshold,
        model=model,
        dry_run=args.dry_run,
    )

    elapsed = time.time() - start_time

    # Relatório final
    print_report(stats, args.dry_run, elapsed)


if __name__ == "__main__":
    main()
