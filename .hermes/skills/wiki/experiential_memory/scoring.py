"""
T010 — scoring.py: Sistema de pontuação (score) para chunks da memória experiencial.
Operações de atualização incremental, consulta e ranqueamento por score.
"""

from datetime import datetime, timezone
from typing import Any

from .store import DB_PATH, _get_conn, _row_to_dict


def update_score(content_hash: str, delta: float) -> bool:
    """Atualiza o score de um chunk aplicando um delta incremental.

    O score é mantido no intervalo [0.0, 1.0] via MAX(0.0, MIN(1.0, ...)).
    Retorna True se alguma linha foi afetada (hash existe), False caso contrário.

    Args:
        content_hash: Hash SHA256 do conteúdo do chunk.
        delta: Valor a somar ao score atual (pode ser positivo ou negativo).
    """
    conn = _get_conn()
    try:
        cursor = conn.execute(
            """
            UPDATE chunks
               SET score = MAX(0.0, MIN(1.0, score + ?)),
                   last_updated = ?
             WHERE content_hash = ?
            """,
            (delta, datetime.now(timezone.utc).isoformat(), content_hash),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_score(content_hash: str) -> float:
    """Retorna o score atual de um chunk, ou 0.0 se não encontrado.

    Args:
        content_hash: Hash SHA256 do conteúdo do chunk.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT score FROM chunks WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        return row['score'] if row else 0.0
    finally:
        conn.close()


def get_top_hints(k: int = 10) -> list[dict[str, Any]]:
    """Retorna os top-k chunks com maior score, em ordem decrescente.

    Args:
        k: Número máximo de chunks a retornar (padrão: 10).

    Returns:
        Lista de dicionários com os dados completos de cada chunk.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM chunks ORDER BY score DESC LIMIT ?",
            (k,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def get_low_score_hints(threshold: float = 0.3) -> list[dict[str, Any]]:
    """Retorna chunks com score abaixo do threshold — candidatos a pruning.

    Args:
        threshold: Score máximo para inclusão (padrão: 0.3).

    Returns:
        Lista de dicionários com os dados completos de cada chunk.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM chunks WHERE score < ? ORDER BY score ASC",
            (threshold,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def reset_all_scores() -> int:
    """Reseta todos os scores para 0.5 (valor neutro).

    Returns:
        Número de linhas afetadas.
    """
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "UPDATE chunks SET score = 0.5, last_updated = ?",
            (datetime.now(timezone.utc).isoformat(),),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
