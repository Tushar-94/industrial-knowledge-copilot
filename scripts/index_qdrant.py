"""Build and persist the complete retrieval corpus in Qdrant."""

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

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

    ensure_collection,

)

from industrial_copilot.vector_store.config import (

    COLLECTION_NAME,

)

from industrial_copilot.vector_store.indexer import (

    index_chunks,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = (

    PROJECT_ROOT

    / "data"

    / "generated"

    / "markdown"

)

def main() -> None:

    """Index the generated corpus into local Qdrant."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    embedder = Embedder()

    embeddings = embedder.embed_chunks(

        chunks

    )

    client = create_qdrant_client()

    ensure_collection(client)

    index_chunks(

        client=client,

        chunks=chunks,

        embeddings=embeddings,

    )

    collection = client.get_collection(

        collection_name=COLLECTION_NAME

    )

    print("Qdrant indexing complete")

    print("=" * 60)

    print(f"Chunks indexed: {len(chunks)}")

    print(f"Embedding dimension: {embedder.embedding_dimension}")

    print(f"Stored points: {collection.points_count}")

if __name__ == "__main__":

    main()
