"""
T014 — distill.py: Geracao de chunks canonicos via LLM a partir de clusters.

Para cada cluster de chunks similares:
1. Concatena os conteudos dos chunks (limitado a 3000 chars)
2. Gera um chunk canonico via LLM com o prompt:
   'Sintetize esses fragmentos similares em um unico padrao canonico conciso:'
3. Se nao houver LLM disponivel, usa o chunk de maior score do cluster
   como representante.
4. Score agregado = media dos scores do cluster.
5. O chunk canonico tem source='_distilled/', heading='Canonical Pattern N'.

API publica:
    distill_clusters(clusters) -> list[dict]
"""

import os

# ── Tentativa de importar APIs de LLM ──────────────────────────────────────

_LLM_BACKEND = None  # 'openai', 'anthropic' ou None (fallback)

try:
    import openai

    if os.environ.get("OPENAI_API_KEY"):
        _LLM_BACKEND = "openai"
except ImportError:
    pass

if not _LLM_BACKEND:
    try:
        import anthropic

        if os.environ.get("ANTHROPIC_API_KEY"):
            _LLM_BACKEND = "anthropic"
    except ImportError:
        pass


# ── Helpers de chamada ao LLM ──────────────────────────────────────────────


def _call_llm(prompt: str) -> str | None:
    """Chama o LLM via API disponivel e retorna a resposta, ou None se falhar.

    Suporta OpenAI e Anthropic. O modelo usado pode ser sobrescrito via
    variavel de ambiente LLM_MODEL.
    """
    if _LLM_BACKEND == "openai":
        try:
            model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as exc:
            print(f"[distill] ⚠️  Erro ao chamar OpenAI: {exc}")
            return None

    elif _LLM_BACKEND == "anthropic":
        try:
            model = os.environ.get("LLM_MODEL", "claude-3-haiku-20240307")
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as exc:
            print(f"[distill] ⚠️  Erro ao chamar Anthropic: {exc}")
            return None

    return None


def _print_prompt_for_review(prompt: str, cluster_index: int) -> None:
    """Imprime o prompt para revisao manual (modo sem LLM ou fallback)."""
    print(f"\n{'─' * 60}")
    print(f"📋  Prompt para revisao — Cluster {cluster_index + 1}")
    print(f"{'─' * 60}")
    print(prompt)
    print(f"{'─' * 60}\n")


# ── API publica ─────────────────────────────────────────────────────────────


def distill_clusters(clusters: list[list[dict]]) -> list[dict]:
    """Gera chunks canonicos a partir de clusters de chunks similares.

    Para cada cluster:
    1. Concatena os conteudos dos chunks (limitado a 3000 chars).
    2. Gera um chunk canonico via LLM com o prompt:
       'Sintetize esses fragmentos similares em um unico padrao canonico conciso:'
    3. Se nao houver LLM disponivel, imprime o prompt para revisao e usa
       o chunk de maior score do cluster como representante.
    4. Score agregado = media dos scores do cluster.
    5. O chunk canonico tem source='_distilled/', heading='Canonical Pattern N'.

    Args:
        clusters: Lista de clusters, cada um sendo uma lista de dicionarios
                  com campos: id, source, heading, content, score, etc.
                  (formato retornado por cluster.py: cluster_chunks()).

    Returns:
        Lista de dicionarios representando os chunks canonicos, com campos:
            source: str       — sempre '_distilled/'
            heading: str      — 'Canonical Pattern N'
            content: str      — conteudo sintetizado (ou fallback)
            score: float      — media dos scores do cluster
            tags: list        — lista vazia
            _original_cluster_size: int   — quantos chunks originaram este
            _original_sources: list[str]  — fontes originais do cluster

    Example:
        >>> from cluster import cluster_chunks
        >>> clusters = cluster_chunks(similarity_threshold=0.85)
        >>> canonicals = distill_clusters(clusters)
        >>> for c in canonicals:
        ...     print(f"{c['heading']}: {c['content'][:80]}...")
    """
    if not clusters:
        return []

    canonical_chunks: list[dict] = []

    for i, cluster in enumerate(clusters):
        if not cluster:
            continue

        # ── 1. Concatena conteudos (limitado a 3000 chars) ──────────────
        contents: list[str] = []
        for chunk in cluster:
            content = chunk.get("content", "")
            if content:
                contents.append(content)

        concatenated = "\n\n---\n\n".join(contents)
        if len(concatenated) > 3000:
            concatenated = concatenated[:3000] + "..."

        # ── 2. Score agregado = media dos scores ────────────────────────
        scores = [chunk.get("score", 0.5) for chunk in cluster]
        avg_score = sum(scores) / len(scores) if scores else 0.5

        # ── 3. Geracao do chunk canonico ────────────────────────────────
        prompt = (
            "Sintetize esses fragmentos similares em um único "
            "padrão canônico conciso:\n\n"
            f"{concatenated}"
        )

        canonical_content: str | None = None

        # Tenta via LLM se disponivel
        if _LLM_BACKEND:
            canonical_content = _call_llm(prompt)

        # Se nao conseguiu gerar via LLM (ou LLM nao disponivel):
        # imprime prompt para revisao e usa fallback
        if canonical_content is None:
            _print_prompt_for_review(prompt, i)

            # Fallback: chunk de maior score do cluster
            best_chunk = max(cluster, key=lambda c: c.get("score", 0.0))
            canonical_content = best_chunk.get("content", "")
            print(f"   🔄  Fallback: usando chunk de maior score "
                  f"(score={best_chunk.get('score', 0.0):.3f}, "
                  f"id={best_chunk.get('id', '?' )})")

        # ── 4. Monta o chunk canonico ───────────────────────────────────
        canonical = {
            "source": "_distilled/",
            "heading": f"Canonical Pattern {i + 1}",
            "content": canonical_content,
            "score": round(avg_score, 4),
            "tags": [],
            "_original_cluster_size": len(cluster),
            "_original_sources": sorted(set(
                c.get("source", "") for c in cluster
            )),
        }
        canonical_chunks.append(canonical)

    return canonical_chunks


# ── Bloco de testes rapido (executavel com python distill.py) ───────────────

if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from cluster import cluster_chunks

    print("🔬  Testando distill_clusters...")
    print(f"    LLM backend: {_LLM_BACKEND or 'nenhum (fallback: maior score)'}")
    print()

    clusters = cluster_chunks(similarity_threshold=0.85)

    if not clusters:
        print("⚠️  Nenhum cluster encontrado. Execute cli_index.py primeiro.")
        sys.exit(0)

    total_chunks = sum(len(c) for c in clusters)
    print(f"✅  {len(clusters)} clusters carregados "
          f"({total_chunks} chunks total).\n")

    canonicals = distill_clusters(clusters)

    print(f"\n{'=' * 60}")
    print(f"📊  Resultado: {len(canonicals)} chunks canonicos gerados")
    print(f"{'=' * 60}\n")

    for c in canonicals:
        print(f"  {c['heading']} "
              f"(score={c['score']:.3f}, "
              f"de {c['_original_cluster_size']} chunks)")
        print(f"    Fontes: {', '.join(c['_original_sources'][:3])}")
        print(f"    Preview: {c['content'][:120].replace(chr(10), ' ')}...")
        print()
