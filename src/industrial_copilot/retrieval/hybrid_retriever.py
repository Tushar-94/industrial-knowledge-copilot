"""Hybrid dense and lexical retrieval."""

from __future__ import annotations

import numpy as np

from numpy.typing import NDArray

from industrial_copilot.retrieval.hybrid import (

    HybridSearchResult,

    reciprocal_rank_fusion,

)

from industrial_copilot.retrieval.in_memory import (

    search_embeddings,

)

from industrial_copilot.retrieval.lexical import (

    BM25Retriever,

)

from industrial_copilot.retrieval.models import Chunk

class HybridRetriever:

    """Combine dense semantic search and BM25 lexical search."""

    def __init__(

        self,

        *,

        chunks: list[Chunk],

        chunk_embeddings: NDArray[np.float32],

    ) -> None:

        self.chunks = chunks

        self.chunk_embeddings = chunk_embeddings

        self.lexical = BM25Retriever(chunks)

    def search(

        self,

        *,

        query: str,

        query_embedding: NDArray[np.float32],

        top_k: int = 5,

        candidate_k: int = 20,

    ) -> list[HybridSearchResult]:

        """Search with dense retrieval and BM25, then fuse rankings."""

        dense_results = search_embeddings(

            chunks=self.chunks,

            chunk_embeddings=self.chunk_embeddings,

            query_embedding=query_embedding,

            top_k=candidate_k,

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
