"""Demonstrate automatic metadata-aware Qdrant retrieval."""

from __future__ import annotations

from industrial_copilot.retrieval.embedder import (

    Embedder,

)

from industrial_copilot.retrieval.query_analyzer import (

    analyze_query,

)

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.query_service import (

    retrieve_query,

)

QUERIES = [

    (

        "How often should the hydraulic pump "

        "on the MX-200 be inspected?"

    ),

    (

        "How often should the hydraulic pump "

        "on the MX-300 be inspected?"

    ),

    "What does alarm HX-417 mean?",

]

def main() -> None:

    embedder = Embedder()

    client = create_qdrant_client()

    for query in QUERIES:

        analysis = analyze_query(query)

        results = retrieve_query(

            query=query,

            client=client,

            embedder=embedder,

            top_k=5,

        )

        print("=" * 80)

        print(f"QUERY: {query}")

        print(

            "Detected machine models: "

            f"{analysis.machine_models}"

        )

        print()

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

if __name__ == "__main__":

    main()
