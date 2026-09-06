"""High-level metadata-aware retrieval using Qdrant."""

from __future__ import annotations

from qdrant_client import QdrantClient

from industrial_copilot.retrieval.embedder import Embedder

from industrial_copilot.retrieval.query_analyzer import (

    QueryIntent,

    analyze_query,

)

from industrial_copilot.vector_store.retriever import (

    QdrantSearchResult,

    search_qdrant,

)

def retrieve_query(

    *,

    query: str,

    client: QdrantClient,

    embedder: Embedder,

    top_k: int = 5,

) -> list[QdrantSearchResult]:

    """Analyze a user query and retrieve relevant Qdrant chunks."""

    analysis = analyze_query(query)

    machine_model = None

    if len(analysis.machine_models) == 1:

        machine_model = analysis.machine_models[0]

    alarm_code = None

    if len(analysis.alarm_codes) == 1:

        alarm_code = analysis.alarm_codes[0]

    contains_spare_parts = None

    if analysis.intent == QueryIntent.PARTS_LOOKUP:

        contains_spare_parts = True

    query_embedding = embedder.embed_query(

        query

    )

    return search_qdrant(

        client=client,

        query_embedding=query_embedding,

        top_k=top_k,

        machine_model=machine_model,

        alarm_code=alarm_code,

        contains_spare_parts=contains_spare_parts,

    )
