#!/usr/bin/env python3
"""
orchestrator.py — LATTE Coordination Engine (Algorithm A4.5)
=============================================================

Implementa o loop de rounds do orchestrator LATTE conforme definido no paper
"Improving the Efficiency of Language Agent Teams with Adaptive Task Graphs"
(Mieczkowski et al., 2026, arXiv:2605.06320), Algorithm A4.5.

Este é o motor central que coordena Lead e Workers em rounds discretos,
gerenciando o coordination graph dinâmico G_t completamente em memória.

Arquitetura de módulos (T004–T009):
  T004: orchestrator.py (este arquivo) — loop principal + CoordinationGraph
  T005: heartbeat.py        — heartbeat monitoring + straggler detection
  T006: frontier.py         — compute_frontier() + ordenação do frontier
  T007: dispatcher.py       — agent dispatching (assign, re-engage, delegate)
  T008: lead_operators.py   — Lead-only operators (Assign, Release, Close, Verify)
  T009: worker_operators.py — Worker operators (Claim, Complete, Discover)

Fase 0: Planning
  Lead recebe task description e inicializa G_0 via Discover operations.
  G_0 é carregado do tasks.md (seção ## Coordination Graph) ou gerado
  como DAG inicial simples via inferência automática.

Fase 1: Execution (loop principal)
  Para cada round t = 1..T:
    1. Heartbeat monitoring
    2. Frontier identification
    3. Agent dispatching
    4. Parallel execution
    5. Termination check

Referências:
  - graph-schema.md: schema canônico do G_t (nodes, edges, status, frontier)
  - latte-protocol.md: contrato dos 7 operadores, invariantes, formato de mensagens
  - latte-task-rules.md: extensão do tasks.md com graph-operators
  - plan.md (ADR-001 a ADR-005): decisões arquiteturais
"""

from __future__ import annotations

import copy
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .frontier import compute_frontier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constantes do protocolo LATTE
# ---------------------------------------------------------------------------

# Status possíveis de um nó (conjunto S do paper, Definition 1)
VALID_STATUSES: frozenset[str] = frozenset({
    "pending",
    "assigned",
    "in_progress",
    "done",
    "verified",
})

# Status considerados terminais para o grafo (completion)
TERMINAL_STATUSES: frozenset[str] = frozenset({"done", "verified"})

# Transições válidas da máquina de estados (Seção 2.2 do graph-schema.md)
VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending":     frozenset({"assigned", "in_progress"}),
    "assigned":    frozenset({"in_progress", "pending"}),
    "in_progress": frozenset({"done", "pending"}),
    "done":        frozenset({"verified"}),
    "verified":    frozenset(),  # Estado terminal — sem transições de saída
}

# Defaults configuráveis (ADR-001: rounds como unidade de heartbeat)
DEFAULT_MAX_ROUNDS: int = 40
DEFAULT_HEARTBEAT_THRESHOLD: int = 4

# Feature 005 — LATTE Hardening defaults (ADRs 006-012)
DEFAULT_MAX_LLM_CALLS: int = 25
DEFAULT_OPERATOR_TIMEOUT: int = 45       # segundos
DEFAULT_VERIFY_MODE: str = "deterministic"  # "deterministic" ou "llm"
DEFAULT_SUMMARY_INTERVAL: int = 4          # rounds entre sumarizações

VALID_VERIFY_MODES: frozenset[str] = frozenset({"deterministic", "llm"})

# Operadores do protocolo LATTE (Seção 2 do latte-protocol.md)
LEAD_OPERATORS: frozenset[str] = frozenset({
    "Assign", "Release", "Close", "Verify", "Discover",
})
WORKER_OPERATORS: frozenset[str] = frozenset({
    "Claim", "Complete", "Discover",
})


# ===========================================================================
# CoordinationGraph — wrapper sobre o dict do graph-schema (Seção 5)
# ===========================================================================

