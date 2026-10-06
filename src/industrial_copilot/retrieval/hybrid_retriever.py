"""Hybrid Qdrant dense and lexical retrieval."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from numpy.typing import NDArray

from qdrant_client import QdrantClient

from industrial_copilot.retrieval.hybrid import (

    HybridSearchResult,

    reciprocal_rank_fusion,

)

from industrial_copilot.retrieval.in_memory import SearchResult

from industrial_copilot.retrieval.lexical import BM25Retriever

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.retrieval.query_analyzer import (

    QueryAnalysis,

    QueryIntent,

)

from industrial_copilot.vector_store.retriever import (

    QdrantSearchResult,

    search_qdrant,

)

@dataclass(frozen=True)

class QdrantQueryConstraints:

    """Structured Qdrant filters derived from query analysis."""

    machine_model: str | None = None

    alarm_code: str | None = None

    procedure_id: str | None = None

    part_number: str | None = None

    contains_spare_parts: bool | None = None

def build_qdrant_constraints(

    analysis: QueryAnalysis,

) -> QdrantQueryConstraints:

    """Translate analyzed query metadata into Qdrant constraints."""

    machine_model = (

        analysis.machine_models[0]

        if len(analysis.machine_models) == 1

        else None

    )

    alarm_code = (

        analysis.alarm_codes[0]

        if len(analysis.alarm_codes) == 1

        else None

    )

    procedure_id = (

        analysis.procedure_ids[0]

        if len(analysis.procedure_ids) == 1

        else None

    )

    part_number = (

        analysis.part_numbers[0]

        if len(analysis.part_numbers) == 1

        else None

    )

    contains_spare_parts = (

        True

        if analysis.intent == QueryIntent.PARTS_LOOKUP

        else None

    )

    return QdrantQueryConstraints(

        machine_model=machine_model,

        alarm_code=alarm_code,

        procedure_id=procedure_id,

        part_number=part_number,

        contains_spare_parts=contains_spare_parts,

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

        constraints = build_qdrant_constraints(

            analysis

        )

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

        )

        return reciprocal_rank_fusion(

            dense_results=dense_results,

            lexical_results=lexical_results,

            top_k=top_k,

        )