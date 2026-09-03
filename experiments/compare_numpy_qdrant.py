"""Compare NumPy dense retrieval with Qdrant dense retrieval."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

from industrial_copilot.retrieval.embedder import (

    Embedder,

)

from industrial_copilot.retrieval.in_memory import (

    search_embeddings,

)

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.retriever import (

    search_qdrant,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = (

    PROJECT_ROOT

    / "data"

    / "generated"

    / "markdown"

)

QUERY = (

    "How often should the hydraulic pump "

    "on the MX-200 be inspected?"

)

def main() -> None:

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    embedder = Embedder()

    chunk_embeddings = embedder.embed_chunks(

        chunks

    )

    query_embedding = embedder.embed_query(

        QUERY

    )

    numpy_results = search_embeddings(

        chunks=chunks,

        chunk_embeddings=chunk_embeddings,

        query_embedding=query_embedding,

        top_k=5,

    )

    client = create_qdrant_client()

    qdrant_results = search_qdrant(

        client=client,

        query_embedding=query_embedding,

        top_k=5,

    )

    print("QUERY")

    print("-" * 80)

    print(QUERY)

    print()

    print("NUMPY")

    print("-" * 80)

    for rank, result in enumerate(

        numpy_results,

        start=1,

    ):

        print(

            f"{rank}. "

            f"{result.score:.4f} | "

            f"{result.chunk.document_id} | "

            f"{result.chunk.section_title}"

        )

    print()

    print("QDRANT")

    print("-" * 80)

    for rank, result in enumerate(

        qdrant_results,

        start=1,

    ):

        print(

            f"{rank}. "

            f"{result.score:.4f} | "

            f"{result.document_id} | "

            f"{result.section_title}"

        )

if __name__ == "__main__":

    main()
