#!/usr/bin/env python3
"""chunk_split.py — Divide arquivos grandes da wiki em sub-páginas por seção.

Lê thresholds de wiki/_meta/chunking.yaml. Para cada arquivo que exceder
max_lines ou max_bytes, split por headings ## e cria sub-páginas com
frontmatter herdado + _index.md.

Uso:
  python3 chunk_split.py --dry-run           # preview sem modificar
  python3 chunk_split.py                      # aplicar split
  python3 chunk_split.py --file <path>        # splitar arquivo específico
  python3 chunk_split.py --wiki-dir <path>    # vault path
"""

import argparse
import os
import re
import sys
from pathlib import Path


def load_config(wiki_dir: str) -> dict:
    config_path = os.path.join(wiki_dir, "_meta", "chunking.yaml")
    if not os.path.exists(config_path):
        print("ERRO: chunking.yaml não encontrado em wiki/_meta/", file=sys.stderr)
        sys.exit(1)

    import yaml
    with open(config_path) as f:
        return yaml.safe_load(f)


def split_by_headings(text: str, level: str = "##") -> list[tuple[str, str]]:
    """Divide texto por headings de um nível específico.

    Returns:
        list of (heading_text, section_content)
    """
    pattern = rf"^{level} (.+)$"
    sections = []
    current_heading = "_intro"
    current_content = []

    for line in text.split("\n"):
        m = re.match(pattern, line)
        if m:
            if current_content or current_heading != "_intro":
                sections.append((current_heading, "\n".join(current_content)))
            current_heading = m.group(1).strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content or current_heading != "_intro":
        sections.append((current_heading, "\n".join(current_content)))

    return sections


