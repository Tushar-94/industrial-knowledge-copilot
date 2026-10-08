"""Hybrid Qdrant dense and lexical retrieval."""

from __future__ import annotations

import numpy as np

from numpy.typing import NDArray

from qdrant_client import QdrantClient

from industrial_copilot.retrieval.hybrid import (

    HybridSearchResult,

    reciprocal_rank_fusion,

)

from industrial_copilot.retrieval.constraints import (

    build_retrieval_constraints,

    chunk_matches_constraints,

)

from industrial_copilot.retrieval.in_memory import SearchResult

from industrial_copilot.retrieval.lexical import BM25Retriever

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.retrieval.query_analyzer import QueryAnalysis

from industrial_copilot.vector_store.retriever import (

    QdrantSearchResult,

    search_qdrant,

)

def adapt_qdrant_results(

    *,

    qdrant_results: list[QdrantSearchResult],

    chunks_by_id: dict[str, Chunk],

) -> list[SearchResult]:

    """Convert Qdrant results into the common retrieval result shape."""

    results: list[SearchResult] = []

    for result in qdrant_results:

        chunk = chunks_by_id.get(

            result.chunk_id

        )

        if chunk is None:

            continue

        results.append(

            SearchResult(

                chunk=chunk,

                score=result.score,

            )

        )

    return results

class HybridRetriever:

    """Combine Qdrant dense search and BM25 lexical search."""

    def __init__(

        self,

        *,

        chunks: list[Chunk],

        client: QdrantClient,

    ) -> None:

        self.chunks = chunks

        self.client = client

        self.chunks_by_id = {

            chunk.chunk_id: chunk

            for chunk in chunks

        }

        self.lexical = BM25Retriever(chunks)

    def search(

        self,

        *,

        query: str,

        query_embedding: NDArray[np.float32],

        analysis: QueryAnalysis,

        top_k: int = 5,

        candidate_k: int = 20,

    ) -> list[HybridSearchResult]:

        """Search with Qdrant and BM25, then fuse rankings."""

        constraints = build_retrieval_constraints(

            analysis

        )

        eligible_chunk_ids = {

            chunk.chunk_id

            for chunk in self.chunks

            if chunk_matches_constraints(

                chunk,

                constraints,

            )

        }

        qdrant_results = search_qdrant(

            client=self.client,

            query_embedding=query_embedding,

            top_k=candidate_k,

            machine_model=constraints.machine_model,

            alarm_code=constraints.alarm_code,

            procedure_id=constraints.procedure_id,

            part_number=constraints.part_number,

            contains_spare_parts=constraints.contains_spare_parts,

        )
        dense_results = adapt_qdrant_results(

            qdrant_results=qdrant_results,

            chunks_by_id=self.chunks_by_id,

        )

        lexical_results = self.lexical.search(

            query,

            top_k=candidate_k,

            eligible_chunk_ids=eligible_chunk_ids,

        )

        return reciprocal_rank_fusion(

            dense_results=dense_results,

            lexical_results=lexical_results,

            top_k=top_k,

        )