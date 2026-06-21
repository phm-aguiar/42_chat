"""
T013 — cluster.py: Clusterização de chunks por similaridade semântica.

Carrega todos os chunks com embedding do SQLite, calcula similaridades e
agrupa chunks semanticamente próximos usando KMeans (com sklearn) ou um
algoritmo guloso como fallback.

API pública:
    cluster_chunks(similarity_threshold=0.85) -> list[list[dict]]
"""

import json
import math
import sqlite3
from typing import Any

# ── Tentativa de importar numpy / sklearn ──────────────────────────────────

_HAS_NUMPY = False
_HAS_SKLEARN = False

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    pass

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    _HAS_SKLEARN = True
except ImportError:
    pass

from store import DB_PATH  # ~/.hermes/wiki_index.db


# ── Helpers de vetor (compartilhados com search.py) ────────────────────────

def _deserialize_embedding(blob: bytes):
    """Converte bytes blob para vetor (numpy array ou lista Python)."""
    if _HAS_NUMPY:
        return np.frombuffer(blob, dtype=np.float32)
    else:
        # Fallback Python puro: 4 bytes por float32
        floats = []
        for i in range(0, len(blob), 4):
            import struct
            floats.append(struct.unpack('f', blob[i:i + 4])[0])
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


# ── Carregamento do banco ──────────────────────────────────────────────────

