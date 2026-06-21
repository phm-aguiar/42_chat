"""
T002 — bm25.py: BM25 lexical retrieval for wiki chunks.

Fornece BM25Retriever, que indexa um corpus de chunks e permite
busca lexical com scores BM25 clássicos via rank_bm25.
"""

from typing import Any

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """Retriever BM25 para busca lexical em chunks de documentos wiki.

    Tokeniza o conteúdo de cada chunk (split por whitespace, lowercase)
    e constrói o índice BM25 clássico via rank_bm25.BM25Okapi.
    """

    def __init__(self, chunks: list[dict[str, Any]]) -> None:
        """Inicializa o retriever com uma lista de chunks.

        Args:
            chunks: Lista de dicionários, cada um com ao menos a chave 'content'.
                    Espera-se que sejam chunks com embedding (embedding IS NOT NULL).
        """
        self._chunks = chunks
        # Tokeniza conteúdo de cada chunk: split por whitespace, lowercase
        self._corpus = [
            self._tokenize(chunk.get("content", ""))
            for chunk in chunks
        ]
        # Constrói o BM25 clássico
        self._bm25 = BM25Okapi(self._corpus)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokeniza texto: split por whitespace + lowercase."""
        return text.lower().split()

    def search(self, query: str, k: int = 5) -> list[tuple[int, float]]:
        """Busca os top-k chunks mais relevantes para a query.

        Args:
            query: Texto da consulta.
            k: Número de resultados a retornar (default: 5).

        Returns:
            Lista de tuplas (chunk_index, bm25_score) ordenada por
            score decrescente. chunk_index é a posição do chunk na lista
            original fornecida no __init__.
        """
        if not self._corpus:
            return []

        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        # Cria lista de (índice, score) e ordena por score decrescente
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return indexed_scores[:k]
