#!/usr/bin/env python3
"""sync_scores.py — Reflete scores do índice SQLite no frontmatter da wiki.

Lê o banco ~/.hermes/wiki_index.db, agrupa chunks por source (path da wiki),
calcula score médio por página, e escreve `rag_score` no frontmatter.

Uso:
  python3 sync_scores.py                    # atualiza todas as páginas
  python3 sync_scores.py --wiki-dir <path>  # vault path
  python3 sync_scores.py --dry-run          # preview, sem modificar
"""

import argparse, json, os, re, sqlite3, sys
from collections import defaultdict
from datetime import datetime, timezone


DB_PATH = os.path.expanduser("~/.hermes/wiki_index.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_scores_by_source() -> dict[str, dict]:
    """Retorna {source_path: {count, avg_score, min_score, max_score, top_tags}}."""
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT source, COUNT(*) as cnt,
                   ROUND(AVG(score), 4) as avg_score,
                   ROUND(MIN(score), 4) as min_score,
                   ROUND(MAX(score), 4) as max_score
            FROM chunks
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY avg_score DESC
        """).fetchall()

        result = {}
        for row in rows:
            result[row["source"]] = {
                "chunk_count": row["cnt"],
                "rag_score": row["avg_score"],
                "min_score": row["min_score"],
                "max_score": row["max_score"],
            }
        return result
    finally:
        conn.close()


def find_md_files(wiki_dir: str) -> list[str]:
    files = []
    for root, _, fnames in os.walk(wiki_dir):
        for f in fnames:
            if f.endswith(".md") and not f.endswith(".bak"):
                files.append(os.path.join(root, f))
    return sorted(files)


def sync_file(filepath: str, wiki_dir: str, scores: dict, dry_run: bool) -> dict:
    """Sincroniza rag_score no frontmatter de um arquivo."""
    rel = os.path.relpath(filepath, wiki_dir)
    result = {"path": rel, "action": "skip"}

    # Busca score no índice — match pelo path relativo
    page_score = scores.get(rel)
    if page_score is None:
        return result

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return result

    parts = content.split("---", 2)
    if len(parts) < 3:
        return result

    fm_text = parts[1]
    body = parts[2]
    new_score = page_score["rag_score"]

    # Verifica se rag_score já existe e tem o mesmo valor
    existing_match = re.search(r"^rag_score:\s*(.+)$", fm_text, re.MULTILINE)
    if existing_match:
        try:
            existing_val = float(existing_match.group(1).strip().strip('"'))
            if abs(existing_val - new_score) < 0.001:
                return result  # já atualizado
        except ValueError:
            pass

    # Remove rag_score antigo se existir
    fm_lines = fm_text.split("\n")
    new_lines = [l for l in fm_lines if not re.match(r"^rag_score:", l.strip())]

    # Insere rag_score após updated ou created
    inserted = False
    final_lines = []
    for line in new_lines:
        final_lines.append(line)
        if not inserted and re.match(r"^(updated|created):", line.strip()):
            final_lines.append(f'rag_score: {new_score}')
            inserted = True

    if not inserted:
        final_lines.append(f'rag_score: {new_score}')

    new_fm = "\n".join(final_lines)
    new_content = f"---{new_fm}---{body}"

    result["action"] = "update"
    result["rag_score"] = new_score
    result["chunk_count"] = page_score["chunk_count"]

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return result


def main():
    parser = argparse.ArgumentParser(description="Sincroniza scores SQLite → wiki frontmatter")
    parser.add_argument("--wiki-dir", default="wiki")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki_dir)
    if not os.path.isdir(wiki_dir):
        print(f"ERRO: diretório não encontrado: {wiki_dir}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(DB_PATH):
        print("ERRO: índice SQLite não encontrado. Rode cli_index.py --full primeiro.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(">>> MODO DRY-RUN <<<\n")

    scores = get_scores_by_source()
    print(f"Índice: {len(scores)} páginas com scores")

    files = find_md_files(wiki_dir)
    updated = 0
    skipped = 0
    total_chunks = 0

    for fpath in files:
        result = sync_file(fpath, wiki_dir, scores, args.dry_run)
        if result["action"] == "update":
            updated += 1
            total_chunks += result["chunk_count"]
            print(f"  {result['path']}: rag_score={result['rag_score']} ({result['chunk_count']} chunks)")
        else:
            skipped += 1

    print(f"\n{'DRY-RUN: ' if args.dry_run else ''}"
          f"{updated} páginas atualizadas, {skipped} sem score no índice")

    sys.exit(0)


if __name__ == "__main__":
    main()
