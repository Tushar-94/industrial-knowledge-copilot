"""Hybrid retrieval using Reciprocal Rank Fusion."""

from __future__ import annotations

from collections import defaultdict

from dataclasses import dataclass

from industrial_copilot.retrieval.in_memory import SearchResult

from industrial_copilot.retrieval.lexical import LexicalSearchResult

from industrial_copilot.retrieval.models import Chunk

@dataclass(frozen=True)

class HybridSearchResult:

    """One fused retrieval result."""

    chunk: Chunk

    score: float

def reciprocal_rank_fusion(

    *,

    dense_results: list[SearchResult],

    lexical_results: list[LexicalSearchResult],

    top_k: int = 5,

    rrf_k: int = 60,

) -> list[HybridSearchResult]:

    """Fuse dense and lexical rankings using Reciprocal Rank Fusion."""

    if top_k <= 0:

        raise ValueError("top_k must be greater than zero.")

    if rrf_k <= 0:

        raise ValueError("rrf_k must be greater than zero.")

    scores: dict[str, float] = defaultdict(float)

    chunks_by_id: dict[str, Chunk] = {}

    for rank, result in enumerate(

        dense_results,

        start=1,

    ):

        chunk_id = result.chunk.chunk_id

        scores[chunk_id] += 1.0 / (rrf_k + rank)

        chunks_by_id[chunk_id] = result.chunk

    for rank, result in enumerate(

        lexical_results,

        start=1,

    ):

        chunk_id = result.chunk.chunk_id

        scores[chunk_id] += 1.0 / (rrf_k + rank)

        chunks_by_id[chunk_id] = result.chunk

    ranked_chunk_ids = sorted(

        scores,

        key=scores.get,

        reverse=True,

    )[:top_k]

    return [

        HybridSearchResult(

            chunk=chunks_by_id[chunk_id],

            score=scores[chunk_id],

        )

        for chunk_id in ranked_chunk_ids

    ]
