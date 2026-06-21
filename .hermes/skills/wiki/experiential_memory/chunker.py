"""
T002 — chunker.py: Quebra documentos Markdown em chunks por seções (headings ##)
com fallback para parágrafos. Cada chunk recebe metadados e hash SHA256.
"""

import hashlib
import re
from typing import Optional


# ── Constantes ──────────────────────────────────────────────────────────────

MAX_CHUNK_SIZE = 4096        # chars máximos por chunk
MIN_CHUNK_SIZE = 50          # chunks menores que isso são ignorados
HEADING_SPLIT_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    """Retorna o hash SHA256 hex de uma string."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _heading_level(line: str) -> int:
    """Retorna o nível do heading (1-6) ou 0 se não for heading."""
    m = HEADING_SPLIT_RE.match(line)
    return len(m.group(1)) if m else 0


def _heading_text(line: str) -> Optional[str]:
    """Retorna o texto do heading ou None."""
    m = HEADING_SPLIT_RE.match(line)
    return m.group(2).strip() if m else None


def _subdivide_large_chunk(content: str, heading_path: str, source: str,
                           tags: list[str]) -> list[dict]:
    """Subdivide um chunk > MAX_CHUNK_SIZE em pedaços menores por parágrafos."""
    paragraphs = re.split(r'\n\s*\n', content)
    chunks = []
    current = ''
    for para in paragraphs:
        para_stripped = para.strip()
        if not para_stripped:
            continue
        if current:
            candidate = current + '\n\n' + para_stripped
        else:
            candidate = para_stripped

        if len(candidate) <= MAX_CHUNK_SIZE:
            current = candidate
        else:
            # Salva o acumulado (se houver) e começa novo chunk
            if current and len(current) >= MIN_CHUNK_SIZE:
                chunks.append(_make_chunk(current, heading_path, source, tags))
            # Se o parágrafo sozinho é maior que MAX_CHUNK_SIZE, força split
            if len(para_stripped) > MAX_CHUNK_SIZE:
                for i in range(0, len(para_stripped), MAX_CHUNK_SIZE):
                    sub = para_stripped[i:i + MAX_CHUNK_SIZE]
                    if len(sub) >= MIN_CHUNK_SIZE:
                        chunks.append(_make_chunk(sub, heading_path, source, tags))
                current = ''
            else:
                current = para_stripped

    if current and len(current) >= MIN_CHUNK_SIZE:
        chunks.append(_make_chunk(current, heading_path, source, tags))

    return chunks


def _make_chunk(content: str, heading_path: str, source: str,
                tags: list[str]) -> dict:
    """Cria um dicionário de chunk padronizado."""
    return {
        'content': content,
        'heading_path': heading_path,
        'source': source,
        'content_hash': _sha256(content),
        'char_count': len(content),
        'tags': tags,
    }


# ── API pública ─────────────────────────────────────────────────────────────

def chunk_markdown(text: str, source_path: str) -> list[dict]:
    """
    Quebra um documento Markdown em chunks por headings de nível 2 (##).

    Estratégia:
    1. Divide o texto por headings `##`. Headings internos (###, ####, etc.)
       são preservados como parte do heading_path hierárquico.
    2. Fallback: se não houver headings `##`, divide por parágrafos (linhas em
       branco).
    3. Chunks > 4096 caracteres são subdivididos respeitando parágrafos.
    4. Chunks < 50 caracteres são ignorados.

    Args:
        text: Conteúdo Markdown completo.
        source_path: Caminho do arquivo fonte (ex: 'docs/guia.md').

    Returns:
        Lista de dicts com chaves: content, heading_path, source,
        content_hash, char_count, tags.
    """
    if not text or not text.strip():
        return []

    lines = text.split('\n')
    has_h2 = any(
        _heading_level(line) == 2 for line in lines
    )

    if has_h2:
        return _chunk_by_headings(text, source_path)
    else:
        return _chunk_by_paragraphs(text, source_path)


def _chunk_by_headings(text: str, source_path: str) -> list[dict]:
    """Divide o texto por headings ## com hierarquia de sub-headings."""
    lines = text.split('\n')
    chunks: list[dict] = []

    # heading_stack: [(nível, texto), ...] mantendo o caminho hierárquico
    heading_stack: list[tuple[int, str]] = []
    current_lines: list[str] = []
    current_h2_path = ''  # caminho até o ## atual (sem sub-headings)

    def flush_current():
        nonlocal current_lines, current_h2_path
        content = '\n'.join(current_lines).strip()
        if content and len(content) >= MIN_CHUNK_SIZE:
            if len(content) > MAX_CHUNK_SIZE:
                chunks.extend(
                    _subdivide_large_chunk(content, current_h2_path,
                                           source_path, [])
                )
            else:
                chunks.append(
                    _make_chunk(content, current_h2_path, source_path, [])
                )
        current_lines = []

    # Primeira passada: coleta conteúdo até o primeiro ##
    pre_h2_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        level = _heading_level(line)
        if level == 2:
            break
        pre_h2_lines.append(line)
        i += 1

    # Se há conteúdo antes do primeiro ##, trata como heading_path vazio
    if pre_h2_lines:
        content = '\n'.join(pre_h2_lines).strip()
        if content and len(content) >= MIN_CHUNK_SIZE:
            if len(content) > MAX_CHUNK_SIZE:
                chunks.extend(
                    _subdivide_large_chunk(content, '', source_path, [])
                )
            else:
                chunks.append(_make_chunk(content, '', source_path, []))

    # Processa o resto do documento
    while i < len(lines):
        line = lines[i]
        level = _heading_level(line)

        if level == 2:
            flush_current()
            h2_text = _heading_text(line) or ''
            heading_stack = [(2, h2_text)]
            current_h2_path = h2_text
            current_lines = [line]  # inclui o heading no conteúdo
        elif level >= 3 and heading_stack:
            # Atualiza heading_stack: remove níveis >= atual, adiciona o novo
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            h_text = _heading_text(line) or ''
            heading_stack.append((level, h_text))
            # Reconstrói heading_path completo
            current_h2_path = ' > '.join(h[1] for h in heading_stack)
            current_lines.append(line)
        else:
            current_lines.append(line)

        i += 1

    # Último chunk
    flush_current()

    return chunks


def _chunk_by_paragraphs(text: str, source_path: str) -> list[dict]:
    """Fallback: divide o texto por parágrafos (linhas em branco)."""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks: list[dict] = []
    current = ''
    heading_path = ''

    for para in paragraphs:
        para_stripped = para.strip()
        if not para_stripped:
            continue

        if current:
            candidate = current + '\n\n' + para_stripped
        else:
            candidate = para_stripped

        if len(candidate) <= MAX_CHUNK_SIZE:
            current = candidate
        else:
            if current and len(current) >= MIN_CHUNK_SIZE:
                chunks.append(_make_chunk(current, heading_path, source_path, []))
            if len(para_stripped) > MAX_CHUNK_SIZE:
                for i in range(0, len(para_stripped), MAX_CHUNK_SIZE):
                    sub = para_stripped[i:i + MAX_CHUNK_SIZE]
                    if len(sub) >= MIN_CHUNK_SIZE:
                        chunks.append(_make_chunk(sub, heading_path, source_path, []))
                current = ''
            else:
                current = para_stripped

    if current and len(current) >= MIN_CHUNK_SIZE:
        chunks.append(_make_chunk(current, heading_path, source_path, []))

    return chunks
