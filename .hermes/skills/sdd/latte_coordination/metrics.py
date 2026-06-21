#!/usr/bin/env python3
"""
metrics.py — Métricas de Coordenação LATTE (T017)
==================================================

Fornece a função ``compute_coordination_metrics(graph) -> dict`` que extrai
do coordination graph G_final métricas quantitativas de qualidade da
coordenação, conforme definido no Feature 001: LATTE Coordination.

Métricas computadas:
  - overwrite_rate      : quantas vezes um arquivo foi escrito por mais de 1 Worker
  - wasted_chars         : caracteres escritos que não aparecem no output final
  - idle_rounds          : proporção de rounds com Workers ociosos
  - straggler_p95        : p95 do tempo de completion por task (em rounds)
  - inter_agent_messages : quantas mensagens Lead↔Workers
  - tokens_consumed      : total estimado de tokens consumidos
  - wall_clock_time      : tempo de parede (segundos) da execução

Referências:
  - graph-schema.md, Seção 5: schema canônico do G_t
  - graph-schema.md, Seção 6: invariantes
  - orchestrator.py: CoordinationGraph wrapper
  - T017: LATTE Coordination Metrics
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Optional, Union

try:
    import numpy as np  # type: ignore[import-untyped]
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Operadores executados por Workers (para detecção de ociosidade)
WORKER_ACTION_OPERATORS: frozenset[str] = frozenset({
    "Claim",
    "Complete",
    "Discover",
})

# Operadores que geram mensagens inter-agente (Lead ↔ Workers)
INTER_AGENT_OPERATORS: frozenset[str] = frozenset({
    "Assign",
    "Claim",
    "Complete",
    "Release",
    "Close",
    "Verify",
    "Discover",
})

# Status terminais (output considerado válido/final)
TERMINAL_STATUSES: frozenset[str] = frozenset({"done", "verified"})

# Tokens estimados por entrada de histórico (heurística conservadora)
# Cada ação no histórico representa ~1 chamada de agente com contexto.
# Valor baseado em estimativa de mensagens típicas LATTE com context scoping.
_ESTIMATED_TOKENS_PER_HISTORY_ENTRY: int = 2000


# ---------------------------------------------------------------------------
# Helper: normalização da entrada
# ---------------------------------------------------------------------------

def _ensure_dict(graph: Any) -> dict[str, Any]:
    """Converte o grafo para dict puro, sem modificar o original.

    Suporta:
      - dict nativo
      - CoordinationGraph (expõe .raw)
      - Qualquer objeto com atributo .raw ou dict-like
    """
    if isinstance(graph, dict):
        return graph
    if hasattr(graph, "raw"):
        return graph.raw
    return dict(graph)


def _parse_graph(graph: Any) -> dict[str, Any]:
    """Normaliza a entrada e retorna dict com metadados, nós, histórico."""
    g = _ensure_dict(graph)
    return {
        "metadata": g.get("metadata", {}),
        "nodes": g.get("nodes", []),
        "edges": g.get("edges", []),
        "history": g.get("history", []),
    }


def _parse_iso_timestamp(ts: Optional[str]) -> Optional[datetime]:
    """Converte timestamp ISO 8601 para datetime UTC-aware.

    Retorna None se ts for None ou mal-formado.
    """
    if ts is None:
        return None
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# p95 helper (sem numpy)
# ---------------------------------------------------------------------------

def _percentile_95(values: list[float]) -> float:
    """Calcula o percentil 95 usando interpolação linear (compatible com numpy).

    Se numpy estiver disponível, usa np.percentile; caso contrário,
    implementa manualmente.

    Args:
        values: Lista de valores numéricos (não vazia).

    Returns:
        Valor no percentil 95.
    """
    if not values:
        return 0.0

    if _HAS_NUMPY:
        return float(np.percentile(values, 95))  # type: ignore[no-any-return]

    # Implementação manual com interpolação linear
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    rank = 0.95 * (n - 1)
    lower_idx = int(math.floor(rank))
    upper_idx = int(math.ceil(rank))

    if lower_idx == upper_idx:
        return sorted_vals[lower_idx]

    fraction = rank - lower_idx
    return sorted_vals[lower_idx] + fraction * (
        sorted_vals[upper_idx] - sorted_vals[lower_idx]
    )


# ===========================================================================
# Métricas individuais
# ===========================================================================

def _compute_overwrite_rate(
    nodes: list[dict],
    history: list[dict],
) -> dict[str, Any]:
    """Calcula overwrite_rate: quantos nós foram escritos por >1 Worker.

    Um "overwrite" ocorre quando um nó tem múltiplos Workers distintos
    registrando ações (Claim, Complete, Discover) sobre ele no histórico.
    Isso indica que o trabalho de um Worker foi descartado e reexecutado
    por outro — tipicamente via Release/Close seguido de reassignment.

    Returns:
        Dict com:
          - overwrite_count: número de nós com >1 Worker distinto
          - overwrite_rate: overwrite_count / total_nodes
          - overwritten_nodes: lista de (node_id, agentes_distintos)
    """
    # Mapeia node_id → set de agentes distintos (excluindo o Lead)
    node_agents: dict[str, set[str]] = defaultdict(set)
    lead = None

    for entry in history:
        node_id = entry.get("node_id", "")
        agent = entry.get("agent", "")
        operator = entry.get("operator", "")

        # Tenta identificar o Lead pela primeira entrada do histórico
        if lead is None and operator == "Discover":
            lead = agent

        node_agents[node_id].add(agent)

    # Remove o Lead da contagem (Lead não é Worker)
    if lead:
        for nid in node_agents:
            node_agents[nid].discard(lead)

    overwritten = [
        (nid, sorted(agents))
        for nid, agents in node_agents.items()
        if len(agents) > 1
    ]

    total_nodes = len(nodes)
    overwrite_count = len(overwritten)
    overwrite_rate = (overwrite_count / total_nodes) if total_nodes > 0 else 0.0

    return {
        "overwrite_count": overwrite_count,
        "overwrite_rate": round(overwrite_rate, 4),
        "overwritten_nodes": overwritten,
    }


def _compute_wasted_chars(
    nodes: list[dict],
    history: list[dict],
) -> dict[str, Any]:
    """Calcula wasted_chars: caracteres escritos que não aparecem no output final.

    Considera como "desperdiçados":
      1. Output de nós cujo status final NÃO é done/verified (output descartado).
      2. Output de nós onde houve Release — output do Worker original foi descartado
         quando outro Worker reassumiu (rastreado via histórico).

    Returns:
        Dict com:
          - wasted_chars: total de caracteres desperdiçados
          - total_output_chars: total de caracteres no output final
          - waste_ratio: wasted_chars / (wasted_chars + total_output_chars)
          - wasted_nodes: lista de (node_id, chars_desperdicados)
    """
    wasted_total = 0
    total_output = 0
    wasted_nodes: list[tuple[str, int, str]] = []  # (node_id, chars, reason)

    # Build node lookup
    node_map: dict[str, dict] = {n["id"]: n for n in nodes}

    # 1. Nós não-terminais com output (output descartado)
    for node in nodes:
        node_id = node["id"]
        output = node.get("output")
        status = node.get("status", "pending")

        if status in TERMINAL_STATUSES and output:
            total_output += len(output)
        elif status not in TERMINAL_STATUSES and output:
            wasted_total += len(output)
            wasted_nodes.append((node_id, len(output), f"status={status}"))

    # 2. Nós com Release no histórico — output anterior foi descartado
    # Rastreamos sequências: Claim por worker A → Release → Claim por worker B
    # O output de A foi desperdiçado.
    release_nodes: set[str] = set()
    for entry in history:
        if entry.get("operator") == "Release":
            release_nodes.add(entry.get("node_id", ""))

    for nid in release_nodes:
        node = node_map.get(nid)
        if node is None:
            continue
        # Se o nó terminou bem, o output do worker que sofreu release foi
        # desperdiçado (sobrescrito pelo worker que reassumiu).
        # Estimamos como metade do output final (aproximação).
        output = node.get("output")
        if output and node.get("status") in TERMINAL_STATUSES:
            # O output final é do último worker. O anterior foi desperdiçado.
            # Estimativa: o worker original produziu ~ mesma quantidade.
            wasted_chars_estimate = len(output) // 2
            if wasted_chars_estimate > 0:
                # Evita dupla contagem com caso 1
                already_counted = any(
                    wn[0] == nid for wn in wasted_nodes
                )
                if not already_counted:
                    wasted_total += wasted_chars_estimate
                    wasted_nodes.append(
                        (nid, wasted_chars_estimate, "release+reassign")
                    )

    total_chars = wasted_total + total_output
    waste_ratio = (wasted_total / total_chars) if total_chars > 0 else 0.0

    return {
        "wasted_chars": wasted_total,
        "total_output_chars": total_output,
        "waste_ratio": round(waste_ratio, 4),
        "wasted_nodes": wasted_nodes,
    }


def _compute_idle_rounds(
    history: list[dict],
    metadata: dict,
) -> dict[str, Any]:
    """Calcula idle_rounds: proporção de rounds com Workers ociosos.

    Um round é considerado "ocioso" se nenhum Worker registrou ação
    (Claim, Complete, Discover) naquele round.

    Returns:
        Dict com:
          - idle_rounds: número de rounds ociosos
          - total_rounds: rounds totais
          - idle_ratio: proporção de rounds ociosos
          - idle_round_list: lista dos números dos rounds ociosos
    """
    total_rounds = metadata.get("round", 0)
    if total_rounds == 0:
        return {
            "idle_rounds": 0,
            "total_rounds": 0,
            "idle_ratio": 0.0,
            "idle_round_list": [],
        }

    # Coleta rounds com ações de Worker
    active_rounds: set[int] = set()
    for entry in history:
        if entry.get("operator") in WORKER_ACTION_OPERATORS:
            active_rounds.add(entry.get("round", 0))

    # Rounds 1..total_rounds (round 0 é setup)
    all_rounds = set(range(1, total_rounds + 1))
    idle_round_set = all_rounds - active_rounds
    idle_count = len(idle_round_set)

    return {
        "idle_rounds": idle_count,
        "total_rounds": total_rounds,
        "idle_ratio": round(idle_count / total_rounds, 4),
        "idle_round_list": sorted(idle_round_set),
    }


def _compute_straggler_p95(
    nodes: list[dict],
) -> dict[str, Any]:
    """Calcula straggler_p95: percentil 95 do tempo de completion por task.

    O tempo de completion é medido como:
      completed_at_round - created_at_round   (rounds do Discovery ao Done)
      ou, se assigned_at_round existir:
      completed_at_round - assigned_at_round  (rounds em execução ativa)

    Reporta ambos.

    Returns:
        Dict com:
          - p95_total: p95 de completed_at_round - created_at_round
          - p95_active: p95 de completed_at_round - assigned_at_round
          - completion_times: lista dos tempos individuais (total)
          - mean_total: média do tempo total
          - max_total: máximo do tempo total
          - tasks_completed: número de tasks com completion registrado
    """
    total_times: list[float] = []
    active_times: list[float] = []

    for node in nodes:
        completed = node.get("completed_at_round")
        if completed is None:
            continue

        created = node.get("created_at_round", 0)
        assigned = node.get("assigned_at_round")

        total_time = completed - created
        if total_time >= 0:
            total_times.append(float(total_time))

        if assigned is not None:
            active_time = completed - assigned
            if active_time >= 0:
                active_times.append(float(active_time))

    return {
        "p95_total": round(_percentile_95(total_times), 2) if total_times else None,
        "p95_active": round(_percentile_95(active_times), 2) if active_times else None,
        "mean_total": round(sum(total_times) / len(total_times), 2) if total_times else None,
        "max_total": max(total_times) if total_times else None,
        "tasks_completed": len(total_times),
        "completion_times": total_times,
    }


def _compute_inter_agent_messages(
    history: list[dict],
    metadata: dict,
) -> dict[str, Any]:
    """Calcula inter_agent_messages: quantas mensagens Lead↔Workers.

    Conta todas as entradas de histórico correspondentes a operadores
    que envolvem comunicação inter-agente.

    Returns:
        Dict com:
          - total_messages: total de mensagens
          - by_operator: contagem por tipo de operador
          - lead_messages: mensagens originadas pelo Lead (Assign, Release, Close, Verify)
          - worker_messages: mensagens originadas por Workers (Claim, Complete, Discover)
    """
    lead_ops = {"Assign", "Release", "Close", "Verify"}
    worker_ops = {"Claim", "Complete", "Discover"}
    # Discover pode ser tanto Lead quanto Worker; usamos o agent para distinguir
    lead_id = metadata.get("lead", "")

    total = 0
    by_operator: Counter[str] = Counter()
    lead_count = 0
    worker_count = 0

    for entry in history:
        op = entry.get("operator", "")
        if op not in INTER_AGENT_OPERATORS:
            continue
        total += 1
        by_operator[op] += 1

        agent = entry.get("agent", "")
        if op == "Discover":
            # Discover: Lead se agent == lead_id, senão Worker
            if agent == lead_id:
                lead_count += 1
            else:
                worker_count += 1
        elif op in lead_ops:
            lead_count += 1
        elif op in worker_ops:
            worker_count += 1

    return {
        "total_messages": total,
        "by_operator": dict(by_operator),
        "lead_messages": lead_count,
        "worker_messages": worker_count,
    }


def _compute_tokens_consumed(
    history: list[dict],
    metadata: dict,
) -> dict[str, Any]:
    """Estima tokens_consumed: total de tokens consumidos na execução.

    Como o coordination graph não armazena contagem exata de tokens,
    usamos uma heurística baseada no número de entradas de histórico:
    cada ação ≈ 1 chamada de agente com contexto, estimada em
    ~2000 tokens (context scoping + mensagem + output).

    Returns:
        Dict com:
          - estimated_tokens: estimativa total de tokens
          - history_entries: total de entradas de histórico
          - tokens_per_entry: fator de estimativa usado
          - note: indica que é uma estimativa
    """
    entry_count = len(history)

    return {
        "estimated_tokens": entry_count * _ESTIMATED_TOKENS_PER_HISTORY_ENTRY,
        "history_entries": entry_count,
        "tokens_per_entry": _ESTIMATED_TOKENS_PER_HISTORY_ENTRY,
        "note": (
            "Estimativa baseada em "
            f"{_ESTIMATED_TOKENS_PER_HISTORY_ENTRY} tokens/entrada "
            "de histórico. Para contagem exata, instrumente o agente."
        ),
    }


def _compute_wall_clock_time(
    history: list[dict],
    metadata: dict,
) -> dict[str, Any]:
    """Calcula wall_clock_time: tempo de parede da execução.

    Usa os timestamps ISO 8601 do histórico para medir o intervalo real.
    Alternativamente, usa metadata.created_at como início e o último
    timestamp do histórico como fim.

    Returns:
        Dict com:
          - wall_clock_seconds: tempo total em segundos
          - start_time: timestamp de início
          - end_time: timestamp de fim
          - note: indica se usou histórico ou metadata
    """
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None

    # Primeiro e último timestamp do histórico
    if history:
        start_ts = history[0].get("timestamp")
        end_ts = history[-1].get("timestamp")
        start_dt = _parse_iso_timestamp(start_ts)
        end_dt = _parse_iso_timestamp(end_ts)

    # Fallback: metadata.created_at
    if start_dt is None:
        created_at = metadata.get("created_at")
        start_dt = _parse_iso_timestamp(created_at)

    # Se ambos disponíveis, calcula
    if start_dt is not None and end_dt is not None:
        delta = end_dt - start_dt
        wall_seconds = delta.total_seconds()
        note = "Calculado a partir dos timestamps do histórico"
    elif start_dt is not None:
        wall_seconds = 0.0
        note = "Apenas timestamp inicial disponível (execução pode estar em andamento)"
    else:
        wall_seconds = None  # type: ignore[assignment]
        note = "Sem timestamps disponíveis no grafo"

    return {
        "wall_clock_seconds": round(wall_seconds, 2) if isinstance(wall_seconds, (int, float)) else None,  # type: ignore[arg-type]
        "start_time": start_dt.isoformat() if start_dt else None,
        "end_time": end_dt.isoformat() if end_dt else None,
        "note": note,
    }


# ===========================================================================
# Função pública principal
# ===========================================================================

def compute_coordination_metrics(
    graph: Union[dict[str, Any], Any],
) -> dict[str, Any]:
    """Calcula métricas de coordenação LATTE a partir do coordination graph G_final.

    Extrai métricas quantitativas de qualidade da coordenação conforme
    definido no Feature 001: LATTE Coordination (T017).

    Args:
        graph: O coordination graph G_final. Aceita:
               - dict nativo (conforme graph-schema.md, Seção 5)
               - Objeto CoordinationGraph (do orchestrator.py)

    Returns:
        Dicionário com as seguintes chaves:

        - **overwrite**: Métricas de sobrescrita
          - overwrite_count: quantos nós foram trabalhados por >1 Worker
          - overwrite_rate: overwrite_count / total_nodes
          - overwritten_nodes: lista de (node_id, agents)

        - **waste**: Métricas de desperdício
          - wasted_chars: caracteres produzidos e descartados
          - total_output_chars: caracteres no output final
          - waste_ratio: wasted_chars / total_chars
          - wasted_nodes: lista de (node_id, chars, motivo)

        - **idle**: Métricas de ociosidade
          - idle_rounds: número de rounds sem ação de Worker
          - total_rounds: rounds totais executados
          - idle_ratio: idle_rounds / total_rounds
          - idle_round_list: lista dos rounds ociosos

        - **straggler**: Métricas de straggler (p95)
          - p95_total: p95 de (completed_at_round - created_at_round)
          - p95_active: p95 de (completed_at_round - assigned_at_round)
          - mean_total: média do tempo de completion
          - max_total: máximo do tempo de completion
          - tasks_completed: número de tasks concluídas

        - **messages**: Métricas de comunicação
          - total_messages: total de mensagens inter-agente
          - by_operator: contagem por operador
          - lead_messages: mensagens do Lead
          - worker_messages: mensagens de Workers

        - **tokens**: Estimativa de tokens
          - estimated_tokens: total estimado
          - history_entries: base da estimativa
          - note: explicação da heurística

        - **timing**: Tempo de parede
          - wall_clock_seconds: segundos totais (ou None)
          - start_time: timestamp ISO 8601
          - end_time: timestamp ISO 8601
          - note: fonte da medição

        - **summary**: Resumo para relatório
          - total_nodes: |V_final|
          - total_edges: |E_final|
          - terminal_nodes: nós em done/verified
          - completion_rate: terminal_nodes / total_nodes
          - graph_is_healthy: todas as tasks terminais?

    Example:
        >>> from orchestrator import Orchestrator
        >>> orch = Orchestrator(task_description="...", G_0=G_0)
        >>> G_final = orch.run()
        >>> metrics = compute_coordination_metrics(G_final)
        >>> print(metrics["summary"]["completion_rate"])
        0.95
    """
    graph_data = _parse_graph(graph)

    metadata = graph_data["metadata"]
    nodes = graph_data["nodes"]
    history = graph_data["history"]
    edges = graph_data["edges"]

    # Validação mínima
    if not nodes and not history:
        return {
            "error": "Grafo vazio — sem nodes e sem history. "
                     "Forneça um G_final populado.",
            "overwrite": {},
            "waste": {},
            "idle": {},
            "straggler": {},
            "messages": {},
            "tokens": {},
            "timing": {},
            "summary": {
                "total_nodes": 0,
                "total_edges": 0,
                "completion_rate": 0.0,
                "graph_is_healthy": False,
            },
        }

    # --- Cálculo das métricas ---
    overwrite = _compute_overwrite_rate(nodes, history)
    waste = _compute_wasted_chars(nodes, history)
    idle = _compute_idle_rounds(history, metadata)
    straggler = _compute_straggler_p95(nodes)
    messages = _compute_inter_agent_messages(history, metadata)
    tokens = _compute_tokens_consumed(history, metadata)
    timing = _compute_wall_clock_time(history, metadata)

    # --- Sumário ---
    total_nodes = len(nodes)
    total_edges = len(edges)
    terminal_count = sum(
        1 for n in nodes if n.get("status") in TERMINAL_STATUSES
    )
    completion_rate = (terminal_count / total_nodes) if total_nodes > 0 else 0.0
    graph_is_healthy = (completion_rate == 1.0) if total_nodes > 0 else False

    summary = {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "terminal_nodes": terminal_count,
        "non_terminal_nodes": total_nodes - terminal_count,
        "completion_rate": round(completion_rate, 4),
        "graph_is_healthy": graph_is_healthy,
        "feature_id": metadata.get("feature_id", "?"),
        "lead": metadata.get("lead", "?"),
        "workers": metadata.get("workers", []),
    }

    return {
        "overwrite": overwrite,
        "waste": waste,
        "idle": idle,
        "straggler": straggler,
        "messages": messages,
        "tokens": tokens,
        "timing": timing,
        "summary": summary,
    }


# ===========================================================================
# CLI mínima para teste rápido
# ===========================================================================

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <graph.json>")
        print("  graph.json : arquivo JSON com o coordination graph G_final")
        sys.exit(1)

    graph_file = sys.argv[1]
    try:
        with open(graph_file, encoding="utf-8") as f:
            graph_dict = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {graph_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERRO: JSON inválido: {e}")
        sys.exit(1)

    metrics = compute_coordination_metrics(graph_dict)
    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=str))
