"""
T005 — search.py: Busca semântica por similaridade de cosseno.

Embedda a query com SentenceTransformer, carrega todos os chunks com embedding
do SQLite, calcula cosine similarity e retorna os top-k mais similares.
"""

import json
import math
import sqlite3
from typing import Any

try:
    import numpy as np

    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

from store import DB_PATH  # ~/.hermes/wiki_index.db
from bm25 import BM25Retriever


# ── Helpers de vetor ───────────────────────────────────────────────────────

def _deserialize_embedding(blob: bytes):
    """Converte bytes blob para vetor (numpy array ou lista Python)."""
    if _HAS_NUMPY:
        return np.frombuffer(blob, dtype=np.float32)
    else:
        # Fallback Python puro: 4 bytes por float32
        floats = []
        for i in range(0, len(blob), 4):
            # struct.unpack é lento, mas funcional
            import struct
            floats.append(struct.unpack('f', blob[i:i+4])[0])
        return floats


def _cosine_similarity(a, b) -> float:
    """Calcula cosine similarity entre dois vetores (numpy ou listas)."""
    if _HAS_NUMPY:
        dot = float(np.dot(a, b))
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
    else:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── API pública ────────────────────────────────────────────────────────────

def search_similar(
    query_text: str,
    model: Any,  # SentenceTransformer
    k: int = 5,
    hybrid: bool = False,
    threshold: float | None = None,
    alpha: float = 0.7,
) -> list[dict]:
    """
    Busca os top-k chunks mais similares à query_text.

    Modos:
    - Padrão (hybrid=False): busca por cosine similarity pura.
    - Hybrid (hybrid=True): combina cosine similarity (embedding) com BM25
      (lexical) usando alpha como peso da parte semântica. Ambos os scores
      são normalizados para [0, 1] antes da combinação.

    Args:
        query_text: Texto da consulta em linguagem natural.
        model: Instância carregada de SentenceTransformer.
        k: Número de resultados a retornar (default: 5).
        hybrid: Se True, ativa o modo híbrido (semântico + lexical).
        threshold: Se definido, filtra resultados com hybrid_score < threshold
                   (só tem efeito quando hybrid=True).
        alpha: Peso da similaridade semântica na combinação híbrida
               (default: 0.7). O peso lexical é (1 - alpha).

    Returns:
        Lista de dicionários com chaves:
        chunk_id, source, heading, content, similarity, score,
        content_hash, tags.

        No modo hybrid, inclui adicionalmente:
        bm25_score, hybrid_score.

        Ordenada por similarity (modo padrão) ou hybrid_score (modo hybrid)
        decrescente.
    """
    # 1. Embedda a query
    query_embedding = model.encode(
        query_text,
        convert_to_numpy=_HAS_NUMPY,
        show_progress_bar=False,
    )
    if _HAS_NUMPY and not isinstance(query_embedding, np.ndarray):
        query_embedding = np.array(query_embedding)

    # 2. Carrega todos os chunks com embedding do SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, source, heading, content, embedding, score, "
            "content_hash, tags "
            "FROM chunks WHERE embedding IS NOT NULL"
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    # 3. Converte rows para lista de dicionários (mantendo conteúdo cru)
    chunks = []
    for row in rows:
        tags = row["tags"]
        if tags:
            try:
                tags = json.loads(tags)
            except (json.JSONDecodeError, TypeError):
                pass
        chunks.append({
            "chunk_id": row["id"],
            "source": row["source"],
            "heading": row["heading"],
            "content": row["content"],
            "embedding": row["embedding"],
            "score": row["score"],
            "content_hash": row["content_hash"],
            "tags": tags,
        })

    # 4. Calcula cosine similarity para cada chunk
    cosine_scores = []
    for chunk in chunks:
        chunk_embedding = _deserialize_embedding(chunk["embedding"])
        sim = _cosine_similarity(query_embedding, chunk_embedding)
        cosine_scores.append(sim)

    # 5. Modo padrão (apenas cosine similarity)
    if not hybrid:
        for i, chunk in enumerate(chunks):
            chunk["similarity"] = cosine_scores[i]

        chunks.sort(key=lambda r: r["similarity"], reverse=True)
        return chunks[:k]

    # 6. Modo híbrido: cosine + BM25
    # 6a. Cria BM25Retriever e obtém scores lexicais
    bm25_retriever = BM25Retriever(chunks)
    bm25_indexed = bm25_retriever.search(query_text, k=len(chunks))
    # Constrói array de BM25 scores alinhado com chunks
    bm25_scores = [0.0] * len(chunks)
    for idx, score in bm25_indexed:
        bm25_scores[idx] = score

    # 6b. Normaliza ambos os scores para [0, 1] via min-max
    def _minmax_normalize(scores: list[float]) -> list[float]:
        mn = min(scores)
        mx = max(scores)
        if mx == mn:
            return [0.0] * len(scores)
        return [(s - mn) / (mx - mn) for s in scores]

    cosine_norm = _minmax_normalize(cosine_scores)
    bm25_norm = _minmax_normalize(bm25_scores)

    # 6c. Combina scores
    for i, chunk in enumerate(chunks):
        chunk["similarity"] = cosine_scores[i]
        chunk["bm25_score"] = bm25_scores[i]
        chunk["hybrid_score"] = alpha * cosine_norm[i] + (1 - alpha) * bm25_norm[i]

    # 6d. Ordena por hybrid_score DESC
    chunks.sort(key=lambda r: r["hybrid_score"], reverse=True)

    # 6e. Filtra por threshold se definido
    if threshold is not None:
        chunks = [c for c in chunks if c["hybrid_score"] >= threshold]

    # 6f. Retorna top-k
    return chunks[:k]
