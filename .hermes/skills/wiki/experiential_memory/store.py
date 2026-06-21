"""
T003 — store.py: Persistência SQLite para chunks de documentos wiki.
Gerencia o banco ~/.hermes/wiki_index.db com schema para embeddings.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional


# ── Constantes ──────────────────────────────────────────────────────────────

DB_PATH = os.path.expanduser('~/.hermes/wiki_index.db')


# ── Schema ──────────────────────────────────────────────────────────────────

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY,
    source      TEXT,
    heading     TEXT,
    content     TEXT,
    embedding   BLOB,
    score       REAL DEFAULT 0.5,
    content_hash TEXT UNIQUE,
    tags        TEXT,
    char_count  INTEGER,
    created_at  TEXT,
    last_updated TEXT
)
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_content_hash ON chunks(content_hash)",
    "CREATE INDEX IF NOT EXISTS idx_source ON chunks(source)",
    "CREATE INDEX IF NOT EXISTS idx_score ON chunks(score)",
]


# ── Conexão ─────────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    """Retorna uma conexão SQLite com row_factory ativado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── API pública ─────────────────────────────────────────────────────────────

def create_tables() -> None:
    """
    Cria a tabela chunks e todos os índices se não existirem.
    Seguro para chamar múltiplas vezes (IF NOT EXISTS).
    Também executa migrações de schema (ex: adiciona last_updated).
    """
    conn = _get_conn()
    try:
        conn.execute(CREATE_TABLE_SQL)
        for idx_sql in CREATE_INDEXES_SQL:
            conn.execute(idx_sql)

        # ── Migrações de schema ─────────────────────────────────────────
        # Adiciona last_updated se a coluna não existir (bancos legados)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(chunks)").fetchall()}
        if 'last_updated' not in cols:
            conn.execute("ALTER TABLE chunks ADD COLUMN last_updated TEXT")
            # Preenche last_updated com created_at para registros existentes
            conn.execute(
                "UPDATE chunks SET last_updated = created_at "
                "WHERE last_updated IS NULL"
            )

        conn.commit()
    finally:
        conn.close()


def insert_chunk(chunk: dict[str, Any], embedding: Optional[bytes]) -> int:
    """
    Insere ou substitui um chunk no banco.

    Usa INSERT OR REPLACE baseado na UNIQUE constraint de content_hash.
    Se já existir um chunk com o mesmo hash, os dados são atualizados.

    Args:
        chunk: Dicionário com chaves content, heading_path, source,
               content_hash, char_count, tags.
        embedding: Vetor de embedding serializado em bytes (ou None).

    Returns:
        O rowid do registro inserido/atualizado.
    """
    tags = chunk.get('tags', [])
    if isinstance(tags, list):
        tags_json = json.dumps(tags, ensure_ascii=False)
    else:
        tags_json = str(tags) if tags else '[]'

    created_at = datetime.now(timezone.utc).isoformat()
    last_updated = datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO chunks
                (source, heading, content, embedding, score,
                 content_hash, tags, char_count, created_at, last_updated)
            VALUES (?, ?, ?, ?,
                    COALESCE((SELECT score FROM chunks WHERE content_hash = ?), 0.5),
                    ?, ?, ?, ?, ?)
            """,
            (
                chunk.get('source', ''),
                chunk.get('heading_path', ''),
                chunk.get('content', ''),
                embedding,
                chunk.get('content_hash', ''),
                chunk.get('content_hash', ''),
                tags_json,
                chunk.get('char_count', 0),
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return rowid
    finally:
        conn.close()


def get_by_hash(content_hash: str) -> Optional[dict[str, Any]]:
    """
    Busca um chunk pelo content_hash.

    Args:
        content_hash: Hash SHA256 do conteúdo.

    Returns:
        Dicionário com os dados do chunk ou None se não encontrado.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM chunks WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()

        if row is None:
            return None

        return _row_to_dict(row)
    finally:
        conn.close()


def get_stats() -> dict[str, Any]:
    """
    Retorna estatísticas do banco: total de chunks, fontes distintas,
    tamanho médio, etc.

    Returns:
        Dicionário com chaves: total_chunks, total_sources,
        avg_char_count, max_char_count, min_char_count,
        chunks_with_embedding, db_size_bytes.
    """
    conn = _get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        sources = conn.execute(
            "SELECT COUNT(DISTINCT source) FROM chunks"
        ).fetchone()[0]
        stats = conn.execute(
            """
            SELECT
                AVG(char_count) as avg_cc,
                MAX(char_count) as max_cc,
                MIN(char_count) as min_cc,
                COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_emb
            FROM chunks
            """
        ).fetchone()

        db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0

        return {
            'total_chunks': total,
            'total_sources': sources,
            'avg_char_count': round(stats['avg_cc'], 1) if stats['avg_cc'] else 0,
            'max_char_count': stats['max_cc'] or 0,
            'min_char_count': stats['min_cc'] or 0,
            'chunks_with_embedding': stats['with_emb'] or 0,
            'db_size_bytes': db_size,
        }
    finally:
        conn.close()


# ── Helpers internos ────────────────────────────────────────────────────────

def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Converte uma Row SQLite em dicionário Python com tipos adequados."""
    d = dict(row)
    # Converte tags de JSON string para lista
    if d.get('tags'):
        try:
            d['tags'] = json.loads(d['tags'])
        except (json.JSONDecodeError, TypeError):
            pass
    return d
