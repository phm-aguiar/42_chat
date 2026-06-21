#!/usr/bin/env python3
"""
dispatcher.py — Agent Dispatch + Context Scoping (T007)
========================================================

Implementa o Passo 3 do Algorithm A4.5 do paper LATTE: agent dispatching
com context scoping restrito (ADR-004) e delegate_task (ADR-003).

Lógica central:
  1. Classifica Workers em busy (com task in_progress) e idle (sem task ativa).
  2. Para Workers busy: constrói contexto de re-engajamento — outputs das
     dependências diretas que acabaram de completar neste round.
  3. Para Workers idle: atribui tasks do frontier F_t (máximo 1 por Worker).
  4. Aplica context scoping (ADR-004): cada Worker recebe APENAS:
     - Descrição da sua task
     - Outputs das dependências diretas concluídas (status ∈ {done, verified})
     - NÃO recebe spec.md, plan.md ou G_t completo.
  5. Prepara o dispatch plan com assignments + context para cada Worker.

Integração com o Orchestrator:
  → Importado por orchestrator.py no método _dispatch_agents().
  → Função principal: dispatch(graph, frontier, busy_workers, idle_workers).
  → Retorna dict com assignments e seus respectivos context scopes.

Referências:
  - plan.md, ADR-003 (delegate_task como spawn)
  - plan.md, ADR-004 (context scoping restrito)
  - latte-protocol.md, Seção 7 (Protocolo de Execução)
  - graph-schema.md, Seção 3 (Frontier F_t)
  - graph-schema.md, Seção 1.2 (Estrutura de nós: id, agent, status, deps, output)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes compartilhadas (sincronizadas com orchestrator.py)
# ---------------------------------------------------------------------------

# Status de nós que indicam Worker ocupado (ativo em uma task)
BUSY_NODE_STATUSES: frozenset[str] = frozenset({
    "assigned",
    "in_progress",
})

# Status que satisfazem dependência para contexto
# (outputs de nós done/verified devem ser incluídos no context scoping)
DEPENDENCY_SATISFIED_STATUSES: frozenset[str] = frozenset({"done", "verified"})

# Status terminais (não precisam de re-engajamento)
TERMINAL_STATUSES: frozenset[str] = frozenset({"done", "verified"})

# Feature 005 — Tool ceiling (ADR-011): toolsets por tipo de worker
TOOLSET_MAP: dict[str, list[str]] = {
    "Dev": ["terminal", "file", "patch"],
    "QA": ["terminal", "file"],
    "DevOps": ["terminal", "file"],
    "default": ["terminal", "file"],
}

# Feature 005 — Equal-weight merge instruction (ADR-012)
MERGE_EQUAL_WEIGHT_INSTRUCTION = (
    "Weight each input equally regardless of length. "
    "If an input is under 100 words, note: '[domain] was under-researched'."
)


# ===========================================================================
# Função principal: dispatch()
# ===========================================================================

def dispatch(
    graph: Any,
    frontier: list[str],
    busy_workers: Optional[list[str]] = None,
    idle_workers: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Passo 3 do Algorithm A4.5: agent dispatching com context scoping.

    Decide quais agentes agem neste round:
      - Re-engaja Workers ocupados com novo contexto (outputs de dependências
        que acabaram de completar).
      - Atribui Workers ociosos a tasks em F_t (máximo 1 por Worker).
      - Prepara context scoping (ADR-004): cada Worker recebe apenas
        sua task description + outputs das dependências diretas concluídas.

    Args:
        graph: CoordinationGraph com acesso a:
               - .workers → list[str]
               - .nodes → list[dict] (nós com id, agent, status, deps,
                 description, output)
               - .round → int
               - .lead → str
               - .get_node(node_id) → Optional[dict]
               - .get_status(node_id) → Optional[str]
        frontier: Lista ordenada de node IDs no frontier F_t.
        busy_workers: Lista opcional de Worker IDs ocupados. Se None,
                      é inferida a partir do grafo.
        idle_workers: Lista opcional de Worker IDs ociosos. Se None,
                      é inferida a partir do grafo.

    Returns:
        Um dispatch_plan com estrutura:
            {
                "lead_action": bool,       # Lead deve agir neste round?
                "assignments": [           # Workers → tasks com contexto
                    {
                        "worker": str,     # ID do Worker
                        "task": str,       # ID do nó/task
                        "action": str,     # "assign" (nova) ou "re_engage" (existente)
                        "context": {       # Context scoping (ADR-004)
                            "task_description": str,
                            "dependency_outputs": {
                                dep_id: str,  # output do nó dependência
                                ...
                            },
                        },
                    },
                    ...
                ],
                "metadata": {
                    "total_workers": int,
                    "busy_count": int,
                    "idle_count": int,
                    "frontier_size": int,
                },
            }

    Reference:
        - plan.md, ADR-003 (delegate_task)
        - plan.md, ADR-004 (context scoping)
        - graph-schema.md, Seção 3 (Frontier)
        - latte-protocol.md, Seção 7 (Protocolo de Execução)
    """
    workers: list[str] = list(graph.workers)

    # ------------------------------------------------------------------
    # Passo 1: Classificar Workers em busy vs idle
    # ------------------------------------------------------------------
    if busy_workers is None or idle_workers is None:
        inferred_busy, inferred_idle = _classify_workers(graph, workers)
        if busy_workers is None:
            busy_workers = inferred_busy
        if idle_workers is None:
            idle_workers = inferred_idle

    # ------------------------------------------------------------------
    # Passo 2: Construir mapa de outputs de dependências concluídas
    # ------------------------------------------------------------------
    # Este mapa é usado para context scoping — para cada nó, sabemos
    # quais outputs de dependências estão disponíveis.
    completed_outputs = _build_completed_outputs_map(graph)

    # ------------------------------------------------------------------
    # Passo 3: Re-engajar Workers busy com novo contexto
    # ------------------------------------------------------------------
    re_engage_assignments = _re_engage_busy_workers(
        graph=graph,
        busy_workers=busy_workers,
        completed_outputs=completed_outputs,
    )

    # ------------------------------------------------------------------
    # Passo 4: Atribuir Workers idle a tasks do frontier
    # ------------------------------------------------------------------
    assign_assignments = _assign_idle_workers(
        graph=graph,
        frontier=frontier,
        idle_workers=idle_workers,
        completed_outputs=completed_outputs,
    )

    # ------------------------------------------------------------------
    # Passo 5: Montar dispatch plan final
    # ------------------------------------------------------------------
    all_assignments = re_engage_assignments + assign_assignments

    dispatch_plan: dict[str, Any] = {
        "lead_action": _should_lead_act(graph, frontier, busy_workers, idle_workers),
        "assignments": all_assignments,
        "metadata": {
            "total_workers": len(workers),
            "busy_count": len(busy_workers),
            "idle_count": len(idle_workers),
            "frontier_size": len(frontier),
            "re_engage_count": len(re_engage_assignments),
            "assign_count": len(assign_assignments),
        },
    }

    if logger.isEnabledFor(logging.INFO):
        logger.info(
            "  Dispatch: lead=%s, re_engage=%d, assign=%d, frontier=%d, "
            "busy=%d, idle=%d",
            dispatch_plan["lead_action"],
            len(re_engage_assignments),
            len(assign_assignments),
            len(frontier),
            len(busy_workers),
            len(idle_workers),
        )

    return dispatch_plan


