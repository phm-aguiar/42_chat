#!/usr/bin/env python3
"""
T004 — cli_index.py: CLI para indexação da wiki no banco de memória experiencial.

Percorre wiki/, chunka documentos Markdown, gera embeddings com
SentenceTransformer('all-MiniLM-L6-v2') e insere no SQLite.

Uso:
    hermes wiki index --full          # indexação completa
    hermes wiki index --full --dry-run  # preview sem escrever no banco
"""

import argparse
import os
import sys
import time
from pathlib import Path

from chunker import chunk_markdown
from store import create_tables, insert_chunk, get_stats

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
WIKI_DIR = Path("wiki")  # relativo ao cwd
DB_DIR = Path.home() / ".hermes"
DB_PATH = DB_DIR / "wiki_index.db"

# Garante que o model sabe onde está o banco (consistência com store.py)
os.environ.setdefault("HERMES_WIKI_DB", str(DB_PATH))


# ── Helpers ─────────────────────────────────────────────────────────────────

def _format_duration(seconds: float) -> str:
    """Formata duração em formato legível."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{int(m)}m {s:.0f}s"
    else:
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{int(h)}h {int(m)}m {s:.0f}s"


def _format_size(size_bytes: int) -> str:
    """Formata tamanho em bytes para formato legível."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _collect_md_files(wiki_dir: Path) -> list[Path]:
    """Coleta todos os arquivos .md recursivamente em wiki_dir."""
    if not wiki_dir.is_dir():
        print(f"Erro: diretório wiki/ não encontrado em {wiki_dir.absolute()}")
        sys.exit(1)

    md_files = sorted(wiki_dir.rglob("*.md"))
    if not md_files:
        print(f"Aviso: nenhum arquivo .md encontrado em {wiki_dir.absolute()}")
    return md_files


# ── Indexação ───────────────────────────────────────────────────────────────

def index_wiki(
    wiki_dir: Path,
    model: SentenceTransformer,
    dry_run: bool = False,
) -> dict:
    """
    Percorre wiki_dir, chunka, embedda e insere no SQLite.

    Args:
        wiki_dir: Caminho para o diretório wiki/.
        model: Instância do SentenceTransformer já carregada.
        dry_run: Se True, apenas simula sem escrever no banco.

    Returns:
        Dicionário com estatísticas da execução.
    """
    md_files = _collect_md_files(wiki_dir)
    total_files = len(md_files)

    if total_files == 0:
        return {
            "total_docs": 0,
            "total_chunks": 0,
            "total_embedded": 0,
            "skipped": 0,
            "errors": 0,
            "elapsed_seconds": 0,
        }

    total_chunks = 0
    total_embedded = 0
    skipped = 0
    errors = 0

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}"
          f"Indexando {total_files} arquivo(s) .md em {wiki_dir.absolute()}")
    print("Modelo:", MODEL_NAME)
    print("-" * 60)

    for idx, md_path in enumerate(md_files, start=1):
        rel_path = md_path.relative_to(wiki_dir)
        print(f"[{idx}/{total_files}] {rel_path} ...", end=" ", flush=True)

        try:
            # 1. Lê conteúdo
            content = md_path.read_text(encoding="utf-8")

            # 2. Chunka
            chunks = chunk_markdown(content, str(rel_path))
            file_chunks = len(chunks)

            if file_chunks == 0:
                print(f"0 chunks (vazio/pulou)")
                skipped += 1
                continue

            # 3. Embedda cada chunk
            embedded_count = 0
            for chunk in chunks:
                embedding_bytes = None
                if chunk.get("content"):
                    try:
                        embedding = model.encode(
                            chunk["content"],
                            convert_to_numpy=True,
                            show_progress_bar=False,
                        )
                        embedding_bytes = embedding.tobytes()
                    except Exception:
                        # Se falhar embedding, insere sem embedding
                        pass

                # 4. Insere no SQLite
                if not dry_run:
                    insert_chunk(chunk, embedding_bytes)

                total_chunks += 1
                if embedding_bytes is not None:
                    embedded_count += 1
                    total_embedded += 1

            print(f"{file_chunks} chunks ({embedded_count} embeddados)")

        except Exception as e:
            print(f"ERRO: {e}")
            errors += 1

    print("-" * 60)
    return {
        "total_docs": total_files,
        "total_chunks": total_chunks,
        "total_embedded": total_embedded,
        "skipped": skipped,
        "errors": errors,
    }


# ── Relatório final ─────────────────────────────────────────────────────────

def print_report(exec_stats: dict, dry_run: bool, elapsed: float) -> None:
    """Exibe relatório ao final da indexação."""
    print("\n" + "=" * 60)
    print("RELATÓRIO DE INDEXAÇÃO")
    print("=" * 60)

    if dry_run:
        print("⚠️  MODO DRY-RUN — NENHUM DADO FOI ESCRITO NO BANCO")

    print(f"  Documentos processados : {exec_stats['total_docs']}")
    print(f"  Chunks criados         : {exec_stats['total_chunks']}")
    print(f"  Chunks com embedding   : {exec_stats['total_embedded']}")
    print(f"  Documentos pulados     : {exec_stats['skipped']}")
    print(f"  Erros                  : {exec_stats['errors']}")
    print(f"  Tempo total            : {_format_duration(elapsed)}")

    if not dry_run:
        try:
            stats = get_stats()
            print(f"  Total chunks no banco  : {stats['total_chunks']}")
            print(f"  Fontes distintas       : {stats['total_sources']}")
            print(f"  Tamanho médio (chars)  : {stats['avg_char_count']}")
            print(f"  Chunks com embedding   : {stats['chunks_with_embedding']}")
            print(f"  Tamanho do banco       : {_format_size(stats['db_size_bytes'])}")
        except Exception as e:
            print(f"  (stats do banco indisponíveis: {e})")

    print("=" * 60)


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexa documentos da wiki/ no banco de memória experiencial.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=True,
        help="Indexação completa (padrão).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas simula a indexação, sem escrever no banco.",
    )
    parser.add_argument(
        "--wiki-dir",
        type=Path,
        default=WIKI_DIR,
        help=f"Caminho para o diretório wiki (padrão: {WIKI_DIR}).",
    )
    args = parser.parse_args()

    # Garante que o diretório pai do banco existe
    if not args.dry_run:
        DB_DIR.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    # Inicializa o banco (cria tabelas/índices se não existirem)
    if not args.dry_run:
        print("Inicializando banco de dados...")
        create_tables()
        print(f"Banco pronto: {DB_PATH}")

    # Carrega o modelo
    print(f"Carregando modelo '{MODEL_NAME}' ...", end=" ", flush=True)
    model = SentenceTransformer(MODEL_NAME)
    print("OK")

    # Indexa
    exec_stats = index_wiki(
        wiki_dir=args.wiki_dir,
        model=model,
        dry_run=args.dry_run,
    )

    elapsed = time.time() - start_time
    exec_stats["elapsed_seconds"] = elapsed

    # Relatório
    print_report(exec_stats, args.dry_run, elapsed)


if __name__ == "__main__":
    main()
