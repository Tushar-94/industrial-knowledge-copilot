"""Inspect BM25 retrieval on known dense-search failures."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

from industrial_copilot.retrieval.lexical import (

    BM25Retriever,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = (

    PROJECT_ROOT

    / "data"

    / "generated"

    / "markdown"

)

QUERIES = [

    "What does alarm HX-417 mean?",

    "What does HX-421 indicate?",

    "Which replacement filter is compatible with the MX-300?",

]

def main() -> None:

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    retriever = BM25Retriever(chunks)

    for query in QUERIES:

        print("=" * 100)

        print(f"QUERY: {query}")

        print("=" * 100)

        results = retriever.search(

            query,

            top_k=5,

        )

        for rank, result in enumerate(

            results,

            start=1,

        ):

            print(

                f"{rank}. "

                f"score={result.score:.4f} | "

                f"{result.chunk.document_id} | "

                f"{result.chunk.section_title}"

            )

        print()

if __name__ == "__main__":

    main()