# ===========================================================================
# Passo 1: Classificação de Workers (busy vs idle)
# ===========================================================================

def _classify_workers(
    graph: Any,
    workers: list[str],
) -> tuple[list[str], list[str]]:
    """
    Classifica Workers em busy (com task ativa) e idle (sem task ativa).

    Um Worker é considerado busy se possui pelo menos um nó com status
    em {assigned, in_progress} atribuído a ele.

    Um Worker é considerado idle se NÃO possui nenhum nó ativo atribuído.

    Args:
        graph: CoordinationGraph com acesso a .nodes.
        workers: Lista de todos os Worker IDs.

    Returns:
        Tuple (busy_workers, idle_workers).
    """
    # Mapa: worker_id → conjunto de node IDs ativos
    busy_set: set[str] = set()

    for node in graph.nodes:
        agent = node.get("agent")
        status = node.get("status")
        if agent and agent in workers and status in BUSY_NODE_STATUSES:
            busy_set.add(agent)

    # Workers não-busy são idle
    idle_workers = [w for w in workers if w not in busy_set]

    # Preserva ordem original
    busy_workers = [w for w in workers if w in busy_set]

    return busy_workers, idle_workers


# ===========================================================================
# Passo 2: Mapa de outputs de dependências concluídas
# ===========================================================================

def _build_completed_outputs_map(
    graph: Any,
) -> dict[str, Optional[str]]:
    """
    Constrói um mapa node_id → output para todos os nós com status
    em {done, verified} (dependências satisfeitas).

    Este mapa é a base do context scoping: para cada task, podemos
    consultar quais outputs de suas dependências estão disponíveis.

    Args:
        graph: CoordinationGraph com acesso a .nodes.

    Returns:
        Dict[node_id → output], onde output é o conteúdo do campo
        'output' do nó (pode ser None se o nó não tem output registrado).
    """
    outputs: dict[str, Optional[str]] = {}
    for node in graph.nodes:
        if node.get("status") in DEPENDENCY_SATISFIED_STATUSES:
            outputs[node["id"]] = node.get("output")
    return outputs


# ===========================================================================
# Passo 3: Re-engajar Workers busy
# ===========================================================================