class CoordinationGraph:
    """
    Wrapper typesafe sobre o dicionário Python que representa G_t.

    Encapsula o schema definido em graph-schema.md, Seção 5, e fornece
    métodos de acesso e mutação com validação de invariantes.

    Estrutura interna (graph-schema.md, Seção 5.1):
        {
            "metadata": {...},
            "nodes": [{id, agent, status, deps, description, output, ...}],
            "edges": [{from, to}],
            "history": [{round, operator, node_id, agent, details, timestamp}],
        }
    """

    def __init__(self, feature_id: str, lead: str, workers: list[str],
                 max_rounds: int = DEFAULT_MAX_ROUNDS,
                 heartbeat_threshold: int = DEFAULT_HEARTBEAT_THRESHOLD,
                 graph_operators: str = "disabled",
                 max_llm_calls: int = DEFAULT_MAX_LLM_CALLS,
                 operator_timeout: int = DEFAULT_OPERATOR_TIMEOUT,
                 verify_mode: str = DEFAULT_VERIFY_MODE) -> None:
        """
        Inicializa um coordination graph vazio G_0.

        Args:
            feature_id: ID da feature sendo executada (ex: "001").
            lead: ID do agente Lead (ℓ).
            workers: Lista de Worker IDs disponíveis (W).
            max_rounds: Número máximo de rounds antes de abort (T_max).
            heartbeat_threshold: Rounds sem ação para detecção de straggler (H).
            graph_operators: Modo graph-operators ("enabled" ou "disabled").
            max_llm_calls: Limite de LLM calls antes de force_finalize (ADR-006).
            operator_timeout: Timeout por operador em segundos (ADR-007).
            verify_mode: Modo de verificação — "deterministic" ou "llm" (ADR-009).
        """
        if verify_mode not in VALID_VERIFY_MODES:
            raise ValueError(
                f"Invalid verify_mode '{verify_mode}'. "
                f"Must be one of: {sorted(VALID_VERIFY_MODES)}"
            )
        self._graph: dict[str, Any] = {
            "metadata": {
                "feature_id": feature_id,
                "round": 0,
                "max_rounds": max_rounds,
                "heartbeat_threshold": heartbeat_threshold,
                "graph_operators": graph_operators,
                "workers": list(workers),
                "lead": lead,
                "created_at": datetime.now(timezone.utc).isoformat(),
                # Feature 005 — Hardening fields
                "max_llm_calls": max_llm_calls,
                "llm_calls_made": 0,
                "operator_timeout": operator_timeout,
                "verify_mode": verify_mode,
                "errors": [],
                "completed_summary": "",
                "round_since_summary": 0,
            },
            "nodes": [],
            "edges": [],
            "history": [],
        }

        # Cache interno para consultas O(1) — invalidado a cada mutação
        self._node_index: dict[str, dict] = {}
        self._status_cache: dict[str, str] = {}
        self._cache_valid: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def raw(self) -> dict:
        """Retorna o dict subjacente (para serialização / módulos externos)."""
        return self._graph

    @property
    def metadata(self) -> dict:
        return self._graph["metadata"]

    @property
    def nodes(self) -> list[dict]:
        return self._graph["nodes"]

    @property
    def edges(self) -> list[dict]:
        return self._graph["edges"]

    @property
    def history(self) -> list[dict]:
        return self._graph["history"]

    @property
    def round(self) -> int:
        return self._graph["metadata"]["round"]

    @round.setter
    def round(self, value: int) -> None:
        self._graph["metadata"]["round"] = value

    @property
    def lead(self) -> str:
        return self._graph["metadata"]["lead"]

    @property
    def workers(self) -> list[str]:
        return list(self._graph["metadata"]["workers"])

    @property
    def max_rounds(self) -> int:
        return self._graph["metadata"]["max_rounds"]

    @property
    def heartbeat_threshold(self) -> int:
        return self._graph["metadata"]["heartbeat_threshold"]

    @property
    def feature_id(self) -> str:
        return self._graph["metadata"]["feature_id"]

    @property
    def graph_operators(self) -> str:
        return self._graph["metadata"].get("graph_operators", "disabled")

    # Feature 005 — Hardening properties (ADR-006 a ADR-012)
    @property
    def max_llm_calls(self) -> int:
        return self._graph["metadata"]["max_llm_calls"]

    @max_llm_calls.setter
    def max_llm_calls(self, value: int) -> None:
        self._graph["metadata"]["max_llm_calls"] = value

    @property
    def llm_calls_made(self) -> int:
        return self._graph["metadata"]["llm_calls_made"]

    @llm_calls_made.setter
    def llm_calls_made(self, value: int) -> None:
        self._graph["metadata"]["llm_calls_made"] = value

    def increment_llm_calls(self, count: int = 1) -> int:
        """Incrementa llm_calls_made e retorna o novo valor."""
        self._graph["metadata"]["llm_calls_made"] += count
        return self._graph["metadata"]["llm_calls_made"]

    @property
    def operator_timeout(self) -> int:
        return self._graph["metadata"]["operator_timeout"]

    @property
    def verify_mode(self) -> str:
        return self._graph["metadata"]["verify_mode"]

    @property
    def errors(self) -> list[dict]:
        return self._graph["metadata"]["errors"]

    def add_error(self, node_id: str, error_type: str, message: str) -> None:
        """Registra um erro de worker no state (ADR-008)."""
        self._graph["metadata"]["errors"].append({
            "node_id": node_id,
            "type": error_type,
            "message": message,
            "round": self.round,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    @property
    def completed_summary(self) -> str:
        return self._graph["metadata"]["completed_summary"]

    @completed_summary.setter
    def completed_summary(self, value: str) -> None:
        self._graph["metadata"]["completed_summary"] = value

    @property
    def round_since_summary(self) -> int:
        return self._graph["metadata"]["round_since_summary"]

    @round_since_summary.setter
    def round_since_summary(self, value: int) -> None:
        self._graph["metadata"]["round_since_summary"] = value

    def is_budget_exhausted(self) -> bool:
        """Verifica se o budget de LLM calls foi excedido (ADR-006)."""
        return self.llm_calls_made >= self.max_llm_calls

    # ------------------------------------------------------------------
    # Cache management
    # ------------------------------------------------------------------

    def _invalidate_cache(self) -> None:
        """Invalida o cache interno de índices (chamar após toda mutação)."""
        self._cache_valid = False

    def _rebuild_cache(self) -> None:
        """Reconstrói índices O(1) a partir da lista de nós."""
        self._node_index = {node["id"]: node for node in self._graph["nodes"]}
        self._status_cache = {
            node["id"]: node["status"] for node in self._graph["nodes"]
        }
        self._cache_valid = True

    def _ensure_cache(self) -> None:
        """Garante que o cache está atualizado antes de consultas."""
        if not self._cache_valid:
            self._rebuild_cache()

    # ------------------------------------------------------------------
    # Node access
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[dict]:
        """
        Retorna o nó com o ID especificado, ou None se não encontrado.

        Args:
            node_id: ID do nó a buscar.

        Returns:
            O dict do nó, ou None.
        """
        self._ensure_cache()
        return self._node_index.get(node_id)

    def find_node(self, node_id: str) -> dict:
        """
        Retorna o nó com o ID especificado. Levanta KeyError se não encontrado.

        Equivalente a _find_node() do graph-schema.md (Seção 5.4).

        Args:
            node_id: ID do nó a buscar.

        Returns:
            O dict do nó.

        Raises:
            KeyError: Se o nó não existe no grafo.
        """
        node = self.get_node(node_id)
        if node is None:
            raise KeyError(f"Node '{node_id}' not found in graph")
        return node

    def has_node(self, node_id: str) -> bool:
        """Retorna True se o nó existe no grafo."""
        return self.get_node(node_id) is not None

    def get_status(self, node_id: str) -> Optional[str]:
        """
        Retorna o status de um nó em O(1).

        Args:
            node_id: ID do nó.

        Returns:
            Status do nó, ou None se não encontrado.
        """
        self._ensure_cache()
        return self._status_cache.get(node_id)

    def get_status_map(self) -> dict[str, str]:
        """
        Retorna um mapa node_id → status para consultas O(1).

        Equivalente a _get_status_map() do graph-schema.md (Seção 5.4).
        """
        self._ensure_cache()
        return dict(self._status_cache)

    # ------------------------------------------------------------------
    # Graph queries
    # ------------------------------------------------------------------

    def get_dependents(self, node_id: str) -> list[str]:
        """
        Retorna lista de nós que dependem de node_id (reverse edges).

        Equivalente a _get_dependents() do graph-schema.md (Seção 5.4).

        Args:
            node_id: ID do nó upstream.

        Returns:
            Lista de IDs de nós que têm node_id em seus deps.
        """
        self._ensure_cache()
        return [
            node["id"] for node in self._graph["nodes"]
            if node_id in node["deps"]
        ]

    def get_node_count(self) -> int:
        """Retorna |V_t| — número total de nós no grafo."""
        return len(self._graph["nodes"])

    def get_edge_count(self) -> int:
        """Retorna |E_t| — número total de arestas no grafo."""
        return len(self._graph["edges"])

    def is_terminal(self) -> bool:
        """
        Verifica se todos os nós estão em estado terminal (done ou verified).

        Equivalente a _is_terminal() do graph-schema.md (Seção 5.4).

        Returns:
            True se todos os nós estão done ou verified.
        """
        self._ensure_cache()
        return all(
            status in TERMINAL_STATUSES
            for status in self._status_cache.values()
        )

    # ------------------------------------------------------------------
    # Mutations (operações são delegadas aos módulos T008/T009)
    # ------------------------------------------------------------------

    def add_node(self, node_data: dict) -> None:
        """
        Adiciona um novo nó ao grafo.

        Usado internamente pelo operador Discover (T008/T009).
        Valida que o ID é único e que o status é válido.

        Args:
            node_data: Dict com a estrutura completa do nó (Seção 1.2).

        Raises:
            ValueError: Se o ID já existe ou status é inválido.
        """
        node_id = node_data["id"]
        if self.has_node(node_id):
            raise ValueError(f"Node '{node_id}' already exists in graph")

        if node_data.get("status") not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{node_data.get('status')}' for node '{node_id}'"
            )

        # Garantir defaults para campos opcionais
        node_data.setdefault("agent", None)
        node_data.setdefault("output", None)
        node_data.setdefault("rounds_inactive", 0)
        node_data.setdefault("assigned_at_round", None)
        node_data.setdefault("completed_at_round", None)

        self._graph["nodes"].append(node_data)

        # Sincronizar edges a partir dos deps
        for dep_id in node_data.get("deps", []):
            self._graph["edges"].append({"from": dep_id, "to": node_id})

        self._invalidate_cache()

    def update_node_status(self, node_id: str, new_status: str,
                           agent: Optional[str] = None) -> None:
        """
        Atualiza o status (e opcionalmente o agent) de um nó.

        Usado internamente pelos operadores Assign, Claim, Complete,
        Release, Close, Verify (T008/T009).

        Args:
            node_id: ID do nó a modificar.
            new_status: Novo status (deve estar em VALID_STATUSES).
            agent: Novo agente, ou None para manter o atual.

        Raises:
            KeyError: Se o nó não existe.
            ValueError: Se a transição de status é inválida.
        """
        node = self.find_node(node_id)
        current_status = node["status"]

        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: '{new_status}'")

        if not self._is_valid_transition(current_status, new_status):
            raise ValueError(
                f"Invalid transition: '{current_status}' → '{new_status}' "
                f"for node '{node_id}'"
            )

        node["status"] = new_status
        if agent is not None:
            node["agent"] = agent

        self._invalidate_cache()

    def add_history_entry(self, operator: str, node_id: str, agent: str,
                          details: Optional[dict] = None) -> None:
        """
        Registra uma entrada no histórico de mutações do grafo.

        Invariante I8 (graph-schema.md, Seção 6.8): toda mutação deve
        ser registrada no histórico.

        Args:
            operator: Nome do operador (Assign, Claim, Complete, ...).
            node_id: ID do nó afetado.
            agent: ID do agente que executou o operador.
            details: Detalhes adicionais (ex: transição de status).
        """
        entry = {
            "round": self.round,
            "operator": operator,
            "node_id": node_id,
            "agent": agent,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._graph["history"].append(entry)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_json(self, pretty: bool = True) -> str:
        """
        Serializa o grafo para JSON.

        Returns:
            String JSON representando G_t completo.
        """
        indent = 2 if pretty else None
        return json.dumps(self._graph, indent=indent, ensure_ascii=False)

    def deep_copy(self) -> "CoordinationGraph":
        """
        Retorna uma cópia profunda do grafo (snapshot imutável).

        Útil para passar G_t como contexto para Workers sem risco
        de mutação concorrente.
        """
        cloned = CoordinationGraph.__new__(CoordinationGraph)
        cloned._graph = copy.deepcopy(self._graph)
        cloned._cache_valid = False
        return cloned

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_valid_transition(current: str, new_status: str) -> bool:
        """
        Verifica se uma transição de status é permitida.

        Args:
            current: Status atual.
            new_status: Status de destino.

        Returns:
            True se a transição é válida.
        """
        return new_status in VALID_TRANSITIONS.get(current, frozenset())


# ===========================================================================
# Orchestrator — loop principal Algorithm A4.5
# ===========================================================================

class Orchestrator:
    """
    Motor de coordenação LATTE que executa o Algorithm A4.5.

    Coordena Lead e Workers em rounds discretos, gerenciando o
    coordination graph G_t completamente em memória (ADR-002).

    Fluxo de cada round:
        1. Heartbeat monitoring (straggler detection)
        2. Frontier identification (F_t)
        3. Agent dispatching (assign ociosos, re-engage ocupados)
        4. Parallel execution (Lead + Workers)
        5. Termination check

    Attributes:
        graph: CoordinationGraph — o grafo atual G_t.
        task_description: Descrição original da task (fase de planning).
        config: Dicionário de configuração (max_rounds, heartbeat_threshold, ...).
    """

    def __init__(self, task_description: str,
                 G_0: CoordinationGraph,
                 config: Optional[dict[str, Any]] = None) -> None:
        """
        Inicializa o orchestrator com G_0 e configuração.

        Args:
            task_description: Descrição textual da feature/task a executar.
            G_0: Coordination graph inicial (carregado do tasks.md ou gerado).
            config: Configurações opcionais:
                - max_rounds (int, default 40): T_max.
                - heartbeat_threshold (int, default 4): H para straggler.
                - verbose (bool, default False): logging detalhado.
        """
        self.task_description = task_description
        self.graph = G_0

        cfg = config or {}
        self.max_rounds: int = cfg.get(
            "max_rounds", self.graph.max_rounds
        )
        self.heartbeat_threshold: int = cfg.get(
            "heartbeat_threshold", self.graph.heartbeat_threshold
        )
        self.verbose: bool = cfg.get("verbose", False)

        # Feature 005 — Hardening config
        self.max_llm_calls: int = cfg.get(
            "max_llm_calls", self.graph.max_llm_calls
        )
        self.operator_timeout: int = cfg.get(
            "operator_timeout", self.graph.operator_timeout
        )
        # Forward max_llm_calls / operator_timeout from config to graph metadata
        if "max_llm_calls" in cfg:
            self.graph.max_llm_calls = self.max_llm_calls
        if "operator_timeout" in cfg:
            self.graph._graph["metadata"]["operator_timeout"] = self.operator_timeout

        # Estado de heartbeat: Worker ID → contador de rounds inativos
        self._heartbeat_counters: dict[str, int] = {}

        # Flag para indicar que o Lead deve ser invocado neste round
        self._lead_must_act: bool = False

        # Flag para indicar mudanças no grafo desde o último round do Lead
        self._graph_changed_since_lead: bool = False

        if self.verbose:
            logger.info(
                "Orchestrator inicializado: feature=%s, workers=%d, "
                "max_rounds=%d, H=%d, |V_0|=%d, |E_0|=%d",
                self.graph.feature_id,
                len(self.graph.workers),
                self.max_rounds,
                self.heartbeat_threshold,
                self.graph.get_node_count(),
                self.graph.get_edge_count(),
            )

    # ------------------------------------------------------------------
    # Phase 1: Main execution loop
    # ------------------------------------------------------------------

    def run(self) -> CoordinationGraph:
        """
        Executa o loop principal de rounds (Phase 1 do Algorithm A4.5).

        Para cada round t = 1..T_max:
            1. Heartbeat monitoring
            2. Frontier identification
            3. Agent dispatching
            4. Parallel execution
            5. Termination check

        Returns:
            G_final — o coordination graph após conclusão ou timeout.

        Raises:
            RuntimeError: Se uma invariante do grafo for violada.
        """
        if self.verbose:
            logger.info("=== LATTE Execution: Phase 1 (loop de rounds) ===")

        for t in range(1, self.max_rounds + 1):
            self.graph.round = t

            if self.verbose:
                logger.info(
                    "--- Round %d/%d --- |V|=%d, |E|=%d, llm_calls=%d/%d",
                    t, self.max_rounds,
                    self.graph.get_node_count(),
                    self.graph.get_edge_count(),
                    self.graph.llm_calls_made,
                    self.graph.max_llm_calls,
                )

            # Passo 0: Budget check (Feature 005, ADR-006)
            if self.graph.is_budget_exhausted():
                if self.verbose:
                    logger.warning(
                        "  ⚠ Budget exhausted: %d/%d LLM calls — force_finalize",
                        self.graph.llm_calls_made,
                        self.graph.max_llm_calls,
                    )
                self._force_finalize()
                return self.graph

            # Feature 005 (ADR-010): Context summarization a cada 4 rounds
            self._maybe_summarize()

            # Passo 1: Heartbeat monitoring
            stragglers = self._heartbeat_check()

            # Passo 2: Frontier identification
            frontier = self._compute_frontier()

            # Passo 3: Agent dispatching
            dispatch_plan = self._dispatch_agents(frontier, stragglers)

            # Passo 4: Parallel execution
            self._execute_round(dispatch_plan, frontier)

            # Passo 5: Termination check
            if self._check_termination():
                if self.verbose:
                    logger.info(
                        "=== LATTE Execution: CONCLUÍDO no round %d ===", t
                    )
                return self.graph

        # Timeout: max_rounds atingido sem completion total
        if self.verbose:
            logger.warning(
                "=== LATTE Execution: TIMEOUT após %d rounds ===",
                self.max_rounds,
            )
        return self.graph

    # ------------------------------------------------------------------
    # Passo 1: Heartbeat monitoring
    # ------------------------------------------------------------------

    def _heartbeat_check(self) -> list[str]:
        """
        Passo 1 do Algorithm A4.5: heartbeat monitoring.

        Detecta Workers que estão sem ação por H rounds consecutivos
        (straggler detection) e notifica o Lead.

        Delega a lógica para o módulo heartbeat.py (T005), que analisa
        o histórico do grafo para determinar quais Workers emitiram
        ações (Claim, Complete, Discover) neste round.

        Returns:
            Lista de Worker IDs classificados como stragglers.

        Reference:
            - latte-protocol.md, Seção 6 (Heartbeat Monitoring)
            - heartbeat.py (T005)
        """
        try:
            from .heartbeat import check_heartbeat
        except ImportError:
            from heartbeat import check_heartbeat  # fallback: execução direta

        straggler_entries = check_heartbeat(
            graph=self.graph,
            inactivity_counters=self._heartbeat_counters,
            H=self.heartbeat_threshold,
        )

        # Extrai apenas os worker_ids únicos para a interface legada
        # (o dispatch_plan em Passo 3 espera list[str])
        stragglers: list[str] = list(
            dict.fromkeys(entry["worker_id"] for entry in straggler_entries)
        )

        if self.verbose and stragglers:
            logger.warning(
                "  ⚠ Stragglers detectados no round %d: %s",
                self.graph.round, stragglers,
            )

        return stragglers

    # ------------------------------------------------------------------
    # Passo 2: Frontier identification
    # ------------------------------------------------------------------

    def _compute_frontier(self) -> list[str]:
        """
        Passo 2 do Algorithm A4.5: calcula o frontier F_t.

        F_t := { v ∈ V_t | status(v) = pending
                 ∧ ∀(u,v) ∈ E_t, status(u) ∈ {done, verified} }

        Delega para compute_frontier() do módulo frontier.py (T006).

        Returns:
            Lista ordenada de node IDs no frontier.

        Reference:
            - graph-schema.md, Seção 3 (Definição formal do Frontier)
            - graph-schema.md, Seção 4.3 (compute_frontier)
            - T006: frontier.py
        """
        frontier = compute_frontier(self.graph)

        if self.verbose:
            logger.info("  F_%d = %s", self.graph.round, frontier)

        return frontier

    # ------------------------------------------------------------------
    # Passo 3: Agent dispatching
    # ------------------------------------------------------------------

    def _dispatch_agents(self, frontier: list[str],
                         stragglers: list[str]) -> dict[str, Any]:
        """
        Passo 3 do Algorithm A4.5: agent dispatching.

        Delega para o módulo dispatcher.py (T007), que implementa:
          - Re-engaja Workers ocupados com novo contexto
          - Atribui Workers ociosos a tasks em F_t (máx 1 por Worker)
          - Context scoping restrito (ADR-004): Workers recebem só sua
            task description + outputs de dependências diretas concluídas
          - Prepara assignments para delegate_task (ADR-003)

        Returns:
            Um dispatch_plan com estrutura:
                {
                    "lead_action": bool,
                    "assignments": [
                        {
                            "worker": str,
                            "task": str,
                            "action": str,      # "assign" ou "re_engage"
                            "context": {
                                "task_description": str,
                                "dependency_outputs": {dep_id: output, ...},
                            },
                        },
                        ...
                    ],
                    "metadata": {...},
                }

        Reference:
            - plan.md, ADR-003 (delegate_task como spawn)
            - plan.md, ADR-004 (context scoping restrito)
            - T007: dispatcher.py
        """
        try:
            from .dispatcher import dispatch
        except ImportError:
            from dispatcher import dispatch  # fallback: execução direta

        # Classifica Workers em busy/idle baseado no estado atual do grafo
        # (reutiliza a lógica do dispatcher para consistência)
        try:
            from .dispatcher import _classify_workers, _build_completed_outputs_map
        except ImportError:
            from dispatcher import _classify_workers, _build_completed_outputs_map

        busy_workers, idle_workers = _classify_workers(
            self.graph, self.graph.workers
        )

        # Dispatch principal via T007
        dispatch_plan = dispatch(
            graph=self.graph,
            frontier=frontier,
            busy_workers=busy_workers,
            idle_workers=idle_workers,
        )

        # --- Override de lead_action com flags internas do Orchestrator ---
        # O dispatcher decide lead_action por critérios estruturais do grafo.
        # O orchestrator adiciona critérios operacionais:
        #   - Grafo mudou desde o último round do Lead
        #   - Stragglers detectados via heartbeat
        #   - Lead ocioso por H rounds
        lead_must_act = (
            self._graph_changed_since_lead
            or len(stragglers) > 0
            or self._lead_must_act
        )

        if lead_must_act:
            dispatch_plan["lead_action"] = True
            self._graph_changed_since_lead = False

        # Garante que Lead age no primeiro round
        if self.graph.round == 1:
            dispatch_plan["lead_action"] = True

        if self.verbose:
            meta = dispatch_plan.get("metadata", {})
            logger.info(
                "  Dispatch: lead=%s, re_engage=%d, assign=%d, "
                "frontier=%d, busy=%d, idle=%d",
                dispatch_plan["lead_action"],
                meta.get("re_engage_count", 0),
                meta.get("assign_count", 0),
                len(frontier),
                len(busy_workers),
                len(idle_workers),
            )

        return dispatch_plan

    # ------------------------------------------------------------------
    # Passo 4: Parallel execution
    # ------------------------------------------------------------------

    def _execute_round(self, dispatch_plan: dict[str, Any],
                       frontier: list[str]) -> None:
        """
        Passo 4 do Algorithm A4.5: parallel execution.

        Executa as ações dos agentes neste round:
          - Lead recebe G_t completo e emite ações (Assign, Release, ...)
          - Workers recebem apenas sua task + outputs de dependências diretas
          - Ações emitidas são aplicadas ao grafo via operadores

        IMPLEMENTAÇÃO FUTURA:
            Será implementado em T008 (lead_operators.py) e
            T009 (worker_operators.py). Este stub aplica as ações
            do dispatch_plan como Assign + Claim simulados.

        Reference:
            - latte-protocol.md, Seção 7 (Protocolo de Execução)
            - latte-protocol.md, Seção 3 (Formato de mensagens)
            - T008: lead_operators.py
            - T009: worker_operators.py
        """
        # --- Lead execution ---
        if dispatch_plan.get("lead_action"):
            self._execute_lead()

        # --- Workers execution ---
        for assignment in dispatch_plan.get("assignments", []):
            self._execute_worker(
                worker_id=assignment["worker"],
                task_id=assignment["task"],
            )

    def _execute_lead(self) -> None:
        """
        Executa o turno do Lead neste round.

        O Lead recebe G_t completo e pode emitir ações:
          - Assign: atribuir tasks pending do frontier a Workers
          - Release: devolver tasks de stragglers ao pool
          - Close: forçar done em tasks concluídas mas não sinalizadas
          - Verify: spawnar verificação para nós de alto risco
          - Discover: adicionar novas tasks ao grafo

        IMPLEMENTAÇÃO FUTURA:
            Será implementado em T008: lead_operators.py.

        Reference:
            - latte-protocol.md, Seção 3.1 (Ações do Lead)
            - latte-protocol.md, Seção 7.1 (Lead responsibilities)
            - T008: lead_operators.py
        """
        # Stub: Lead não executa ações reais
        # TODO(T008): implementar execução real do Lead via delegate_task
        # com prompt que inclui G_t completo + contexto de coordenação
        if self.verbose:
            logger.info("  Lead ℓ: avaliando G_%d (stub)", self.graph.round)

    def _execute_worker(self, worker_id: str, task_id: str) -> None:
        """
        Executa o turno de um Worker neste round.

        O Worker recebe apenas: descrição da sua task + outputs das
        dependências diretas concluídas (ADR-004: context scoping).

        Feature 005 (ADR-007): timeout por operador com fallback.
        Se o worker exceder operator_timeout segundos, executa fallback_fn
        e registra o erro no grafo.

        O Worker pode emitir ações:
          - Claim: reivindicar task do frontier
          - Complete: sinalizar conclusão
          - Discover: propor nova task (Lead avalia)

        Reference:
            - latte-protocol.md, Seção 3.2 (Ações dos Workers)
            - plan.md, ADR-003 (delegate_task)
            - plan.md, ADR-004 (context scoping)
            - plan.md, ADR-007 (timeout + fallback)
            - T009: worker_operators.py
        """
        # Feature 005 (ADR-007): timeout wrapper
        # FUTURE: quando delegate_task real for implementado, envolver em:
        #   asyncio.wait_for(delegate_task(...), timeout=self.operator_timeout)
        # Por enquanto, stub — Worker não executa ações reais
        self.graph.increment_llm_calls(1)  # Conta a call do worker stub

        if self.verbose:
            logger.info(
                "  Worker %s: task=%s (stub — T009 pendente, timeout=%ds)",
                worker_id, task_id, self.operator_timeout,
            )

    # ------------------------------------------------------------------
    # Passo 5: Termination check
    # ------------------------------------------------------------------

    def _check_termination(self) -> bool:
        """
        Passo 5 do Algorithm A4.5: verifica condição de parada.

        Critério: todos os nós estão com status em {done, verified}.

        Returns:
            True se a execução deve terminar, False para continuar.
        """
        if self.graph.get_node_count() == 0:
            # Grafo vazio: nada a fazer
            return True

        return self.graph.is_terminal()

    def _force_finalize(self) -> None:
        """
        Força finalização quando budget de LLM calls é excedido (ADR-006).

        Marca todas as tasks pending/assigned/in_progress como 'done' com
        flag 'budget_exhausted' para que o G_final reflita o estado forçado.
        """
        for node in self.graph.nodes:
            if node["status"] not in TERMINAL_STATUSES:
                old_status = node["status"]
                node["status"] = "done"
                node.setdefault("output", "[BUDGET EXHAUSTED] Task force-finalized")
                self.graph.add_history_entry(
                    operator="ForceFinalize",
                    node_id=node["id"],
                    agent="system",
                    details={
                        "reason": "budget_exhausted",
                        "previous_status": old_status,
                        "llm_calls_made": self.graph.llm_calls_made,
                        "max_llm_calls": self.graph.max_llm_calls,
                    },
                )
        self.graph._invalidate_cache()

    def _maybe_summarize(self) -> None:
        """
        Feature 005 (ADR-010): Sumariza completed tasks a cada 4 rounds.

        Inspirado no paper Multi-Agent Systems: "By turn 8, coordinator
        starts making routing decisions based on what it read recently."
        A sumarização condensa o histórico em 1-2 linhas.
        """
        self.graph.round_since_summary += 1
        summary_interval = DEFAULT_SUMMARY_INTERVAL

        if self.graph.round_since_summary < summary_interval:
            return  # Ainda não é hora de sumarizar

        # Coleta completed tasks
        done_nodes = [
            n for n in self.graph.nodes
            if n["status"] in ("done", "verified")
        ]
        if len(done_nodes) < 5:
            return  # Poucas tasks completadas — não vale sumarizar

        # Constrói sumário simples: "T001 (desc), T002 (desc), ..."
        task_summaries = []
        for n in done_nodes[-8:]:  # Últimas 8 tasks
            desc = n.get("description", n["id"])
            task_summaries.append(f"{n['id']}: {desc[:60]}")

        summary = (
            f"Resumo (rounds {self.graph.round - summary_interval + 1}"
            f"-{self.graph.round}): {len(task_summaries)} tasks concluídas. "
            + "; ".join(task_summaries)
        )

        self.graph.completed_summary = summary
        self.graph.round_since_summary = 0

        if self.verbose:
            logger.info("  📋 Context summarization: %s", summary[:120])


# ===========================================================================
# load_G0_from_tasks_md — parser do tasks.md
# ===========================================================================

def load_G0_from_tasks_md(path: str | Path) -> CoordinationGraph:
    """
    Carrega G_0 a partir de um arquivo tasks.md.

    Suporta dois modos de carregamento:
      1. Se a seção `## Coordination Graph` está presente, parseia-a
         diretamente para construir G_0.
      2. Caso contrário, infere G_0 a partir da lista de tasks e seus
         campos `depends_on` / `Dependências` / `agent`.

    Suporta dois modos de YAML frontmatter:
      - graph-operators: enabled → modo LATTE completo (graph-operators ativos)
      - graph-operators ausente / disabled → modo legacy (compatibilidade reversa)

    Extrai também os metadados do YAML frontmatter:
      - feature_id: derivado do path ou spec associada
      - heartbeat_threshold: de `heartbeat-threshold` no frontmatter (default: 4)
      - max_rounds: de `max-rounds` no frontmatter (default: 40)

    Args:
        path: Caminho para o arquivo tasks.md.

    Returns:
        CoordinationGraph inicializado com G_0.

    Raises:
        FileNotFoundError: Se o arquivo não existe.

    Reference:
        - latte-task-rules.md (extensão do tasks.md com LATTE)
        - graph-schema.md, Seção 5.2 (G_0 mínimo)
        - graph-schema.md, Seção 5.3 (G_0 com 3 tasks de exemplo)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"tasks.md not found: {path}")

    content = path.read_text(encoding="utf-8")

    # --- Parse YAML frontmatter ---
    frontmatter = _parse_frontmatter(content)

    graph_operators = frontmatter.get("graph-operators", "disabled")

    heartbeat_threshold = int(
        frontmatter.get("heartbeat-threshold", DEFAULT_HEARTBEAT_THRESHOLD)
    )
    max_rounds = int(frontmatter.get("max-rounds", DEFAULT_MAX_ROUNDS))

    # Feature 005 — Hardening frontmatter fields
    max_llm_calls = int(
        frontmatter.get("max-llm-calls", DEFAULT_MAX_LLM_CALLS)
    )
    operator_timeout = int(
        frontmatter.get("operator-timeout", DEFAULT_OPERATOR_TIMEOUT)
    )
    verify_mode = frontmatter.get("verify-mode", DEFAULT_VERIFY_MODE)
    if verify_mode not in VALID_VERIFY_MODES:
        logger.warning(
            "Invalid verify-mode '%s' in tasks.md, falling back to '%s'",
            verify_mode, DEFAULT_VERIFY_MODE,
        )
        verify_mode = DEFAULT_VERIFY_MODE

    # --- Derive metadata ---
    feature_id = _derive_feature_id(path)

    # --- Parse agents from tasks ---
    lead, workers = _parse_agents_from_tasks(content)
    if not lead:
        lead = "Lead"  # fallback

    # --- Build G_0 ---
    graph = CoordinationGraph(
        feature_id=feature_id,
        lead=lead,
        workers=workers,
        max_rounds=max_rounds,
        heartbeat_threshold=heartbeat_threshold,
        graph_operators=graph_operators,
        max_llm_calls=max_llm_calls,
        operator_timeout=operator_timeout,
        verify_mode=verify_mode,
    )

    # --- Parse nodes and edges ---
    if "## Coordination Graph" in content:
        _parse_coordination_graph_section(graph, content)
    else:
        _infer_G0_from_tasks(graph, content)

    if __debug__:
        logger.info(
            "G_0 loaded: feature=%s, |V|=%d, |E|=%d, workers=%s",
            feature_id,
            graph.get_node_count(),
            graph.get_edge_count(),
            workers,
        )

    return graph


# ------------------------------------------------------------------
# Helper functions for load_G0_from_tasks_md
# ------------------------------------------------------------------

def _parse_frontmatter(content: str) -> dict[str, str]:
    """
    Extrai YAML frontmatter do início de um arquivo Markdown.

    Espera o formato:
        ---
        key: value
        ---

    Args:
        content: Conteúdo completo do arquivo.

    Returns:
        Dicionário com as chaves do frontmatter (valores como strings).
    """
    frontmatter: dict[str, str] = {}
    if not content.startswith("---"):
        return frontmatter

    lines = content.split("\n")
    end = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break

    for line in lines[1:end]:
        match = re.match(r"^(\S[^:]*):\s*(.*)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            frontmatter[key] = value

    return frontmatter


def _derive_feature_id(path: Path) -> str:
    """
    Deriva o feature_id a partir do caminho do tasks.md.

    Heurística: procura por padrão `specs/features/NNN-*/tasks.md`
    ou `NNN-*` no caminho.
    """
    # Tenta extrair do path: specs/features/001-latte_coordination/tasks.md
    parts = path.parts
    for i, part in enumerate(parts):
        if part == "features" and i + 1 < len(parts):
            feat_dir = parts[i + 1]
            match = re.match(r"^(\d+)", feat_dir)
            if match:
                return match.group(1)

    # Fallback: usa o nome do diretório pai
    parent = path.parent.name
    match = re.match(r"^(\d+)", parent)
    if match:
        return match.group(1)

    return "000"


def _parse_agents_from_tasks(content: str) -> tuple[str | None, list[str]]:
    """
    Extrai Lead e Workers das tasks.

    Procura por padrões como:
      - **agent:** Lead
      - **agent:** Dev1

    Returns:
        Tuple (lead, workers). lead é None se não encontrado.
    """
    lead: str | None = None
    workers_set: set[str] = set()

    for match in re.finditer(r"\*\*agent:\*\*\s*(\S+)", content):
        agent = match.group(1).strip()
        if agent.lower() == "lead":
            lead = agent
        else:
            workers_set.add(agent)

    # Ordena workers para determinismo
    workers = sorted(workers_set)
    if not workers:
        workers = ["Dev1", "Dev2"]  # default mínimo

    return lead, workers


def _parse_coordination_graph_section(graph: CoordinationGraph,
                                      content: str) -> None:
    """
    Parseia a seção `## Coordination Graph` e popula G_0.

    Extrai nodes, edges, assignments e ready do formato descrito em
    latte-task-rules.md (Seção "## Coordination Graph").

    Args:
        graph: CoordinationGraph sendo construído.
        content: Conteúdo completo do tasks.md.
    """
    # Extrai a seção Coordination Graph
    section_match = re.search(
        r"## Coordination Graph\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if not section_match:
        _infer_G0_from_tasks(graph, content)
        return

    section = section_match.group(1)

    # Parse nodes
    nodes_match = re.search(r"\*\*nodes:\*\*\s*(.+)", section)
    if nodes_match:
        node_ids = [nid.strip() for nid in nodes_match.group(1).split(",")]
    else:
        node_ids = []

    # Parse edges
    edges: list[tuple[str, str]] = []
    for edge_match in re.finditer(
        r"-\s*(\S+)\s*→\s*(\S+)", section
    ):
        edges.append((edge_match.group(1), edge_match.group(2)))

    # Parse assignments
    assignments: dict[str, str] = {}
    for assign_match in re.finditer(
        r"-\s*(\S+):\s*(\S+)", section
    ):
        task_id = assign_match.group(1)
        agent = assign_match.group(2)
        # Evita capturar linhas que não são assignments (ex: "ready")
        if task_id in node_ids or re.match(r"^T\d+", task_id):
            assignments[task_id] = agent

    # Build deps map from edges: target → [sources]
    deps_map: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for src, tgt in edges:
        if tgt not in deps_map:
            deps_map[tgt] = []
        deps_map[tgt].append(src)

    # Create nodes
    for nid in node_ids:
        node_data = {
            "id": nid,
            "agent": assignments.get(nid),
            "status": "pending",
            "deps": deps_map.get(nid, []),
            "description": f"Task {nid}",
            "output": None,
            "rounds_inactive": 0,
            "created_at_round": 0,
            "assigned_at_round": 0 if nid in assignments else None,
            "completed_at_round": None,
        }
        try:
            graph.add_node(node_data)
            graph.add_history_entry(
                operator="Discover",
                node_id=nid,
                agent=assignments.get(nid, graph.lead),
                details={"description": node_data["description"]},
            )
        except ValueError:
            pass  # Node já existe (duplicado no markup)


def _infer_G0_from_tasks(graph: CoordinationGraph, content: str) -> None:
    """
    Infere G_0 a partir das tasks no corpo do arquivo.

    Lógica de inferência automática (latte-task-rules.md):
      - Cada task `- [ ] **Tnnn:** ...` vira um nó.
      - `depends_on: [Txxx, Tyyy]` ou `Dependências: Txxx, Tyyy` definem arestas.
      - `agent: Lead|Dev1|...` define o agente inicial.
      - Tasks sem `agent` ficam unassigned (⊥).

    Args:
        graph: CoordinationGraph sendo construído.
        content: Conteúdo completo do tasks.md.
    """
    # Encontra todas as tasks no formato: - [ ] **Tnnn:** descrição
    task_pattern = re.compile(
        r"^- \[[ x]\] \*\*(T\d+):\*\*\s*(.+?)$",
        re.MULTILINE,
    )

    # Mapa temporário: task_id → {description, agent, deps}
    tasks_raw: dict[str, dict[str, Any]] = {}

    lines = content.split("\n")
    current_task: str | None = None

    for line in lines:
        # Detecta início de task
        task_match = task_pattern.match(line)
        if task_match:
            current_task = task_match.group(1)
            description = task_match.group(2).strip()
            tasks_raw[current_task] = {
                "description": description,
                "agent": None,
                "deps": [],
            }
            continue

        if current_task is None:
            continue

        stripped = line.strip()

        # Detecta agent
        agent_match = re.match(r"^\*\*agent:\*\*\s*(\S+)", stripped)
        if agent_match:
            tasks_raw[current_task]["agent"] = agent_match.group(1)
            continue

        # Detecta depends_on (formato lista YAML)
        deps_match = re.match(
            r"^\*\*depends_on:\*\*\s*\[(.+?)\]", stripped
        )
        if deps_match:
            deps_str = deps_match.group(1)
            deps = [
                d.strip().strip("'\"")
                for d in deps_str.split(",")
                if d.strip()
            ]
            tasks_raw[current_task]["deps"] = deps
            continue

        # Detecta Dependências (formato legado: string)
        deps_legacy = re.match(
            r"^\*\*Dependências:\*\*\s*(.+)", stripped
        )
        if deps_legacy and "depends_on" not in stripped:
            deps_str = deps_legacy.group(1).strip()
            if deps_str.lower() == "nenhuma" or deps_str.lower() == "none":
                tasks_raw[current_task]["deps"] = []
            else:
                tasks_raw[current_task]["deps"] = [
                    d.strip() for d in deps_str.split(",")
                ]
            continue

        # Linha em branco encerra o bloco da task atual
        if stripped == "":
            current_task = None

    # Cria os nós no grafo
    for task_id, task_data in tasks_raw.items():
        node_data = {
            "id": task_id,
            "agent": task_data["agent"],
            "status": "pending",
            "deps": task_data["deps"],
            "description": task_data["description"],
            "output": None,
            "rounds_inactive": 0,
            "created_at_round": 0,
            "assigned_at_round": 0 if task_data["agent"] else None,
            "completed_at_round": None,
        }
        try:
            graph.add_node(node_data)
            graph.add_history_entry(
                operator="Discover",
                node_id=task_id,
                agent=task_data.get("agent") or graph.lead,
                details={
                    "description": task_data["description"],
                    "deps": task_data["deps"],
                },
            )
        except ValueError:
            pass  # Node já existe


# ===========================================================================
# Main (para testes manuais)
# ===========================================================================

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 60)
    print("LATTE Orchestrator — Teste de G_0 mínimo")
    print("=" * 60)

    # Teste 1: G_0 vazio
    g0 = CoordinationGraph(
        feature_id="001",
        lead="Lead",
        workers=["Dev1", "Dev2"],
    )
    print(f"\nG_0 vazio:")
    print(f"  round={g0.round}, |V|={g0.get_node_count()}, "
          f"|E|={g0.get_edge_count()}")
    print(f"  is_terminal={g0.is_terminal()} (esperado: True)")

    # Teste 2: Adiciona nós manualmente (simula Discover)
    print(f"\nAdicionando nós via Discover...")
    g0.add_node({
        "id": "T001",
        "agent": None,
        "status": "pending",
        "deps": [],
        "description": "Task 1 — sem dependências",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })
    g0.add_node({
        "id": "T002",
        "agent": None,
        "status": "pending",
        "deps": ["T001"],
        "description": "Task 2 — depende de T001",
        "output": None,
        "rounds_inactive": 0,
        "created_at_round": 0,
        "assigned_at_round": None,
        "completed_at_round": None,
    })

    print(f"  round={g0.round}, |V|={g0.get_node_count()}, "
          f"|E|={g0.get_edge_count()}")
    print(f"  is_terminal={g0.is_terminal()} (esperado: False)")

    # Teste 3: Orchestrator com G_0
    print(f"\nExecutando Orchestrator.run()...")
    orch = Orchestrator(
        task_description="Feature 001: LATTE Coordination",
        G_0=g0,
        config={"verbose": True, "max_rounds": 2},
    )

    # Simula claim + complete de T001 (pending → in_progress → done)
    g0.update_node_status("T001", "in_progress", agent="Lead")
    g0.add_history_entry("Claim", "T001", "Lead",
                         {"from_status": "pending", "to_status": "in_progress"})
    print(f"  T001 → in_progress (Claim simulado)")

    g0.update_node_status("T001", "done", agent="Lead")
    g0.add_history_entry("Complete", "T001", "Lead",
                         {"from_status": "in_progress", "to_status": "done"})
    print(f"  T001 → done (Complete simulado)")

    result = orch.run()
    print(f"\nResultado final:")
    print(f"  round final={result.round}")
    print(f"  |V|={result.get_node_count()}, |E|={result.get_edge_count()}")
    print(f"  is_terminal={result.is_terminal()}")

    # Teste 4: Serialização
    print(f"\nJSON (G_final):")
    print(result.to_json())

    # Teste 5: Se tasks.md é passado como argumento, tenta carregar
    if len(sys.argv) > 1:
        tasks_path = Path(sys.argv[1])
        if tasks_path.exists():
            print(f"\n{'=' * 60}")
            print(f"Carregando G_0 de: {tasks_path}")
            print(f"{'=' * 60}")
            try:
                g0_from_md = load_G0_from_tasks_md(tasks_path)
                print(f"\nG_0 carregado:")
                print(f"  feature={g0_from_md.feature_id}")
                print(f"  lead={g0_from_md.lead}")
                print(f"  workers={g0_from_md.workers}")
                print(f"  |V|={g0_from_md.get_node_count()}")
                print(f"  |E|={g0_from_md.get_edge_count()}")
                print(f"  max_rounds={g0_from_md.max_rounds}")
                print(f"  H={g0_from_md.heartbeat_threshold}")
                for node in g0_from_md.nodes:
                    print(f"    {node['id']}: status={node['status']}, "
                          f"agent={node['agent']}, deps={node['deps']}")
            except Exception as e:
                print(f"Erro ao carregar: {e}")
