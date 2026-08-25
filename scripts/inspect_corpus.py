"""Inspect the complete generated retrieval corpus."""

from __future__ import annotations

from collections import Counter

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def main() -> None:

    """Build the corpus and print useful summary statistics."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    chunks_per_document = Counter(

        chunk.document_id

        for chunk in chunks

    )

    chunks_per_type = Counter(

        chunk.document_type

        for chunk in chunks

    )

    print("Retrieval Corpus")

    print("=" * 80)

    print(f"Documents: {len(repository.documents.documents)}")

    print(f"Total chunks: {len(chunks)}")

    print()

    print("Chunks by document")

    print("-" * 80)

    for document_id, count in sorted(

        chunks_per_document.items()

    ):

        print(

            f"{document_id:<20} {count:>3}"

        )

    print()

    print("Chunks by document type")

    print("-" * 80)

    for document_type, count in sorted(

        chunks_per_type.items()

    ):

        print(

            f"{document_type:<35} {count:>3}"

        )

if __name__ == "__main__":

    main()