def _re_engage_busy_workers(
    graph: Any,
    busy_workers: list[str],
    completed_outputs: dict[str, Optional[str]],
) -> list[dict[str, Any]]:
    """
    Re-engaja Workers ocupados com novo contexto.

    Para cada Worker busy, encontra a task em in_progress e constrói
    um contexto atualizado com os outputs das dependências diretas que
    acabaram de completar.

    Isso permite que Workers em execução recebam informações de
    dependências que foram concluídas enquanto eles trabalhavam,
    sem precisar re-ler o grafo inteiro.

    Args:
        graph: CoordinationGraph.
        busy_workers: Lista de Worker IDs ocupados.
        completed_outputs: Mapa node_id → output para nós concluídos.

    Returns:
        Lista de assignments de re-engajamento, cada um com:
            {
                "worker": str,
                "task": str,
                "action": "re_engage",
                "context": {task_description, dependency_outputs},
            }
    """
    assignments: list[dict[str, Any]] = []

    for worker_id in busy_workers:
        # Encontra a(s) task(s) ativa(s) deste Worker
        active_tasks = _find_active_tasks_for_worker(graph, worker_id)

        for task_node in active_tasks:
            task_id = task_node["id"]
            task_description = task_node.get("description", f"Task {task_id}")

            # Constrói contexto de re-engajamento:
            # outputs das dependências diretas que estão concluídas
            dep_outputs = _build_dependency_context(
                node=task_node,
                completed_outputs=completed_outputs,
            )

            # Feature 005 — upstream errors (ADR-008) + toolsets (ADR-011)
            upstream_errors = _build_error_context(graph, task_node)
            toolsets = _get_toolset_for_worker(graph, worker_id, task_node)

            context = {
                "task_description": task_description,
                "dependency_outputs": dep_outputs,
                "upstream_errors": upstream_errors,
                "toolsets": toolsets,
                "merge_instruction": MERGE_EQUAL_WEIGHT_INSTRUCTION if dep_outputs else None,
            }

            assignments.append({
                "worker": worker_id,
                "task": task_id,
                "action": "re_engage",
                "context": context,
            })

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "  Re-engage: Worker %s → task %s (deps completadas: %s)",
                    worker_id, task_id, list(dep_outputs.keys()),
                )

    return assignments


def _find_active_tasks_for_worker(
    graph: Any,
    worker_id: str,
) -> list[dict[str, Any]]:
    """
    Encontra os nós ativos atribuídos a um Worker específico.

    Considera ativos nós com status em {assigned, in_progress}.
    Prioriza nós in_progress sobre assigned (um Worker pode ter
    múltiplos nós assigned mas só trabalha em um por vez).

    Args:
        graph: CoordinationGraph com acesso a .nodes.
        worker_id: ID do Worker.

    Returns:
        Lista de dicts dos nós ativos, ordenados: in_progress primeiro.
    """
    active_nodes: list[dict[str, Any]] = []
    for node in graph.nodes:
        if (
            node.get("agent") == worker_id
            and node.get("status") in BUSY_NODE_STATUSES
        ):
            active_nodes.append(node)

    # Ordena: in_progress primeiro (Worker está trabalhando ativamente),
    # depois assigned (Worker ainda não iniciou)
    active_nodes.sort(
        key=lambda n: 0 if n["status"] == "in_progress" else 1
    )

    return active_nodes


# ===========================================================================
# Passo 4: Atribuir Workers idle a tasks do frontier
# ===========================================================================

def _assign_idle_workers(
    graph: Any,
    frontier: list[str],
    idle_workers: list[str],
    completed_outputs: dict[str, Optional[str]],
) -> list[dict[str, Any]]:
    """
    Atribui Workers ociosos a tasks do frontier F_t.

    Regras:
      - Cada Worker idle recebe no MÁXIMO 1 task.
      - Tasks são consumidas do frontier em ordem (menos dependências primeiro).
      - Se há mais Workers idle que tasks no frontier, alguns Workers
        permanecem ociosos neste round.
      - Se há mais tasks no frontier que Workers idle, tasks restantes
        ficam para o próximo round ou para Claims espontâneos.

    Args:
        graph: CoordinationGraph.
        frontier: Lista ordenada de node IDs no frontier.
        idle_workers: Lista de Worker IDs ociosos.
        completed_outputs: Mapa node_id → output para nós concluídos.

    Returns:
        Lista de assignments de atribuição, cada um com:
            {
                "worker": str,
                "task": str,
                "action": "assign",
                "context": {task_description, dependency_outputs},
            }
    """
    assignments: list[dict[str, Any]] = []

    # Faz uma cópia local da lista de idle workers (consumível)
    available_workers = list(idle_workers)

    for task_id in frontier:
        if not available_workers:
            break  # Sem Workers idle disponíveis

        # Pega o próximo Worker idle
        worker_id = available_workers.pop(0)

        # Obtém o nó da task
        task_node = graph.get_node(task_id)
        if task_node is None:
            logger.warning(
                "  ⚠ Task '%s' no frontier não encontrada no grafo — ignorada",
                task_id,
            )
            continue

        task_description = task_node.get("description", f"Task {task_id}")

        # Constrói context scoping (ADR-004):
        # APENAS task description + outputs das dependências diretas concluídas
        dep_outputs = _build_dependency_context(
            node=task_node,
            completed_outputs=completed_outputs,
        )

        # Feature 005 — upstream errors (ADR-008) + toolsets (ADR-011)
        upstream_errors = _build_error_context(graph, task_node)
        toolsets = _get_toolset_for_worker(graph, worker_id, task_node)

        context = {
            "task_description": task_description,
            "dependency_outputs": dep_outputs,
            "upstream_errors": upstream_errors,
            "toolsets": toolsets,
            "merge_instruction": MERGE_EQUAL_WEIGHT_INSTRUCTION if dep_outputs else None,
        }

        assignments.append({
            "worker": worker_id,
            "task": task_id,
            "action": "assign",
            "context": context,
        })

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "  Assign: Worker %s ← task %s (deps: %s)",
                worker_id, task_id, list(dep_outputs.keys()),
            )

    if logger.isEnabledFor(logging.DEBUG) and frontier and not assignments:
        logger.debug(
            "  Assign: nenhum Worker idle disponível para %d tasks no frontier",
            len(frontier),
        )

    return assignments


