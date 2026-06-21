"""
T011 — feedback.py: Feedback loop que converte métricas de coordenação LATTE
em utility signal e atualiza scores dos chunks usados como hints na feature.

Parte da Feature 002: Wiki Experiential Memory (M2.3 — Hint Scoring + Feedback).

Fluxo:
  1. compute_utility_signal(metrics) → u ∈ [0, 1]
  2. apply_feedback(u, chunk_hashes) → atualiza scores via scoring.update_score()
"""

from __future__ import annotations

from typing import Any

from .scoring import update_score


# ── Pesos do utility signal ──────────────────────────────────────────────────

# Refletem o impacto relativo na qualidade da execução:
#   overwrite (0.4): retrabalho → output menos confiável
#   waste     (0.3): esforço mal direcionado → ineficiência
#   idle      (0.3): Workers ociosos → DAG mal particionado
_W_OVERWRITE = 0.4
_W_WASTE = 0.3
_W_IDLE = 0.3

# Fator de ajuste fino: mantém updates pequenos e graduais (máx ±0.10/feature)
_DELTA_SCALE = 0.2


def compute_utility_signal(metrics: dict[str, Any]) -> float:
    """Converte métricas de coordenação LATTE em utility signal u ∈ [0, 1].

    Fórmula:
        u = 1.0 - (overwrite_rate × 0.4 + waste_ratio × 0.3 + idle_ratio × 0.3)

    Args:
        metrics: Dicionário retornado por
                 ``latte_coordination.metrics.compute_coordination_metrics(G_final)``.
                 Espera as chaves: overwrite.overwrite_rate, waste.waste_ratio,
                 idle.idle_ratio.

    Returns:
        Utility signal normalizado no intervalo [0.0, 1.0].

    Raises:
        KeyError: Se as chaves esperadas não existirem no dicionário de métricas.
        TypeError: Se os valores não forem numéricos.

    Example:
        >>> metrics = {
        ...     "overwrite": {"overwrite_rate": 0.0},
        ...     "waste": {"waste_ratio": 0.15},
        ...     "idle": {"idle_ratio": 0.10},
        ... }
        >>> u = compute_utility_signal(metrics)
        >>> print(f"{u:.4f}")
        0.9250
    """
    overwrite_rate = float(metrics["overwrite"]["overwrite_rate"])
    waste_ratio = float(metrics["waste"]["waste_ratio"])
    idle_ratio = float(metrics["idle"]["idle_ratio"])

    penalty = (
        overwrite_rate * _W_OVERWRITE
        + waste_ratio * _W_WASTE
        + idle_ratio * _W_IDLE
    )

    u = 1.0 - penalty

    # Clamp para garantir intervalo [0, 1] mesmo com métricas extremas
    return max(0.0, min(1.0, u))


def classify_utility(u: float) -> str:
    """Classifica o utility signal em categoria qualitativa.

    Args:
        u: Utility signal no intervalo [0, 1].

    Returns:
        String de classificação: 'good', 'neutral', ou 'poor'.

    >>> classify_utility(0.85)
    'good'
    >>> classify_utility(0.55)
    'neutral'
    >>> classify_utility(0.25)
    'poor'
    """
    if u > 0.7:
        return "good"
    elif u >= 0.4:
        return "neutral"
    else:
        return "poor"


def utility_to_delta(u: float) -> float:
    """Converte utility signal em delta de score para cada chunk usado como hint.

    Delta = (u - 0.5) × 0.2

    O fator 0.2 mantém ajustes pequenos (máx ±0.10 por feature), permitindo
    convergência gradual ao longo de múltiplas features.

    Args:
        u: Utility signal no intervalo [0, 1].

    Returns:
        Delta a ser aplicado via scoring.update_score().

    >>> utility_to_delta(0.925)
    0.085
    >>> utility_to_delta(0.5)
    0.0
    >>> utility_to_delta(0.1)
    -0.08
    """
    delta = (u - 0.5) * _DELTA_SCALE
    return round(delta, 4)


def apply_feedback(
    u: float,
    chunk_hashes: list[str],
) -> dict[str, Any]:
    """Aplica o feedback loop: atualiza scores de todos os chunks usados como hints.

    Para cada chunk_hash na lista, chama scoring.update_score(hash, delta) onde
    delta = (u - 0.5) × 0.2.

    Args:
        u: Utility signal computado por compute_utility_signal().
        chunk_hashes: Lista de hashes SHA256 dos chunks usados como hints
                      durante a feature.

    Returns:
        Dicionário com resumo da operação:
        - utility: float — o utility signal usado
        - classification: str — 'good', 'neutral', ou 'poor'
        - delta: float — o delta aplicado a cada chunk
        - updated: int — número de chunks atualizados com sucesso
        - not_found: int — número de hashes não encontrados no índice
        - total: int — total de hashes processados

    Example:
        >>> u = 0.85
        >>> chunk_hashes = ["abc123...", "def456..."]
        >>> result = apply_feedback(u, chunk_hashes)
        >>> print(result["updated"])
        2
    """
    delta = utility_to_delta(u)
    classification = classify_utility(u)

    updated = 0
    not_found = 0

    for chunk_hash in chunk_hashes:
        success = update_score(chunk_hash, delta)
        if success:
            updated += 1
        else:
            not_found += 1

    return {
        "utility": round(u, 4),
        "classification": classification,
        "delta": delta,
        "updated": updated,
        "not_found": not_found,
        "total": len(chunk_hashes),
    }


def get_delta_for_utility(u: float) -> float:
    """Retorna o delta de score correspondente ao mapeamento qualitativo.

    Mapeamento usado para relatórios e logging:
      - u > 0.7  → +0.04 (boa execução, hints contribuíram positivamente)
      - u < 0.4  → −0.04 (execução ruim, hints possivelmente prejudiciais)
      - 0.4–0.7  →  0.00 (neutro, sem ajuste)

    Args:
        u: Utility signal no intervalo [0, 1].

    Returns:
        Delta qualitativo conforme tabela de mapeamento.

    >>> get_delta_for_utility(0.85)
    0.04
    >>> get_delta_for_utility(0.55)
    0.0
    >>> get_delta_for_utility(0.25)
    -0.04
    """
    classification = classify_utility(u)
    if classification == "good":
        return 0.04
    elif classification == "poor":
        return -0.04
    else:
        return 0.0
