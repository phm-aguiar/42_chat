#!/usr/bin/env python3
"""fix_frontmatter.py — Corrige YAML quebrado e title ausente nas páginas da wiki.

Uso:
  python3 fix_frontmatter.py --dry-run          # preview sem modificar
  python3 fix_frontmatter.py                     # aplicar correções
  python3 fix_frontmatter.py --wiki-dir <path>   # vault path (default: wiki/)
"""

import argparse
import os
import re
import sys
from pathlib import Path


def find_md_files(wiki_dir: str) -> list[str]:
    """Retorna paths absolutos de todos os .md no vault."""
    files = []
    for root, _, fnames in os.walk(wiki_dir):
        for f in fnames:
            if f.endswith(".md"):
                files.append(os.path.join(root, f))
    return sorted(files)


def parse_frontmatter(text: str) -> tuple[bool, str, str, str]:
    """Parse YAML frontmatter de um arquivo .md.

    Returns:
        (has_fm, fm_text, body, error_msg)
        has_fm: True se frontmatter encontrado e parseável
        fm_text: texto bruto do frontmatter (entre os ---)
        body: resto do arquivo após o segundo ---
        error_msg: string vazia se OK, descrição do erro se inválido
    """
    if not text.startswith("---"):
        return False, "", text, "não começa com ---"

    # Encontra o segundo ---
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, parts[1] if len(parts) > 1 else "", "", "--- sem fechamento"

    fm_text = parts[1]
    body = parts[2]

    # Verifica se o YAML é parseável (checagem leve — sem pyyaml)
    # Detecta o erro comum: valor string com : não escapado
    broken_lines = []
    for i, line in enumerate(fm_text.split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Se o valor contém ':' e não está entre aspas, é YAML quebrado
        if ":" in value and not (value.startswith('"') and value.endswith('"')):
            if not (value.startswith("[") and value.endswith("]")):  # lista YAML
                if not (value.startswith("{") and value.endswith("}")):  # dict YAML
                    broken_lines.append((i, line, key, value))

    if broken_lines:
        return True, fm_text, body, f"YAML com : não escapado em {len(broken_lines)} linha(s)"
    return True, fm_text, body, ""


def fix_unescaped_colons(fm_text: str) -> tuple[str, int]:
    """Envolve em aspas duplas valores string que contêm : não escapado.

    Returns:
        (fm_text_corrigido, num_correcoes)
    """
    lines = fm_text.split("\n")
    fixed = 0
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        if ":" not in stripped:
            new_lines.append(line)
            continue

        # Separa chave: valor preservando indentação
        indent = line[: len(line) - len(line.lstrip())]
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        # Pula listas YAML, dicionários, números, booleans
        if not value:
            new_lines.append(line)
            continue
        if value.startswith("[") or value.startswith("{"):
            new_lines.append(line)
            continue
        if value.lower() in ("true", "false", "yes", "no", "null", "~"):
            new_lines.append(line)
            continue
        try:
            float(value)
            new_lines.append(line)
            continue
        except ValueError:
            pass

        # Se o valor contém ':' e não está entre aspas → YAML quebrado
        if ":" in value and not (value.startswith('"') and value.endswith('"')):
            # Escapa aspas internas se houver
            escaped_value = value.replace('"', '\\"')
            new_lines.append(f'{indent}{key}: "{escaped_value}"')
            fixed += 1
        else:
            new_lines.append(line)

    return "\n".join(new_lines), fixed


def derive_title(filepath: str, body: str) -> str:
    """Deriva título do primeiro H1 ou do nome do arquivo."""
    # Tenta primeiro H1
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()

    # Fallback: nome do arquivo
    stem = Path(filepath).stem
    # Converte hífens/underscores → espaços, title case
    title = stem.replace("-", " ").replace("_", " ")
    # Title case simples
    title = " ".join(
        w[0].upper() + w[1:] if w and w[0].islower() else w for w in title.split()
    )
    return title


def ensure_field(fm_text: str, field: str, value: str) -> tuple[str, bool]:
    """Garante que um campo exista no frontmatter. Insere 'title' no topo (após ---).

    Returns:
        (fm_text_atualizado, foi_adicionado)
    """
    # Se o campo já existe, não mexe
    if re.search(rf"^{field}:", fm_text, re.MULTILINE):
        return fm_text, False

    # Insere no topo do frontmatter (posição canônica para title)
    lines = fm_text.split("\n")
    # Pula linhas vazias iniciais
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip():
            insert_at = i
            break

    indent = ""
    new_lines = lines[:insert_at] + [f'{indent}{field}: "{value}"'] + lines[insert_at:]
    return "\n".join(new_lines), True


def process_file(filepath: str, dry_run: bool) -> dict:
    """Processa um arquivo: corrige YAML escapando + garante title.

    Returns:
        dict com: path, had_issues, fixes_applied, dry_run
    """
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    has_fm, fm_text, body, error = parse_frontmatter(original)
    result = {"path": filepath, "had_issues": False, "fixes": [], "dry_run": dry_run}

    if not has_fm:
        result["had_issues"] = True
        result["error"] = error
        return result

    # Corrige : não escapado
    fixed_fm, colon_fixes = fix_unescaped_colons(fm_text)
    if colon_fixes > 0:
        result["had_issues"] = True
        result["fixes"].append(f"escapou {colon_fixes} valor(es) com ':' não escapado")
        fm_text = fixed_fm

    # Garante title
    title_added = 0
    if not re.search(r"^title:", fm_text, re.MULTILINE):
        derived = derive_title(filepath, body)
        fm_text, added = ensure_field(fm_text, "title", derived)
        if added:
            result["had_issues"] = True
            result["fixes"].append(f"adicionou title: '{derived}'")
            title_added = 1

    if not result["had_issues"]:
        return result

    # Reconstrói arquivo
    new_content = f"---{fm_text}---{body}"

    if dry_run:
        result["preview"] = _diff_summary(original, new_content)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return result


def _diff_summary(original: str, new: str) -> str:
    """Resumo textual do diff (sem dependência de lib externa)."""
    orig_lines = original.split("\n")
    new_lines = new.split("\n")
    changes = []
    for i, (o, n) in enumerate(zip(orig_lines, new_lines)):
        if o != n:
            changes.append(f"  L{i+1}: {o.strip()[:80]} → {n.strip()[:80]}")
    # Linhas adicionadas no final
    if len(new_lines) > len(orig_lines):
        for i in range(len(orig_lines), len(new_lines)):
            changes.append(f"  +L{i+1}: {new_lines[i].strip()[:80]}")
    return "\n".join(changes[:10])  # limita a 10 mudanças


def main():
    parser = argparse.ArgumentParser(
        description="Corrige YAML frontmatter quebrado na wiki"
    )
    parser.add_argument(
        "--wiki-dir",
        default="wiki",
        help="Diretório do vault Obsidian (default: wiki/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas preview, não modifica arquivos",
    )
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki_dir)
    if not os.path.isdir(wiki_dir):
        print(f"ERRO: diretório não encontrado: {wiki_dir}", file=sys.stderr)
        sys.exit(1)

    files = find_md_files(wiki_dir)
    print(f"Processando {len(files)} arquivos em {wiki_dir}...")
    if args.dry_run:
        print(">>> MODO DRY-RUN — nenhum arquivo será modificado <<<\n")

    total_issues = 0
    total_fixes = 0

    for fpath in files:
        result = process_file(fpath, args.dry_run)
        if result.get("error"):
            rel = os.path.relpath(fpath, wiki_dir)
            print(f"  ERRO: {rel} — {result['error']}")
            total_issues += 1
        elif result["had_issues"]:
            rel = os.path.relpath(fpath, wiki_dir)
            fixes_str = "; ".join(result["fixes"])
            print(f"  {rel}: {fixes_str}")
            total_issues += 1
            total_fixes += len(result["fixes"])
            if "preview" in result:
                print(result["preview"])

    print(f"\n{'DRY-RUN: ' if args.dry_run else ''}"
          f"{total_issues} arquivo(s) com problemas, "
          f"{total_fixes} correções {'simuladas' if args.dry_run else 'aplicadas'}")

    sys.exit(0 if total_issues == 0 else 0)  # nunca falha, só reporta


if __name__ == "__main__":
    main()
