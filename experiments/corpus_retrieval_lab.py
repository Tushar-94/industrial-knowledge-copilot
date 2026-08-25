
"""Run semantic retrieval over the complete generated knowledge corpus."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

from industrial_copilot.retrieval.embedder import Embedder

from industrial_copilot.retrieval.in_memory import (

    search_embeddings,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

QUERIES = [

    "How often should the hydraulic pump on the MX-200 be inspected?",

    "When should the MX-300 return filter be replaced?",

    "What does alarm HX-417 mean?",

    "What can cause HX-417?",

    "Which procedure explains hydraulic return filter replacement?",

    "Which replacement filter is compatible with the MX-300?",

]

def main() -> None:

    """Search the complete corpus with representative queries."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    embedder = Embedder()

    # We embed the corpus once.

    chunk_embeddings = embedder.embed_chunks(chunks)

    print(f"Corpus chunks: {len(chunks)}")

    print(

        f"Embedding dimension: "

        f"{embedder.embedding_dimension}"

    )

    print()

    for query in QUERIES:

        query_embedding = embedder.embed_query(query)

        results = search_embeddings(

            chunks=chunks,

            chunk_embeddings=chunk_embeddings,

            query_embedding=query_embedding,

            top_k=5,

        )

        print("=" * 100)

        print(f"QUERY: {query}")

        print("=" * 100)

        for rank, result in enumerate(results, start=1):

            print(

                f"{rank}. "

                f"score={result.score:.4f} | "

                f"{result.chunk.document_id} | "

                f"{result.chunk.section_title}"

            )

        print()

if __name__ == "__main__":

    main()

