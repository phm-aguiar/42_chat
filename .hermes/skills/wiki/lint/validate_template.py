#!/usr/bin/env python3
"""validate_template.py — Audita frontmatter de páginas wiki contra template.md.

Uso:
  python3 validate_template.py                  # audita vault, FAIL só em quebra real
  python3 validate_template.py --wiki-dir <path>
  python3 validate_template.py --strict          # + WARNs viram FAIL

Exit code: 0 = nenhum FAIL, 1 = algum FAIL
"""

import argparse, os, re, sys
from datetime import datetime, date

REQUIRED_ALL = ["title", "tags", "created"]
REQUIRED_BY_DIR = {
    "concepts": ["category"],
    "references": ["category", "summary", "updated"],
    "skills": ["category", "summary"],
    "journal": ["category"],
}
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def find_md_files(wiki_dir: str) -> list[str]:
    files = []
    for root, _, fnames in os.walk(wiki_dir):
        for f in fnames:
            if f.endswith(".md"):
                files.append(os.path.join(root, f))
    return sorted(files)


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    import yaml
    if not text.startswith("---"):
        return None, "não começa com ---"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "--- sem fechamento"
    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        return None, f"YAML inválido: {e}"
    if not isinstance(fm, dict):
        return None, f"tipo inesperado: {type(fm).__name__}"
    return fm, ""


def get_dir_category(relpath: str) -> str:
    parts = relpath.split(os.sep)
    return parts[0] if len(parts) > 1 else "root"


def validate_iso_date(val) -> bool:
    if isinstance(val, (datetime, date)):
        return True
    if isinstance(val, str):
        return bool(ISO_DATE_RE.match(val.strip().strip('"')))
    return False


def validate_file(filepath: str, wiki_dir: str) -> tuple[list[str], list[str]]:
    """Retorna (errors, warnings). errors = quebra real, warnings = campos novos ausentes."""
    rel = os.path.relpath(filepath, wiki_dir)
    errors = []
    warnings = []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fm, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
        return errors, warnings

    # Tier 1: obrigatórios — QUEBRAM (FAIL)
    for field in REQUIRED_ALL:
        if field not in fm or not fm[field]:
            errors.append(f"campo obrigatório ausente: {field}")

    if "tags" in fm:
        tags = fm["tags"]
        if not isinstance(tags, list):
            errors.append(f"tags deve ser lista, recebeu {type(tags).__name__}")
        elif len(tags) == 0:
            errors.append("tags é lista vazia")

    if "created" in fm and fm["created"]:
        if not validate_iso_date(fm["created"]):
            errors.append(f"created não é data válida: {fm['created']}")

    # Tier 2: por diretório — AVISAM (WARN, viram FAIL com --strict)
    dir_cat = get_dir_category(rel)
    if dir_cat in REQUIRED_BY_DIR:
        for field in REQUIRED_BY_DIR[dir_cat]:
            if field not in fm or not fm[field]:
                warnings.append(f"campo recomendado para {dir_cat}/: {field}")

    if "updated" in fm and fm["updated"]:
        if not validate_iso_date(fm["updated"]):
            warnings.append(f"updated não é data válida: {fm['updated']}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Valida frontmatter wiki contra template.md")
    parser.add_argument("--wiki-dir", default="wiki")
    parser.add_argument("--strict", action="store_true", help="WARNs viram FAIL")
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki_dir)
    if not os.path.isdir(wiki_dir):
        print(f"ERRO: diretório não encontrado: {wiki_dir}", file=sys.stderr)
        sys.exit(1)

    files = find_md_files(wiki_dir)
    total = len(files)
    errors_found = 0
    warnings_found = 0

    for fpath in files:
        errs, warns = validate_file(fpath, wiki_dir)
        rel = os.path.relpath(fpath, wiki_dir)
        for e in errs:
            print(f"  FAIL: {rel}: {e}")
            errors_found += 1
        for w in warns:
            if args.strict:
                print(f"  FAIL: {rel}: {w}")
                errors_found += 1
            else:
                warnings_found += 1

    print(f"\n{total} páginas: {errors_found} FAIL(s), {warnings_found} WARN(s)")
    if args.strict:
        sys.exit(0 if errors_found == 0 else 1)
    else:
        sys.exit(0 if errors_found == 0 else 1)


if __name__ == "__main__":
    main()