# ===========================================================================
# Context Scoping (ADR-004)
# ===========================================================================

def _build_dependency_context(
    node: dict[str, Any],
    completed_outputs: dict[str, Optional[str]],
) -> dict[str, Optional[str]]:
    """
    Constrói o contexto de dependências diretas para uma task.

    ADR-004: Workers recebem APENAS outputs das dependências DIRETAS
    concluídas — NÃO recebem o grafo completo, spec.md, ou plan.md.

    Para cada dependência direta do nó:
      - Se está em {done, verified}: inclui seu output no contexto.
      - Se NÃO está concluída: a task não deveria estar no frontier
        (pré-condição do frontier), mas por segurança, omite do contexto.

    Args:
        node: Dict do nó da task (com campo 'deps').
        completed_outputs: Mapa node_id → output para nós concluídos.

    Returns:
        Dict[dep_id → output] contendo apenas as dependências diretas
        que estão concluídas. output pode ser None se o nó concluído
        não registrou output.
    """
    dep_outputs: dict[str, Optional[str]] = {}

    for dep_id in node.get("deps", []):
        if dep_id in completed_outputs:
            dep_outputs[dep_id] = completed_outputs[dep_id]
        # else: dependência não está concluída — não deve acontecer
        # para nós no frontier, mas é seguro omitir

    return dep_outputs


def _build_error_context(
    graph: Any,
    node: dict[str, Any],
) -> list[dict]:
    """
    Feature 005 (ADR-008): coleta upstream errors para uma task.

    Para cada dependência direta do nó, verifica se houve erro registrado
    no grafo. Retorna lista de erros relevantes para o context scoping.

    Args:
        graph: CoordinationGraph com acesso a .errors.
        node: Dict do nó da task (com campo 'deps').

    Returns:
        Lista de dicts de erro onde node_id está nas deps do nó.
    """
    errors = getattr(graph, "errors", [])
    if not errors:
        return []

    deps = set(node.get("deps", []))
    return [e for e in errors if e.get("node_id") in deps]


def _get_toolset_for_worker(
    graph: Any,
    worker_id: str,
    task_node: dict[str, Any],
) -> list[str]:
    """
    Feature 005 (ADR-011): determina toolsets para um worker/task.

    Prioridade:
      1. Campo 'toolsets' no nó da task (tasks.md)
      2. Tipo do agente (Dev/QA/DevOps) → TOOLSET_MAP
      3. default

    Args:
        graph: CoordinationGraph.
        worker_id: ID do worker.
        task_node: Dict do nó da task.

    Returns:
        Lista de toolset names.
    """
    # 1. Campo toolsets no nó
    if "toolsets" in task_node:
        return task_node["toolsets"]

    # 2. Inferir do nome do worker (ex: "worker-dev-1" → Dev)
    for role in ("DevOps", "Dev", "QA"):
        if role.lower() in worker_id.lower():
            return TOOLSET_MAP.get(role, TOOLSET_MAP["default"])

    return TOOLSET_MAP["default"]


def build_context_for_task(
    graph: Any,
    task_id: str,
) -> dict[str, Any]:
    """
    Constrói o contexto completo para uma task específica (API pública).

    Útil para quando o orchestrator precisa construir contexto para
    uma task fora do fluxo normal de dispatch (ex: Claim espontâneo,
    re-engajamento manual).

    Args:
        graph: CoordinationGraph.
        task_id: ID do nó da task.

    Returns:
        Dict com:
            {
                "task_description": str,
                "dependency_outputs": {dep_id: output, ...},
                "task_status": str,
                "task_agent": str | None,
            }

    Raises:
        KeyError: Se task_id não existe no grafo.
    """
    task_node = graph.find_node(task_id)
    completed_outputs = _build_completed_outputs_map(graph)

    dep_outputs = _build_dependency_context(
        node=task_node,
        completed_outputs=completed_outputs,
    )

    return {
        "task_description": task_node.get("description", f"Task {task_id}"),
        "dependency_outputs": dep_outputs,
        "task_status": task_node.get("status"),
        "task_agent": task_node.get("agent"),
    }


# ===========================================================================
# Passo 5: Decisão de Lead action
# ===========================================================================

