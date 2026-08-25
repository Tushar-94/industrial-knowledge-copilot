"""Simple in-memory semantic retrieval for learning and evaluation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from numpy.typing import NDArray

from industrial_copilot.retrieval.models import Chunk

@dataclass(frozen=True)

class SearchResult:

    """One ranked semantic-search result."""

    chunk: Chunk

    score: float

def search_embeddings(

    *,

    chunks: list[Chunk],

    chunk_embeddings: NDArray[np.float32],

    query_embedding: NDArray[np.float32],

    top_k: int = 5,

) -> list[SearchResult]:

    """Rank chunks by similarity to a normalized query embedding."""

    if len(chunks) != len(chunk_embeddings):

        raise ValueError(

            "Number of chunks must match number of chunk embeddings."

        )

    if top_k <= 0:

        raise ValueError("top_k must be greater than zero.")

    scores = chunk_embeddings @ query_embedding

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    return [

        SearchResult(

            chunk=chunks[index],

            score=float(scores[index]),

        )

        for index in ranked_indices

    ]
