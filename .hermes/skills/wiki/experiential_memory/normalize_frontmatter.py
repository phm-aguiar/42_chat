#!/usr/bin/env python3
"""
normalize_frontmatter.py — Adiciona YAML frontmatter MÍNIMO aos docs da wiki
que ainda não possuem bloco `---` no início.

Feature 003 — Hybrid Retrieval (T006)
"""

import argparse
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def filename_to_title(filepath: str) -> str:
    """Extrai title do nome do arquivo: sem extensão .md, underscores → espaços,
    capitaliza primeira letra de cada palavra."""
    basename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(basename)[0]
    # underscores → espaços
    text = name_no_ext.replace("_", " ").replace("-", " ")
    # Capitaliza primeira letra de cada palavra
    words = text.split()
    if not words:
        return name_no_ext
    title = " ".join(w.capitalize() for w in words)
    return title


def infer_tags(filepath: str, wiki_root: str) -> list[str]:
    """Infere tags a partir do diretório relativo à raiz wiki/.

    Regras:
      references/toolkits/<name>/… → [<name>, reference]
      skills/…                    → [skill]
      concepts/…                  → [concept]
      references/… (fora de toolkits) → [reference]
      projects/…                  → [project]
      journal/…                   → [journal]
      synthesis/…                 → [synthesis]
      _raw/…                      → [raw]
      _meta/…                     → [meta]
      Fallback                     → [wiki]
    """
    rel = os.path.relpath(filepath, wiki_root)
    parts = rel.replace("\\", "/").split("/")

    # references/toolkits/<toolkit>/...
    if len(parts) >= 3 and parts[0] == "references" and parts[1] == "toolkits":
        toolkit = parts[2]
        return [toolkit, "reference"]

    # skills/
    if len(parts) >= 1 and parts[0] == "skills":
        return ["skill"]

    # concepts/
    if len(parts) >= 1 and parts[0] == "concepts":
        return ["concept"]

    # references/ (não toolkits)
    if len(parts) >= 1 and parts[0] == "references":
        return ["reference"]

    # projects/
    if len(parts) >= 1 and parts[0] == "projects":
        return ["project"]

    # journal/
    if len(parts) >= 1 and parts[0] == "journal":
        return ["journal"]

    # synthesis/
    if len(parts) >= 1 and parts[0] == "synthesis":
        return ["synthesis"]

    # _raw/
    if len(parts) >= 1 and parts[0] == "_raw":
        return ["raw"]

    # _meta/
    if len(parts) >= 1 and parts[0] == "_meta":
        return ["meta"]

    # Raiz da wiki
    return ["wiki"]


def has_frontmatter(filepath: str) -> bool:
    """Retorna True se o arquivo começa com '---'."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            first_line = fh.readline()
            return first_line.strip() == "---"
    except (OSError, UnicodeDecodeError):
        return True  # não processa arquivos problemáticos


def get_iso_date(filepath: str) -> str:
    """Data de modificação do arquivo no formato ISO (YYYY-MM-DD)."""
    mtime = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_frontmatter(filepath: str, wiki_root: str) -> str:
    """Constrói bloco YAML frontmatter mínimo."""
    title = filename_to_title(filepath)
    tags = infer_tags(filepath, wiki_root)
    created = get_iso_date(filepath)

    # Formata tags como lista YAML inline: [tag1, tag2]
    tags_yaml = "[" + ", ".join(tags) + "]"

    fm = (
        "---\n"
        f'title: "{title}"\n'
        f"tags: {tags_yaml}\n"
        f"created: {created}\n"
        "---\n"
    )
    return fm


def process_file(filepath: str, wiki_root: str, dry_run: bool = False) -> bool:
    """Adiciona frontmatter a um arquivo. Retorna True se processado."""
    fm = build_frontmatter(filepath, wiki_root)

    if dry_run:
        print(f"[DRY-RUN] {filepath}")
        print(f"  → {fm.split(chr(10))[1].strip()}")  # linha title
        return True

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            original = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[ERRO] Não foi possível ler {filepath}: {exc}", file=sys.stderr)
        return False

    new_content = fm + original

    try:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print(f"[OK] {filepath}")
        return True
    except OSError as exc:
        print(f"[ERRO] Não foi possível escrever {filepath}: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adiciona YAML frontmatter mínimo a docs wiki sem '---' inicial."
    )
    parser.add_argument(
        "--wiki-root",
        default=None,
        help="Diretório raiz da wiki (default: <cwd>/wiki)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas reporta, não modifica arquivos",
    )
    args = parser.parse_args()

    # Determina raiz da wiki
    if args.wiki_root:
        wiki_root = os.path.abspath(args.wiki_root)
    else:
        wiki_root = os.path.join(os.getcwd(), "wiki")

    if not os.path.isdir(wiki_root):
        print(f"[ERRO] Diretório wiki não encontrado: {wiki_root}", file=sys.stderr)
        sys.exit(1)

    # Coleta todos os .md
    md_files: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(wiki_root):
        for fn in filenames:
            if fn.endswith(".md"):
                md_files.append(os.path.join(dirpath, fn))

    # Filtra os que NÃO têm frontmatter
    to_process = [f for f in md_files if not has_frontmatter(f)]

    if not to_process:
        print("Nenhum documento sem frontmatter encontrado.")
        return

    print(f"Encontrados {len(to_process)} docs sem frontmatter.")
    if args.dry_run:
        print("Modo DRY-RUN — nada será modificado.\n")

    processed = 0
    errors = 0

    for filepath in sorted(to_process):
        ok = process_file(filepath, wiki_root, dry_run=args.dry_run)
        if ok:
            processed += 1
        else:
            errors += 1

    # Relatório final
    print(f"\n{processed} docs processados, {errors} erros")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
