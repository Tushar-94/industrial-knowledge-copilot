"""Run semantic retrieval over the generated MX-200 manual."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.embedder import Embedder

from industrial_copilot.retrieval.in_memory import (

    search_embeddings,

)

from industrial_copilot.retrieval.markdown_chunker import (

    chunk_markdown_file,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

QUERY = "How often should I inspect the hydraulic pump on the MX-200?"

def main() -> None:

    """Embed chunks and rank them against one user query."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == "MAN-MX200-001"

    )

    chunks = chunk_markdown_file(

        path=DOCUMENT_DIR / "MAN-MX200-001.md",

        document=document,

    )

    embedder = Embedder()

    chunk_embeddings = embedder.embed_chunks(chunks)

    query_embedding = embedder.embed_query(QUERY)

    results = search_embeddings(

        chunks=chunks,

        chunk_embeddings=chunk_embeddings,

        query_embedding=query_embedding,

        top_k=5,

    )

    print(f"Query: {QUERY}")

    print()

    print(f"Chunks searched: {len(chunks)}")

    print(

        f"Embedding dimension: "

        f"{embedder.embedding_dimension}"

    )

    print()

    for rank, result in enumerate(results, start=1):

        print("=" * 80)

        print(f"Rank: {rank}")

        print(f"Score: {result.score:.4f}")

        print(f"Chunk ID: {result.chunk.chunk_id}")

        print(f"Section: {result.chunk.section_title}")

        print()

        print(result.chunk.text[:700])

        if len(result.chunk.text) > 700:

            print("...")

        print()

if __name__ == "__main__":

    main()
