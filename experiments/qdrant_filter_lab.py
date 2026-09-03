"""Compare unrestricted and machine-filtered Qdrant retrieval."""

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

def _print_results(

    title: str,

    results,

) -> None:

    print(title)

    print("-" * 80)

    for rank, result in enumerate(

        results,

        start=1,

    ):

        print(

            f"{rank}. "

            f"{result.score:.4f} | "

            f"{result.document_id} | "

            f"{result.section_title} | "

            f"models={result.machine_models}"

        )

    print()

def main() -> None:

    embedder = Embedder()

    query_embedding = embedder.embed_query(

        QUERY

    )

    client = create_qdrant_client()

    unrestricted_results = search_qdrant(

        client=client,

        query_embedding=query_embedding,

        top_k=5,

    )

    filtered_results = search_qdrant(

        client=client,

        query_embedding=query_embedding,

        top_k=5,

        machine_model="MX-200",

    )

    print("QUERY")

    print("-" * 80)

    print(QUERY)

    print()

    _print_results(

        "UNRESTRICTED",

        unrestricted_results,

    )

    _print_results(

        "FILTERED: MX-200",

        filtered_results,

    )

if __name__ == "__main__":

    main()
