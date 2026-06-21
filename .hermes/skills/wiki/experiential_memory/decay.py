"""
T012 — decay.py: Score decay por inatividade.

Aplica penalidade de score a chunks que não são atualizados há várias
features. Usa a coluna last_updated (adicionada via store.py) para
determinar o cutoff de inatividade.
"""

from .store import _get_conn


def apply_decay(
    inactivity_threshold: int = 5,
    decay_amount: float = 0.01,
    floor: float = 0.1,
) -> int:
    """Aplica decay de score a chunks inativos.

    Um chunk é considerado inativo se não estiver entre os
    ``inactivity_threshold`` chunks mais recentemente atualizados
    (por ``last_updated``). Chunks com score <= floor são preservados
    (já estão no piso e não devem perder mais pontos).

    Args:
        inactivity_threshold: Quantos chunks mais recentes (por
            ``last_updated``) são considerados ativos e portanto
            imunes ao decay.
        decay_amount: Quanto subtrair do score de cada chunk
            inativo (padrão: 0.01).
        floor: Score mínimo — chunks com score <= floor NÃO
            sofrem decay (padrão: 0.1).

    Returns:
        Número de chunks afetados pelo decay.
    """
    if inactivity_threshold <= 0:
        return 0

    conn = _get_conn()
    try:
        # ── 1. Encontra o timestamp de corte ──────────────────────────
        # O cutoff é o last_updated do inactivity_threshold-ésimo
        # chunk mais recente (ordenado por last_updated DESC).
        cutoff_row = conn.execute(
            """
            SELECT last_updated
              FROM chunks
             WHERE last_updated IS NOT NULL
             ORDER BY last_updated DESC
             LIMIT 1 OFFSET ?
            """,
            (inactivity_threshold - 1,),
        ).fetchone()

        if cutoff_row is None:
            # Menos chunks que inactivity_threshold → nada a decair
            return 0

        cutoff = cutoff_row[0]

        # ── 2. Aplica decay nos chunks abaixo do corte ────────────────
        cursor = conn.execute(
            """
            UPDATE chunks
               SET score = MAX(?, score - ?)
             WHERE score > ?
               AND (last_updated < ? OR last_updated IS NULL)
            """,
            (floor, decay_amount, floor, cutoff),
        )
        conn.commit()
        return cursor.rowcount

    finally:
        conn.close()