def _should_lead_act(
    graph: Any,
    frontier: list[str],
    busy_workers: list[str],
    idle_workers: list[str],
) -> bool:
    """
    Decide se o Lead deve agir neste round.

    O Lead age quando:
      - É o primeiro round (round 1) — planejamento inicial.
      - Há mais tasks no frontier que Workers idle disponíveis
        (Lead precisa Assign ou fazer Discover de novas tasks).
      - Há Workers busy que precisam de supervisão.
      - Não há tasks no frontier mas ainda há Workers busy
        (Lead precisa monitorar ou fazer Discover).

    Nota: A detecção de stragglers (heartbeat) é feita pelo Orchestrator
    e também força lead_action=True. Esta função cobre os casos
    estruturais do grafo.

    Args:
        graph: CoordinationGraph.
        frontier: Lista de node IDs no frontier.
        busy_workers: Lista de Worker IDs ocupados.
        idle_workers: Lista de Worker IDs ociosos.

    Returns:
        True se o Lead deve ser invocado neste round.
    """
    current_round = graph.round

    # Round 1: Lead sempre age (planejamento inicial)
    if current_round == 1:
        return True

    # Caso 1: frontier maior que Workers idle disponíveis
    # → Lead deve priorizar, Assign, ou descobrir novas tasks
    if len(frontier) > len(idle_workers):
        return True

    # Caso 2: Sem tasks no frontier mas Workers ainda busy
    # → Lead deve monitorar progresso
    if len(frontier) == 0 and len(busy_workers) > 0:
        return True

    # Caso 3: Há Workers busy → Lead pode precisar intervir
    # (Release, Close, Verify — detectado pelo heartbeat no orchestrator)
    if len(busy_workers) > 0:
        return True

    # Caso 4: Grafo tem nós pending mas frontier vazio
    # → possíveis dependências não satisfeitas; Lead deve verificar
    pending_nodes = sum(
        1 for node in graph.nodes
        if node.get("status") == "pending"
    )
    if pending_nodes > 0 and len(frontier) == 0:
        return True

    # Caso default: sem ação necessária do Lead
    return False


# ===========================================================================
# Funções auxiliares para integração com delegate_task (ADR-003)
# ===========================================================================

def build_worker_prompt(
    assignment: dict[str, Any],
    worker_id: str,
) -> str:
    """
    Constrói o prompt que será enviado ao Worker via delegate_task.

    ADR-003: Workers são spawnados via delegate_task do Hermes.
    ADR-004: O prompt contém APENAS task description + outputs de
             dependências diretas — NÃO contém spec.md ou plan.md.

    Args:
        assignment: Dict com a estrutura de um assignment do dispatch_plan:
                   {"worker": str, "task": str, "action": str, "context": {...}}
        worker_id: ID do Worker (para confirmar identidade).

    Returns:
        String com o prompt formatado para o Worker.

    Example:
        >>> prompt = build_worker_prompt(assignment, "Dev1")
        >>> # prompt contém apenas a task description + outputs de deps
    """
    context = assignment.get("context", {})
    task_description = context.get("task_description", "No description")
    dep_outputs = context.get("dependency_outputs", {})
    task_id = assignment.get("task", "unknown")
    action = assignment.get("action", "assign")

    lines: list[str] = []

    # Cabeçalho
    if action == "re_engage":
        lines.append(f"## Re-engajamento: Task {task_id}")
        lines.append("")
        lines.append(
            "Você já está trabalhando nesta task. As seguintes dependências "
            "foram concluídas desde o último round:"
        )
    else:
        lines.append(f"## Task: {task_id}")
        lines.append("")
        lines.append("Você foi designado para executar esta task.")

    lines.append("")
    lines.append(f"### Descrição da Task")
    lines.append(f"```")
    lines.append(task_description)
    lines.append(f"```")

    # Outputs das dependências concluídas
    if dep_outputs:
        lines.append("")
        lines.append("### Outputs das Dependências Concluídas")
        lines.append("")
        for dep_id, output in dep_outputs.items():
            lines.append(f"#### {dep_id}")
            if output:
                lines.append(f"```")
                # Trunca outputs muito longos para evitar estouro de contexto
                # (mantém no máximo 4000 caracteres por output)
                truncated = output[:4000]
                if len(output) > 4000:
                    truncated += "\n... [output truncado — consulte o arquivo fonte]"
                lines.append(truncated)
                lines.append(f"```")
            else:
                lines.append("(output não registrado)")

    else:
        lines.append("")
        lines.append("### Dependências")
        lines.append("")
        lines.append("Esta task não possui dependências diretas concluídas.")

    # Instruções de protocolo
    lines.append("")
    lines.append("### Ações Disponíveis")
    lines.append("")
    lines.append(
        "Como Worker LATTE, você pode emitir as seguintes ações usando "
        "tags XML:"
    )
    lines.append("")
    lines.append("- `<claim_task id=\"...\"/>` — Reivindicar esta task do frontier")
    lines.append("- `<complete_task id=\"...\"/>` — Sinalizar conclusão da task")
    lines.append(
        "- `<discover_task id=\"...\" title=\"...\" dependencies=\"...\">` — "
        "Propor nova task"
    )
    lines.append("")
    lines.append(
        "**Atenção:** Você só pode Claim/Complete tasks atribuídas a você. "
        "Tasks concluídas devem ter seus testes passando (`<run_tests />`)."
    )

    return "\n".join(lines)