def slugify(text: str) -> str:
    """Converte heading em slug para nome de arquivo."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def extract_frontmatter_body(text: str) -> tuple[str, str, str]:
    """Extrai frontmatter bruto, corpo, e texto do frontmatter."""
    if not text.startswith("---"):
        return "", "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", "", text
    return parts[1], parts[2], parts[1]  # fm_text, body, fm_text (dup for compat)


def process_file(filepath: str, config: dict, wiki_dir: str, dry_run: bool) -> dict:
    """Processa um arquivo: split se exceder thresholds.

    Returns:
        dict com status e ações tomadas
    """
    max_lines = config["thresholds"]["max_lines"]
    max_bytes = config["thresholds"]["max_bytes"]
    min_subpage = config["split"]["min_subpage_lines"]
    exclude = config.get("exclude_dirs", [])
    subpage_add = config.get("subpage_frontmatter", {}).get("add", {})
    preserve_fields = config.get("subpage_frontmatter", {}).get("preserve", [])
    post_action = config.get("post_split", {}).get("action", "archive")
    archive_suffix = config.get("post_split", {}).get("archive_suffix", ".bak")

    rel = os.path.relpath(filepath, wiki_dir)
    dir_cat = rel.split(os.sep)[0] if os.sep in rel else "root"
    if dir_cat in exclude:
        return {"path": rel, "action": "skip", "reason": f"diretório excluído: {dir_cat}"}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.count("\n") + 1
    size = len(content.encode("utf-8"))

    if lines <= max_lines and size <= max_bytes:
        return {"path": rel, "action": "skip", "reason": "dentro dos thresholds"}

    # Parse frontmatter
    fm_text, body, _ = extract_frontmatter_body(content)
    if not fm_text:
        return {"path": rel, "action": "skip", "reason": "sem frontmatter"}

    # Parse frontmatter como dict para herdar campos
    import yaml
    try:
        fm_dict = yaml.safe_load(fm_text)
    except Exception:
        return {"path": rel, "action": "skip", "reason": "YAML inválido"}

    if not isinstance(fm_dict, dict):
        return {"path": rel, "action": "skip", "reason": "frontmatter não é dict"}

    # Encontra o corpo após o frontmatter
    body_start = content.find("---", 3) + 3
    body_text = content[body_start:].lstrip("\n")

    # Split por headings — usa level default ou override por diretório
    split_on = config["split"]["level"]
    per_dir = config["split"].get("per_dir", {})
    # Tenta match mais específico primeiro (ex: tools/golangci-lint)
    for dir_prefix in sorted(per_dir.keys(), key=len, reverse=True):
        if rel.startswith(dir_prefix) or rel.startswith(dir_prefix + "/"):
            split_on = per_dir[dir_prefix]
            break

    sections = split_by_headings(body_text, split_on)
    if len(sections) < 2:
        return {"path": rel, "action": "skip", "reason": f"apenas {len(sections)} seções"}

    # Filtra seções muito curtas
    valid_sections = []
    carry = []
    for heading, section_text in sections:
        section_lines = section_text.count("\n") + 1
        if section_lines < min_subpage and heading != "_intro":
            carry.append(f"## {heading}\n{section_text}")
        else:
            if carry:
                section_text = "\n".join(carry) + "\n" + section_text
                carry = []
            valid_sections.append((heading, section_text))

    if len(valid_sections) < 2:
        return {"path": rel, "action": "skip", "reason": f"apenas {len(valid_sections)} seções válidas"}

    # Cria diretório de saída
    parent_dir = os.path.dirname(filepath)
    stem = Path(filepath).stem
    out_dir = os.path.join(parent_dir, stem.lower().replace(" ", "-"))
    out_dir_rel = os.path.relpath(out_dir, wiki_dir)

    subpages = []
    index_entries = []

    for heading, section_text in valid_sections:
        slug = slugify(heading) if heading != "_intro" else "overview"
        if not slug:
            slug = f"section-{len(subpages)+1}"

        # Constrói frontmatter da sub-página
        sub_fm = {}
        for field in preserve_fields:
            if field in fm_dict:
                sub_fm[field] = fm_dict[field]
        sub_fm["title"] = heading if heading != "_intro" else fm_dict.get("title", stem)

        # Adiciona campos de rastreamento
        for k, v in subpage_add.items():
            sub_fm[k] = v.replace("{original_path}", rel)

        # Serializa frontmatter
        sub_fm_lines = []
        for k, v in sub_fm.items():
            if isinstance(v, str):
                sub_fm_lines.append(f'{k}: "{v}"')
            elif isinstance(v, list):
                sub_fm_lines.append(f"{k}: {v}")
            else:
                sub_fm_lines.append(f"{k}: {v}")

        subpage_content = f"---\n" + "\n".join(sub_fm_lines) + f"\n---\n\n# {heading}\n\n{section_text}"
        subpage_path = os.path.join(out_dir, f"{slug}.md")
        subpages.append((subpage_path, subpage_content))

        # Entrada do índice
        desc_line = section_text.strip().split("\n")[0] if section_text.strip() else heading
        desc_line = desc_line[:120]
        index_entries.append(f"- [[{out_dir_rel}/{slug}|{heading}]]: {desc_line}")

    # Cria _index.md
    original_title = fm_dict.get("title", stem)
    index_fm = {}
    for field in preserve_fields:
        if field in fm_dict:
            index_fm[field] = fm_dict[field]
    index_fm["title"] = f"{original_title} — Índice"
    index_fm["tags"] = fm_dict.get("tags", []) + ["index"]

    index_fm_lines = [f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}" for k, v in index_fm.items()]
    index_content = (
        f"---\n" + "\n".join(index_fm_lines) + f"\n---\n\n"
        f"# {original_title} — Índice\n\n"
        f"> Documento original splitado em {len(subpages)} sub-páginas.\n"
        f"> Fonte: [[{rel}]]\n\n"
        + "\n".join(index_entries)
    )
    index_path = os.path.join(out_dir, "_index.md")
    subpages.append((index_path, index_content))

    result = {
        "path": rel,
        "action": "split",
        "lines": lines,
        "size": size,
        "subpages": len(subpages) - 1,  # -1 pelo _index
        "out_dir": out_dir_rel,
        "dry_run": dry_run,
    }

    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
        for spath, scontent in subpages:
            with open(spath, "w", encoding="utf-8") as f:
                f.write(scontent)

        # Pós-split: arquiva ou deleta original
        if post_action == "archive":
            os.rename(filepath, filepath + archive_suffix)
            result["archived"] = filepath + archive_suffix
        elif post_action == "delete":
            os.remove(filepath)
            result["deleted"] = True

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Divide arquivos grandes da wiki em sub-páginas"
    )
    parser.add_argument("--wiki-dir", default="wiki", help="Diretório do vault")
    parser.add_argument("--dry-run", action="store_true", help="Preview sem modificar")
    parser.add_argument("--file", help="Processar apenas um arquivo específico")
    args = parser.parse_args()

    wiki_dir = os.path.abspath(args.wiki_dir)
    if not os.path.isdir(wiki_dir):
        print(f"ERRO: diretório não encontrado: {wiki_dir}", file=sys.stderr)
        sys.exit(1)

    config = load_config(wiki_dir)

    if args.dry_run:
        print(">>> MODO DRY-RUN — nenhum arquivo será modificado <<<\n")

    if args.file:
        filepath = os.path.abspath(args.file)
        result = process_file(filepath, config, wiki_dir, args.dry_run)
        print_result(result, wiki_dir)
    else:
        # Processa todos os .md
        files = []
        for root, _, fnames in os.walk(wiki_dir):
            for f in fnames:
                if f.endswith(".md"):
                    files.append(os.path.join(root, f))

        split_count = 0
        skip_count = 0
        for fpath in sorted(files):
            result = process_file(fpath, config, wiki_dir, args.dry_run)
            if result["action"] == "split":
                split_count += 1
                print_result(result, wiki_dir)
            else:
                skip_count += 1

        print(f"\n{'DRY-RUN: ' if args.dry_run else ''}"
              f"{split_count} split(s), {skip_count} skip(s)")


def print_result(result, wiki_dir):
    if result["action"] == "split":
        print(f"  SPLIT: {result['path']} "
              f"({result['lines']} linhas, {result['size']} bytes) "
              f"→ {result['subpages']} sub-páginas em {result['out_dir']}/")
    elif result["action"] == "skip":
        pass  # silencioso


if __name__ == "__main__":
    main()
