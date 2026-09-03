"""Run the first semantic query against persistent Qdrant vectors."""

from __future__ import annotations

from industrial_copilot.retrieval.embedder import (

    Embedder,

)

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.retriever import (

    search_qdrant,

)

QUERY = (

    "How often should the hydraulic pump "

    "on the MX-200 be inspected?"

)

def main() -> None:

    """Embed one query and search the local Qdrant collection."""

    embedder = Embedder()

    query_embedding = embedder.embed_query(

        QUERY

    )

    client = create_qdrant_client()

    results = search_qdrant(

        client=client,

        query_embedding=query_embedding,

        top_k=5,

    )

    print(f"Query: {QUERY}")

    print()

    for rank, result in enumerate(

        results,

        start=1,

    ):

        print("=" * 80)

        print(f"Rank: {rank}")

        print(f"Score: {result.score:.4f}")

        print(f"Document: {result.document_id}")

        print(f"Section: {result.section_title}")

        print(f"Chunk ID: {result.chunk_id}")

        print()

        print(result.text[:700])

        if len(result.text) > 700:

            print("...")

        print()

if __name__ == "__main__":

    main()