def _load_chunks_with_embeddings() -> list[dict]:
    """
    Carrega todos os chunks que possuem embedding do SQLite.

    Returns:
        Lista de dicionários com os campos completos do chunk mais o vetor
        de embedding já desserializado na chave '_embedding'.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, source, heading, content, embedding, score, "
            "content_hash, tags, char_count, created_at, last_updated "
            "FROM chunks WHERE embedding IS NOT NULL"
        ).fetchall()
    finally:
        conn.close()

    chunks = []
    for row in rows:
        d = dict(row)
        # Desserializa embedding
        d['_embedding'] = _deserialize_embedding(row['embedding'])
        # Converte tags de JSON string para lista
        if d.get('tags'):
            try:
                d['tags'] = json.loads(d['tags'])
            except (json.JSONDecodeError, TypeError):
                pass
        chunks.append(d)

    return chunks


# ── Estratégia com KMeans (sklearn) ────────────────────────────────────────

def _cluster_kmeans(
    chunks: list[dict],
) -> list[list[dict]]:
    """
    Clusterização via KMeans com seleção automática de k via elbow method
    (silhouette score) ou sqrt(n) como fallback.

    Args:
        chunks: Lista de chunks com chave '_embedding' (numpy array).

    Returns:
        Lista de clusters, cada cluster = lista de chunks.
    """
    n = len(chunks)

    # Casos triviais
    if n == 0:
        return []
    if n == 1:
        return [chunks]

    # Empilha embeddings em matriz (n_samples, n_features)
    X = np.vstack([c['_embedding'] for c in chunks])

    # Determina número de clusters: elbow method com silhouette score
    k = _pick_k_elbow(X, n)

    # Aplica KMeans
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)

    # Agrupa por label
    clusters: dict[int, list[dict]] = {}
    for chunk, label in zip(chunks, labels):
        label = int(label)
        clusters.setdefault(label, []).append(chunk)

    # Retorna lista de listas, ordenada por tamanho decrescente
    result = sorted(clusters.values(), key=len, reverse=True)
    return result


def _pick_k_elbow(X, n: int) -> int:
    """
    Seleciona o número de clusters k usando silhouette score como elbow proxy.

    Testa valores de k de 2 até min(10, n-1) e escolhe o k com maior
    silhouette score. Se não for possível calcular, usa sqrt(n) como fallback.

    Args:
        X: Matriz (n_samples, n_features) numpy.
        n: Número de amostras.

    Returns:
        Número de clusters k (mínimo 2 quando n >= 2).
    """
    max_k = min(10, n - 1)

    if max_k < 2:
        return 1

    best_k = max(2, int(math.sqrt(n)))
    best_score = -1.0

    for k_candidate in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k_candidate, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(X)

        # Silhouette precisa de pelo menos 2 clusters com mais de 1 amostra
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            continue

        try:
            score = silhouette_score(X, labels)
            if score > best_score:
                best_score = score
                best_k = k_candidate
        except Exception:
            # Se silhouette falhar, mantém o k atual
            continue

    return best_k


# ── Estratégia gulosa (fallback sem sklearn) ───────────────────────────────

def _cluster_greedy(
    chunks: list[dict],
    similarity_threshold: float,
) -> list[list[dict]]:
    """
    Algoritmo guloso: para cada chunk não visitado, encontra todos os chunks
    com cosine similarity > threshold e forma um cluster.

    Complexidade: O(n²) pairwise similarities.

    Args:
        chunks: Lista de chunks com chave '_embedding'.
        similarity_threshold: Limiar de similaridade (0.0 a 1.0).

    Returns:
        Lista de clusters, cada cluster = lista de chunks similares.
    """
    n = len(chunks)

    if n == 0:
        return []
    if n == 1:
        return [chunks]

    visited: set[int] = set()
    clusters: list[list[dict]] = []

    for i in range(n):
        if i in visited:
            continue

        # Inicia novo cluster com o chunk atual
        cluster = [chunks[i]]
        visited.add(i)

        # Encontra todos os chunks similares ainda não visitados
        for j in range(i + 1, n):
            if j in visited:
                continue

            sim = _cosine_similarity(
                chunks[i]['_embedding'],
                chunks[j]['_embedding'],
            )

            if sim > similarity_threshold:
                cluster.append(chunks[j])
                visited.add(j)

        clusters.append(cluster)

    # Ordena por tamanho decrescente
    clusters.sort(key=len, reverse=True)
    return clusters


# ── API pública ─────────────────────────────────────────────────────────────

def cluster_chunks(
    similarity_threshold: float = 0.85,
) -> list[list[dict]]:
    """
    Clusteriza todos os chunks com embedding por similaridade semântica.

    Estratégia:
    1. Carrega todos os chunks com embedding do SQLite.
    2. Se sklearn disponível: usa KMeans com seleção automática de k
       (silhouette / elbow method ou sqrt(n)).
    3. Fallback sem sklearn: algoritmo guloso — para cada chunk não visitado,
       encontra todos com cosine similarity > threshold e forma um cluster.

    Args:
        similarity_threshold: Limiar de similaridade usado apenas no modo
            guloso (padrão: 0.85). Ignorado no modo KMeans.

    Returns:
        Lista de clusters. Cada cluster é uma lista de dicionários com os
        campos completos do chunk (id, source, heading, content, score,
        content_hash, tags, char_count, created_at, last_updated) mais a
        chave '_embedding' com o vetor desserializado.

        Clusters ordenados por tamanho decrescente. Chunks sem embedding
        são ignorados.

    Example:
        >>> clusters = cluster_chunks(similarity_threshold=0.85)
        >>> for i, cluster in enumerate(clusters):
        ...     print(f"Cluster {i}: {len(cluster)} chunks")
        ...     for chunk in cluster:
        ...         print(f"  - {chunk['heading']}: {chunk['content'][:60]}...")
    """
    # 1. Carrega chunks com embedding
    chunks = _load_chunks_with_embeddings()

    if not chunks:
        return []

    # 2. Escolhe estratégia
    if _HAS_SKLEARN and _HAS_NUMPY:
        return _cluster_kmeans(chunks)

    # 3. Fallback guloso
    return _cluster_greedy(chunks, similarity_threshold)


# ── Bloco de testes rápido (executável com python cluster.py) ───────────────

if __name__ == '__main__':
    import sys

    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.85

    print(f"🔬 Clusterizando chunks com threshold={threshold}...")
    print(f"   numpy={_HAS_NUMPY}  sklearn={_HAS_SKLEARN}")
    print()

    clusters = cluster_chunks(similarity_threshold=threshold)

    if not clusters:
        print("⚠️  Nenhum chunk com embedding encontrado no banco.")
        sys.exit(0)

    print(f"✅ {len(clusters)} clusters formados a partir de "
          f"{sum(len(c) for c in clusters)} chunks:\n")

    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i + 1}: {len(cluster)} chunks")
        for chunk in cluster[:3]:  # mostra só os 3 primeiros de cada cluster
            heading = chunk.get('heading', '') or '(sem heading)'
            content_preview = chunk['content'][:80].replace('\n', ' ')
            print(f"    [{chunk['id']}] {heading}")
            print(f"         {content_preview}...")
        if len(cluster) > 3:
            print(f"    ... +{len(cluster) - 3} mais")
        print()
