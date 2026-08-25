"""Build a retrieval corpus from generated technical documents."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import CanonicalRepository

from industrial_copilot.retrieval.markdown_chunker import (

    chunk_markdown_file,

)

from industrial_copilot.retrieval.models import Chunk

def build_markdown_corpus(

    *,

    repository: CanonicalRepository,

    document_dir: Path,

) -> list[Chunk]:

    """Load and chunk every generated document defined in the repository."""

    chunks: list[Chunk] = []

    for document in repository.documents.documents:

        document_path = (

            document_dir

            / f"{document.document_id}.md"

        )

        if not document_path.exists():

            raise FileNotFoundError(

                "Generated document is missing: "

                f"{document_path}"

            )

        document_chunks = chunk_markdown_file(

            path=document_path,

            document=document,

        )

        chunks.extend(document_chunks)

    return chunks
