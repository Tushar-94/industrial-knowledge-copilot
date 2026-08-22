"""Inspect structure-aware chunks created from a generated document."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.markdown_chunker import (

    chunk_markdown_file,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

DOCUMENT_ID = "MAN-MX200-001"

def main() -> None:

    """Load one generated document, chunk it, and print chunk details."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == DOCUMENT_ID

    )

    document_path = DOCUMENT_DIR / f"{DOCUMENT_ID}.md"

    chunks = chunk_markdown_file(

        path=document_path,

        document=document,

    )

    print(f"Document: {document.document_id}")

    print(f"Source file: {document_path}")

    print(f"Total chunks: {len(chunks)}")

    print()

    for index, chunk in enumerate(chunks, start=1):

        print("=" * 80)

        print(f"Chunk number: {index}")

        print(f"Chunk ID: {chunk.chunk_id}")

        print(f"Section: {chunk.section_title}")

        print(f"Document type: {chunk.document_type}")

        print(f"Machine models: {chunk.machine_models}")

        print(f"Revision: {chunk.revision}")

        print(f"Language: {chunk.language}")

        print(f"Characters: {len(chunk.text)}")

        print()

        print("Heading path:")

        print(" > ".join(chunk.heading_path))

        print()

        print("Chunk text:")

        print("-" * 80)

        print(chunk.text)

        print()

        print("Embedding text:")

        print("-" * 80)

        print(chunk.embedding_text)

        print()

if __name__ == "__main__":

    main()
