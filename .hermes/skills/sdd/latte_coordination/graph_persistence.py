#!/usr/bin/env python3
"""
graph_persistence.py — Persistência do Coordination Graph no Wiki (T011)
========================================================================

Implementa a função `save_graph_to_wiki()` que serializa G_final como um
arquivo `coordination-graph.md` no diretório wiki do projeto, contendo:

  (1) Tabela markdown com todas as tasks (id, agent, status final,
      dependências, rounds ativos).
  (2) Grafo ASCII com `|->` representando dependências e status final.
  (3) Seção de métricas: rounds totais, operadores usados, nodes
      created/completed/released/closed/verified.
  (4) Salvamento em `wiki/projects/<feature_id>/coordination-graph.md`.

O diretório de destino é criado automaticamente se não existir.

Referências:
  - graph-schema.md: schema canônico do G_t (Seção 5)
  - latte-protocol.md: operadores e invariantes
  - orchestrator.py: CoordinationGraph wrapper
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Optional, Union

try:
    from .orchestrator import CoordinationGraph  # noqa: F401 — type hint
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

STATUS_ICONS: dict[str, str] = {
    "pending":     "⏳",
    "assigned":    "📋",
    "in_progress": "🔄",
    "done":        "✅",
    "verified":    "🔒",
}

# Operadores distinguidos para métricas (da máquina de estados, Seção 2.2)
MONITORED_OPERATORS: frozenset[str] = frozenset({
    "Assign", "Claim", "Complete", "Release", "Close", "Verify", "Discover",
})


# ---------------------------------------------------------------------------
# Helpers de extração
# ---------------------------------------------------------------------------

def _ensure_dict(graph: Any) -> dict[str, Any]:
    """
    Converte o grafo para dict puro, sem modificar o original.

    Suporta:
      - dict nativo
      - CoordinationGraph (expõe .raw)
      - Qualquer objeto com atributo .raw ou dict-like
    """
    if isinstance(graph, dict):
        return graph
    if hasattr(graph, "raw"):
        return graph.raw
    # Fallback: tenta iterar como dict
    return dict(graph)


def _parse_graph(graph: Any) -> dict[str, Any]:
    """Normaliza a entrada e retorna o dict do grafo + metadados extraídos."""
    g = _ensure_dict(graph)
    metadata = g.get("metadata", {})
    nodes = g.get("nodes", [])
    edges = g.get("edges", [])
    history = g.get("history", [])
    return {
        "metadata": metadata,
        "nodes": nodes,
        "edges": edges,
        "history": history,
    }


# ---------------------------------------------------------------------------
# (1) Tabela markdown de tasks
# ---------------------------------------------------------------------------

def _build_task_table(nodes: list[dict], metadata: dict) -> str:
    """
    Gera uma tabela markdown com todas as tasks do grafo.

    Colunas:
      - Task ID
      - Agent
      - Status Final
      - Dependências
      - Rounds Ativos
    """
    current_round = metadata.get("round", 0)

    lines: list[str] = []
    lines.append("## 📋 Tabela de Tasks")
    lines.append("")
    lines.append(
        "| Task ID | Agent | Status Final | Dependências | Rounds Ativos |"
    )
    lines.append(
        "|---------|-------|--------------|--------------|---------------|"
    )

    for node in nodes:
        nid = node.get("id", "?")
        agent = node.get("agent") or "—"
        status = node.get("status", "?")
        icon = STATUS_ICONS.get(status, "")
        deps = ", ".join(node.get("deps", [])) or "—"

        created_at = node.get("created_at_round", 0)
        completed_at = node.get("completed_at_round")
        if completed_at is not None:
            active_rounds = completed_at - created_at + 1
        else:
            active_rounds = current_round - created_at + 1

        lines.append(
            f"| `{nid}` | {agent} | {icon} {status} | {deps} | {active_rounds} |"
        )

    if not nodes:
        lines.append("| *(grafo vazio)* | — | — | — | — |")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# (2) Grafo ASCII com dependências
# ---------------------------------------------------------------------------

def _build_ascii_graph(nodes: list[dict]) -> str:
    """
    Gera uma representação ASCII do coordination graph usando `|->`
    para representar dependências e anotando o status final de cada nó.

    Estrutura:
        [T001 ✅ done]
          |-> [T003 ✅ done]
          |-> [T004 🔄 in_progress]
        [T002 ✅ done]
          |-> [T004 🔄 in_progress]

    Nós sem dependências são exibidos como raízes (sem indentação).
    Nós com dependências são exibidos sob seus pais com indentação.
    """
    if not nodes:
        return "## 🌐 Grafo de Coordenação\n\n*(grafo vazio)*\n"

    # Build lookup: node_id → node
    node_map: dict[str, dict] = {n["id"]: n for n in nodes}

    # Build reverse lookup: parent_id → list of child_ids
    children_map: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    for n in nodes:
        for dep in n.get("deps", []):
            if dep in children_map:
                children_map[dep].append(n["id"])

    # Find roots (nodes with empty deps)
    roots = [n["id"] for n in nodes if not n.get("deps")]

    # If no roots (shouldn't happen in a DAG, but handle gracefully),
    # use all nodes as roots
    if not roots:
        roots = [n["id"] for n in nodes]

    # Track visited to handle the DAG correctly (each node appears once)
    visited: set[str] = set()
    lines: list[str] = []
    lines.append("## 🌐 Grafo de Coordenação")
    lines.append("")

    # Topological-sort-like traversal from roots
    def render_node(nid: str, indent: int = 0, prefix: str = "") -> None:
        if nid in visited:
            return
        visited.add(nid)

        node = node_map.get(nid)
        if node is None:
            return

        status = node.get("status", "?")
        icon = STATUS_ICONS.get(status, "")
        deps_str = f" (deps: {', '.join(node['deps'])})" if node.get("deps") else ""

        if indent == 0:
            lines.append(f"{prefix}[{nid} {icon} {status}]{deps_str}")
        else:
            lines.append(f"{prefix}[{nid} {icon} {status}]{deps_str}")

        children = children_map.get(nid, [])
        for i, child in enumerate(children):
            if indent == 0:
                child_prefix = "  |-> "
            else:
                child_prefix = prefix + "  |-> "
            render_node(child, indent + 1, child_prefix)

    for root in roots:
        render_node(root, 0, "")

    # Handle any nodes not reachable from roots (disconnected)
    for n in nodes:
        if n["id"] not in visited:
            render_node(n["id"], 0, "")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# (3) Seção de métricas
# ---------------------------------------------------------------------------

def _build_metrics(metadata: dict, nodes: list[dict], history: list[dict]) -> str:
    """
    Gera a seção de métricas da execução:
      - Rounds totais
      - Operadores usados (contagem por tipo)
      - Nodes created/completed/released/closed/verified
    """
    current_round = metadata.get("round", 0)
    max_rounds = metadata.get("max_rounds", "?")
    total_nodes = len(nodes)

    # Contagem de status finais
    status_counts = Counter(n.get("status", "?") for n in nodes)

    # Contagem de operadores a partir do histórico
    operator_counts: Counter[str] = Counter()
    for entry in history:
        op = entry.get("operator", "?")
        operator_counts[op] += 1

    # Métricas derivadas do histórico:
    #   created  = Discover
    #   completed = Complete
    #   released  = Release
    #   closed    = Close
    #   verified  = Verify
    #   assigned  = Assign
    #   claimed   = Claim
    created_count = operator_counts.get("Discover", 0)
    completed_count = operator_counts.get("Complete", 0)
    released_count = operator_counts.get("Release", 0)
    closed_count = operator_counts.get("Close", 0)
    verified_count = operator_counts.get("Verify", 0)
    assigned_count = operator_counts.get("Assign", 0)
    claimed_count = operator_counts.get("Claim", 0)

    lines: list[str] = []
    lines.append("## 📊 Métricas da Execução")
    lines.append("")

    # Rounds
    lines.append("### Rounds")
    lines.append("")
    lines.append(f"| Métrica | Valor |")
    lines.append(f"|---------|-------|")
    lines.append(f"| Rounds executados | {current_round} |")
    lines.append(f"| Rounds máximos configurados | {max_rounds} |")
    lines.append(f"| Total de nós no grafo final | {total_nodes} |")
    lines.append("")

    # Operadores
    lines.append("### Operadores Utilizados")
    lines.append("")
    lines.append(
        "| Operador | Contagem | Descrição |"
    )
    lines.append(
        "|----------|----------|-----------|"
    )
    lines.append(
        f"| Discover | {created_count} | Criar nova task no grafo |"
    )
    lines.append(
        f"| Assign   | {assigned_count} | Atribuir task a Worker |"
    )
    lines.append(
        f"| Claim    | {claimed_count} | Worker reivindica task do frontier |"
    )
    lines.append(
        f"| Complete | {completed_count} | Worker conclui task com sucesso |"
    )
    lines.append(
        f"| Release  | {released_count} | Devolver task ao pool (straggler) |"
    )
    lines.append(
        f"| Close    | {closed_count} | Lead força done em task concluída |"
    )
    lines.append(
        f"| Verify   | {verified_count} | Spawnar verificação de qualidade |"
    )
    lines.append("")

    # Status finais
    lines.append("### Distribuição de Status Final")
    lines.append("")
    lines.append(
        "| Status | Contagem | Ícone |"
    )
    lines.append(
        "|--------|----------|-------|"
    )
    for status in ["pending", "assigned", "in_progress", "done", "verified"]:
        count = status_counts.get(status, 0)
        icon = STATUS_ICONS.get(status, "")
        lines.append(f"| {status} | {count} | {icon} |")
    lines.append("")

    # Resumo de ações
    total_actions = sum(operator_counts.values())
    lines.append(f"**Total de ações registradas no histórico:** {total_actions}")
    lines.append("")

    # Progressão
    terminal_count = status_counts.get("done", 0) + status_counts.get("verified", 0)
    if total_nodes > 0:
        completion_pct = (terminal_count / total_nodes) * 100
        lines.append(f"**Taxa de conclusão:** {terminal_count}/{total_nodes} ({completion_pct:.1f}%)")
    else:
        lines.append("**Taxa de conclusão:** N/A (grafo vazio)")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# (4) Salvamento em arquivo
# ---------------------------------------------------------------------------

def _build_full_markdown(graph_data: dict[str, Any]) -> str:
    """
    Constrói o conteúdo completo do coordination-graph.md.

    Args:
        graph_data: Dicionário com as chaves 'metadata', 'nodes', 'edges', 'history'.

    Returns:
        String markdown completa.
    """
    metadata = graph_data["metadata"]
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]
    history = graph_data["history"]

    feature_id = metadata.get("feature_id", "?")
    created_at = metadata.get("created_at", "?")

    parts: list[str] = []

    # Cabeçalho
    parts.append(f"# Coordination Graph — Feature `{feature_id}`")
    parts.append("")
    parts.append(f"> **Gerado em:** {created_at}")
    parts.append(f"> **Feature ID:** `{feature_id}`")
    parts.append(f"> **Lead:** `{metadata.get('lead', '?')}`")
    parts.append(
        f"> **Workers:** {', '.join(f'`{w}`' for w in metadata.get('workers', []))}"
    )
    parts.append(f"> **Total de nós:** {len(nodes)} | **Total de arestas:** {len(edges)}")
    parts.append("")
    parts.append("---")
    parts.append("")

    # (1) Tabela de tasks
    parts.append(_build_task_table(nodes, metadata))

    # (2) Grafo ASCII
    parts.append(_build_ascii_graph(nodes))

    # (3) Métricas
    parts.append(_build_metrics(metadata, nodes, history))

    # Legenda
    parts.append("---")
    parts.append("")
    parts.append("## 📖 Legenda de Status")
    parts.append("")
    for status, icon in STATUS_ICONS.items():
        parts.append(f"- {icon} **{status}** — ", end="")
        if status == "pending":
            parts.append("Task criada, aguardando atribuição ou claim")
        elif status == "assigned":
            parts.append("Task atribuída a um Worker, execução ainda não iniciada")
        elif status == "in_progress":
            parts.append("Worker está ativamente executando a task")
        elif status == "done":
            parts.append("Worker concluiu a task com sucesso")
        elif status == "verified":
            parts.append("Task passou por verificação adicional de qualidade")
        parts[-1] += "\n"  # close the append

    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(
        "*Gerado automaticamente pelo módulo `graph_persistence.py` "
        "do LATTE Coordination Engine.*"
    )
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Função pública principal
# ---------------------------------------------------------------------------

def save_graph_to_wiki(
    graph: Any,
    feature_id: str,
    wiki_root: str = "wiki/",
) -> Path:
    """
    Salva G_final como `coordination-graph.md` no diretório wiki do projeto.

    Gera um arquivo markdown contendo:
      1. Tabela com todas as tasks (id, agent, status final, dependências,
         rounds ativos).
      2. Grafo ASCII com `|->` representando dependências entre tasks e
         anotando o status final de cada nó.
      3. Seção de métricas: rounds totais, operadores usados (contagem
         por tipo), nodes created/completed/released/closed/verified.
      4. Legenda de status.

    O diretório `wiki/projects/<feature_id>/` é criado automaticamente se
    não existir.

    Args:
        graph: O coordination graph G_final. Aceita dict nativo ou objeto
               CoordinationGraph (do orchestrator.py).
        feature_id: ID da feature (ex: "001", "002-latte_coordination").
        wiki_root: Diretório raiz do wiki (default: "wiki/").
                   O caminho final será: <wiki_root>/projects/<feature_id>/coordination-graph.md

    Returns:
        Path absoluto do arquivo salvo.

    Raises:
        OSError: Se não for possível criar o diretório ou escrever o arquivo.
        ValueError: Se o grafo não contiver a estrutura esperada.

    Example:
        >>> from orchestrator import Orchestrator, CoordinationGraph
        >>> orch = Orchestrator(task_description="...", G_0=G_0)
        >>> G_final = orch.run()
        >>> save_graph_to_wiki(G_final, "001")
        PosixPath('/home/user/projeto/wiki/projects/001/coordination-graph.md')
    """
    # Normaliza o grafo
    graph_data = _parse_graph(graph)

    # Validações básicas
    if "nodes" not in graph_data:
        raise ValueError(
            "O grafo fornecido não contém a chave 'nodes'. "
            "Verifique se é um CoordinationGraph ou dict válido "
            "conforme graph-schema.md, Seção 5."
        )

    # Constrói caminho de destino
    wiki_path = Path(wiki_root)
    target_dir = wiki_path / "projects" / feature_id
    target_file = target_dir / "coordination-graph.md"

    # Cria diretório se não existir
    target_dir.mkdir(parents=True, exist_ok=True)

    # Gera conteúdo markdown
    content = _build_full_markdown(graph_data)

    # Escreve o arquivo
    target_file.write_text(content, encoding="utf-8")

    return target_file.resolve()


# ---------------------------------------------------------------------------
# CLI minimal para testes
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    # Exemplo de uso: carrega G_final de um JSON e salva no wiki
    if len(sys.argv) < 3:
        print(f"Uso: {sys.argv[0]} <graph.json> <feature_id> [wiki_root]")
        print("  graph.json : arquivo JSON com o coordination graph")
        print("  feature_id : ID da feature (ex: '001')")
        print("  wiki_root  : diretório raiz do wiki (default: 'wiki/')")
        sys.exit(1)

    graph_file = Path(sys.argv[1])
    fid = sys.argv[2]
    root = sys.argv[3] if len(sys.argv) > 3 else "wiki/"

    if not graph_file.exists():
        print(f"ERRO: Arquivo não encontrado: {graph_file}")
        sys.exit(1)

    with open(graph_file, encoding="utf-8") as f:
        graph_dict = json.load(f)

    output_path = save_graph_to_wiki(graph_dict, fid, wiki_root=root)
    print(f"✅ coordination-graph.md salvo em: {output_path}")