def extract_worker_actions(
    worker_response: str,
    worker_id: str,
) -> list[dict[str, Any]]:
    """
    Extrai ações emitidas por um Worker a partir de sua resposta.

    Parseia tags XML do protocolo LATTE (Seção 3.2 do latte-protocol.md):
      - <claim_task id="..."/>
      - <complete_task id="..."/>
      - <discover_task id="..." title="..." dependencies="...">...</discover_task>

    Args:
        worker_response: Texto completo da resposta do Worker.
        worker_id: ID do Worker que emitiu a resposta.

    Returns:
        Lista de ações parseadas, cada uma como dict:
            {"type": "claim_task", "id": "T001"}
            {"type": "complete_task", "id": "T001"}
            {"type": "discover_task", "id": "T003", "title": "...",
             "dependencies": ["T001"], "description": "..."}
    """
    import re

    actions: list[dict[str, Any]] = []

    # --- Parse <claim_task id="..."/> ---
    for match in re.finditer(
        r'<claim_task\s+id="([^"]+)"\s*/>',
        worker_response,
        re.IGNORECASE,
    ):
        actions.append({
            "type": "claim_task",
            "id": match.group(1),
        })

    # --- Parse <complete_task id="..."/> ---
    for match in re.finditer(
        r'<complete_task\s+id="([^"]+)"\s*/>',
        worker_response,
        re.IGNORECASE,
    ):
        actions.append({
            "type": "complete_task",
            "id": match.group(1),
        })

    # --- Parse <discover_task id="..." title="..." dependencies="...">...</discover_task> ---
    for match in re.finditer(
        r'<discover_task\s+id="([^"]+)"\s+title="([^"]*)"(?:\s+dependencies="([^"]*)")?\s*>(.*?)</discover_task>',
        worker_response,
        re.DOTALL | re.IGNORECASE,
    ):
        deps_str = match.group(3) or ""
        deps = [d.strip() for d in deps_str.split() if d.strip()] if deps_str else []
        actions.append({
            "type": "discover_task",
            "id": match.group(1),
            "title": match.group(2),
            "dependencies": deps,
            "description": match.group(4).strip(),
        })

    if logger.isEnabledFor(logging.DEBUG) and actions:
        logger.debug(
            "  Worker %s emitiu %d ação(ões): %s",
            worker_id,
            len(actions),
            [a["type"] for a in actions],
        )

    return actions


# ===========================================================================
# Testes rápidos (executáveis com python -m pytest ou diretamente)
# ===========================================================================

if __name__ == "__main__":
    """
    Teste manual do módulo dispatcher.py.

    Simula um CoordinationGraph mínimo e exercita:
      - Classificação busy/idle
      - Re-engajamento de Workers busy
      - Atribuição de Workers idle
      - Context scoping (ADR-004)
      - build_worker_prompt
      - extract_worker_actions
    """
    import sys
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import Optional as Opt

    sys.path.insert(0, str(Path(__file__).resolve().parent))

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ------------------------------------------------------------------
    # Mock mínimo de CoordinationGraph para teste standalone
    # ------------------------------------------------------------------

    @dataclass
    class MockGraph:
        """Simula a interface mínima de CoordinationGraph."""
        workers: list[str] = field(default_factory=lambda: ["Dev1", "Dev2", "Dev3"])
        round: int = 2
        lead: str = "Lead"
        nodes: list[dict] = field(default_factory=list)
        history: list[dict] = field(default_factory=list)

        def get_node(self, node_id: str) -> Opt[dict]:
            for node in self.nodes:
                if node["id"] == node_id:
                    return node
            return None

        def find_node(self, node_id: str) -> dict:
            node = self.get_node(node_id)
            if node is None:
                raise KeyError(f"Node '{node_id}' not found")
            return node

    print("=" * 60)
    print("dispatcher.py — Testes de unidade (T007)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Teste 1: Classificação busy vs idle
    # ------------------------------------------------------------------
    print("\n[Teste 1] Classificação busy vs idle")
    graph = MockGraph(
        workers=["Dev1", "Dev2", "Dev3"],
        nodes=[
            {"id": "T001", "agent": "Dev1", "status": "in_progress",
             "deps": [], "description": "Task 1: Setup",
             "output": None},
            {"id": "T002", "agent": "Dev2", "status": "assigned",
             "deps": ["T001"], "description": "Task 2: Feature",
             "output": None},
            {"id": "T003", "agent": None, "status": "pending",
             "deps": ["T001"], "description": "Task 3: Tests",
             "output": None},
        ],
    )
    busy, idle = _classify_workers(graph, graph.workers)
    assert set(busy) == {"Dev1", "Dev2"}, f"Esperado Dev1+Dev2 busy, obtido {busy}"
    assert idle == ["Dev3"], f"Esperado Dev3 idle, obtido {idle}"
    print(f"  ✓ PASS: busy={busy}, idle={idle}")

    # ------------------------------------------------------------------
    # Teste 2: Re-engajamento de Workers busy
    # ------------------------------------------------------------------
    print("\n[Teste 2] Re-engajamento de Workers busy")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        nodes=[
            {"id": "T001", "agent": None, "status": "done",
             "deps": [], "description": "Task 1: Setup",
             "output": "Setup completo: venv criado, deps instaladas."},
            {"id": "T002", "agent": "Dev1", "status": "in_progress",
             "deps": ["T001"], "description": "Task 2: Feature X",
             "output": None},
            {"id": "T003", "agent": "Dev2", "status": "in_progress",
             "deps": [], "description": "Task 3: Feature Y (sem deps)",
             "output": None},
        ],
    )
    busy, idle = _classify_workers(graph, graph.workers)
    completed = _build_completed_outputs_map(graph)
    re_engage = _re_engage_busy_workers(graph, busy, completed)
    assert len(re_engage) == 2, f"Esperado 2 re-engagements, obtido {len(re_engage)}"
    # Dev1 deve receber output de T001
    dev1_assignment = next(a for a in re_engage if a["worker"] == "Dev1")
    assert "T001" in dev1_assignment["context"]["dependency_outputs"]
    assert dev1_assignment["context"]["dependency_outputs"]["T001"] == \
        "Setup completo: venv criado, deps instaladas."
    # Dev2 não tem dependências → dependency_outputs vazio
    dev2_assignment = next(a for a in re_engage if a["worker"] == "Dev2")
    assert dev2_assignment["context"]["dependency_outputs"] == {}
    print(f"  ✓ PASS: {len(re_engage)} re-engagements")
    print(f"    Dev1 context: {dev1_assignment['context']}")
    print(f"    Dev2 context: {dev2_assignment['context']}")

    # ------------------------------------------------------------------
    # Teste 3: Atribuição de Workers idle ao frontier
    # ------------------------------------------------------------------
    print("\n[Teste 3] Atribuição de Workers idle ao frontier")
    graph = MockGraph(
        workers=["Dev1", "Dev2", "Dev3"],
        nodes=[
            {"id": "T001", "agent": None, "status": "done",
             "deps": [], "description": "Task 1: Setup",
             "output": "Setup complete."},
            {"id": "T002", "agent": None, "status": "pending",
             "deps": ["T001"], "description": "Task 2: Feature",
             "output": None},
            {"id": "T003", "agent": None, "status": "pending",
             "deps": [], "description": "Task 3: Docs",
             "output": None},
        ],
    )
    frontier = ["T003", "T002"]  # T003 primeiro (menos deps)
    idle_workers = ["Dev1", "Dev2"]  # Dois ociosos
    completed = _build_completed_outputs_map(graph)
    assignments = _assign_idle_workers(graph, frontier, idle_workers, completed)
    assert len(assignments) == 2, f"Esperado 2 assignments, obtido {len(assignments)}"
    # Dev1 deve pegar T003 (primeira do frontier)
    assert assignments[0]["worker"] == "Dev1"
    assert assignments[0]["task"] == "T003"
    # Dev2 deve pegar T002
    assert assignments[1]["worker"] == "Dev2"
    assert assignments[1]["task"] == "T002"
    # T002 deve ter output de T001 no contexto
    assert "T001" in assignments[1]["context"]["dependency_outputs"]
    print(f"  ✓ PASS: {len(assignments)} assignments")
    for a in assignments:
        print(f"    {a['worker']} ← {a['task']}: deps={list(a['context']['dependency_outputs'].keys())}")

    # ------------------------------------------------------------------
    # Teste 4: dispatch() completo
    # ------------------------------------------------------------------
    print("\n[Teste 4] dispatch() completo")
    graph = MockGraph(
        workers=["Dev1", "Dev2", "Dev3"],
        round=3,
        nodes=[
            {"id": "T001", "agent": "Dev1", "status": "done",
             "deps": [], "description": "Setup",
             "output": "Setup output"},
            {"id": "T002", "agent": "Dev2", "status": "in_progress",
             "deps": ["T001"], "description": "Feature X",
             "output": None},
            {"id": "T003", "agent": None, "status": "pending",
             "deps": ["T001"], "description": "Feature Y",
             "output": None},
            {"id": "T004", "agent": None, "status": "pending",
             "deps": [], "description": "Docs",
             "output": None},
        ],
    )
    frontier = ["T004", "T003"]
    plan = dispatch(graph, frontier)
    assert plan["lead_action"] is True, "Lead deve agir (há Workers busy)"
    assert plan["metadata"]["busy_count"] == 1
    assert plan["metadata"]["idle_count"] == 2
    # Deve ter 1 re-engage (Dev2) + até 2 assigns (Dev3, Dev1 se idle)
    assert len(plan["assignments"]) >= 1
    re_engages = [a for a in plan["assignments"] if a["action"] == "re_engage"]
    assigns = [a for a in plan["assignments"] if a["action"] == "assign"]
    assert len(re_engages) == 1  # Dev2 com T002
    assert len(assigns) >= 1  # Pelo menos Dev3 recebe task
    print(f"  ✓ PASS: lead_action={plan['lead_action']}")
    print(f"    re_engages={len(re_engages)}, assigns={len(assigns)}")
    print(f"    metadata={plan['metadata']}")

    # ------------------------------------------------------------------
    # Teste 5: Context scoping — build_context_for_task
    # ------------------------------------------------------------------
    print("\n[Teste 5] build_context_for_task (API pública)")
    graph = MockGraph(
        workers=["Dev1"],
        nodes=[
            {"id": "T001", "agent": None, "status": "done",
             "deps": [], "description": "Setup",
             "output": "Setup output"},
            {"id": "T002", "agent": None, "status": "done",
             "deps": [], "description": "Config",
             "output": "Config gerado"},
            {"id": "T003", "agent": None, "status": "pending",
             "deps": ["T001", "T002"], "description": "Feature Z",
             "output": None},
        ],
    )
    ctx = build_context_for_task(graph, "T003")
    assert ctx["task_description"] == "Feature Z"
    assert ctx["task_status"] == "pending"
    assert "T001" in ctx["dependency_outputs"]
    assert "T002" in ctx["dependency_outputs"]
    assert ctx["dependency_outputs"]["T001"] == "Setup output"
    assert ctx["dependency_outputs"]["T002"] == "Config gerado"
    print(f"  ✓ PASS: context={ctx}")

    # ------------------------------------------------------------------
    # Teste 6: build_worker_prompt (ADR-003 + ADR-004)
    # ------------------------------------------------------------------
    print("\n[Teste 6] build_worker_prompt")
    assignment = {
        "worker": "Dev1",
        "task": "T003",
        "action": "assign",
        "context": {
            "task_description": "Implementar feature Z com validação de input",
            "dependency_outputs": {
                "T001": "Setup output: venv criado, deps OK",
                "T002": "Config: database_url=postgresql://...",
            },
        },
    }
    prompt = build_worker_prompt(assignment, "Dev1")
    assert "feature Z" in prompt
    assert "T001" in prompt
    assert "T002" in prompt
    assert "venv criado" in prompt
    assert "database_url" in prompt
    # NÃO deve conter spec.md ou plan.md
    assert "spec.md" not in prompt.lower()
    assert "plan.md" not in prompt.lower()
    print(f"  ✓ PASS: prompt gerado ({len(prompt)} chars)")
    print(f"    (primeiras linhas):")
    for line in prompt.split("\n")[:5]:
        print(f"    {line}")

    # ------------------------------------------------------------------
    # Teste 7: extract_worker_actions
    # ------------------------------------------------------------------
    print("\n[Teste 7] extract_worker_actions")
    worker_response = """
    Analisei a task e farei o seguinte:

    <claim_task id="T003"/>

    Vou implementar feature Z...

    <complete_task id="T003"/>

    Também descobri que precisamos:

    <discover_task id="T004" title="Fix edge case" dependencies="T003">
    Edge case X não foi tratado. Precisamos adicionar validação.
    </discover_task>
    """
    actions = extract_worker_actions(worker_response, "Dev1")
    assert len(actions) == 3, f"Esperado 3 ações, obtido {len(actions)}"
    assert actions[0]["type"] == "claim_task"
    assert actions[0]["id"] == "T003"
    assert actions[1]["type"] == "complete_task"
    assert actions[1]["id"] == "T003"
    assert actions[2]["type"] == "discover_task"
    assert actions[2]["id"] == "T004"
    assert actions[2]["title"] == "Fix edge case"
    assert actions[2]["dependencies"] == ["T003"]
    print(f"  ✓ PASS: {len(actions)} ações extraídas")
    for a in actions:
        print(f"    {a['type']}: {a.get('id', '?')}")

    # ------------------------------------------------------------------
    # Teste 8: dispatch com frontier vazio
    # ------------------------------------------------------------------
    print("\n[Teste 8] dispatch com frontier vazio")
    graph = MockGraph(
        workers=["Dev1", "Dev2"],
        round=5,
        nodes=[
            {"id": "T001", "agent": "Dev1", "status": "in_progress",
             "deps": [], "description": "Task 1",
             "output": None},
        ],
    )
    plan = dispatch(graph, frontier=[])
    assert plan["lead_action"] is True  # Há Workers busy, Lead deve monitorar
    assert len(plan["assignments"]) == 1  # Re-engage de Dev1
    assert plan["assignments"][0]["action"] == "re_engage"
    assert plan["metadata"]["idle_count"] == 1  # Dev2 idle
    print(f"  ✓ PASS: lead_action={plan['lead_action']}, "
          f"assignments={plan['metadata']}")

    # ------------------------------------------------------------------
    # Teste 9: dispatch com idle_workers/busy_workers fornecidos
    # ------------------------------------------------------------------
    print("\n[Teste 9] dispatch com busy_workers/idle_workers fornecidos")
    graph = MockGraph(
        workers=["Dev1", "Dev2", "Dev3"],
        round=2,
        nodes=[
            {"id": "T001", "agent": None, "status": "pending",
             "deps": [], "description": "Task 1", "output": None},
            {"id": "T002", "agent": None, "status": "pending",
             "deps": [], "description": "Task 2", "output": None},
        ],
    )
    # Força classificação manual
    plan = dispatch(
        graph,
        frontier=["T001", "T002"],
        busy_workers=["Dev1"],
        idle_workers=["Dev2", "Dev3"],
    )
    assert plan["metadata"]["busy_count"] == 1
    assert plan["metadata"]["idle_count"] == 2
    re_engages = [a for a in plan["assignments"] if a["action"] == "re_engage"]
    assigns = [a for a in plan["assignments"] if a["action"] == "assign"]
    assert len(re_engages) == 0  # Dev1 está busy mas não tem task ativa no grafo
    assert len(assigns) == 2  # Dev2 + Dev3 recebem T001 + T002
    print(f"  ✓ PASS: re_engages={len(re_engages)}, assigns={len(assigns)}")

    print("\n" + "=" * 60)
    print("Todos os testes passaram ✓")
    print("=" * 60)
