"""Evaluate hybrid dense + BM25 retrieval over the complete corpus."""

from __future__ import annotations

from collections import defaultdict

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.evaluation.benchmark import (

    RETRIEVAL_BENCHMARK,

)

from industrial_copilot.evaluation.retrieval import (

    CaseResult,

    hit_at_k,

    mean_reciprocal_rank,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

from industrial_copilot.retrieval.embedder import Embedder

from industrial_copilot.retrieval.hybrid_retriever import (

    HybridRetriever,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def is_expected_result(result, case) -> bool:

    """Return whether a hybrid result matches valid benchmark evidence."""

    for expected in case.expected_evidence:

        if (

            result.chunk.document_id == expected.document_id

            and expected.section_contains.lower()

            in result.chunk.section_title.lower()

        ):

            return True

    return False

def main() -> None:

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    embedder = Embedder()

    chunk_embeddings = embedder.embed_chunks(chunks)

    retriever = HybridRetriever(

        chunks=chunks,

        chunk_embeddings=chunk_embeddings,

    )

    case_results: list[CaseResult] = []

    for case in RETRIEVAL_BENCHMARK:

        query_embedding = embedder.embed_query(

            case.query

        )

        results = retriever.search(

            query=case.query,

            query_embedding=query_embedding,

            top_k=5,

        )

        first_relevant_rank = None

        for rank, result in enumerate(

            results,

            start=1,

        ):

            if is_expected_result(

                result,

                case,

            ):

                first_relevant_rank = rank

                break

        case_results.append(

            CaseResult(

                case=case,

                first_relevant_rank=first_relevant_rank,

                results=[],

            )

        )

        status = (

            "PASS"

            if first_relevant_rank is not None

            else "FAIL"

        )

        rank_display = (

            str(first_relevant_rank)

            if first_relevant_rank is not None

            else "MISS"

        )

        print(

            f"{status:<4} | "

            f"{case.case_id:<15} | "

            f"rank={rank_display:<4} | "

            f"{case.query}"

        )

    print()

    print("=" * 80)

    print("Hybrid Retrieval")

    print("=" * 80)

    print(f"Cases: {len(case_results)}")

    print(f"Hit@1: {hit_at_k(case_results, 1):.3f}")

    print(f"Hit@3: {hit_at_k(case_results, 3):.3f}")

    print(f"Hit@5: {hit_at_k(case_results, 5):.3f}")

    print(

        f"MRR:   "

        f"{mean_reciprocal_rank(case_results):.3f}"

    )

    category_results = defaultdict(list)

    for result in case_results:

        category_results[

            result.case.category

        ].append(result)

    print()

    print("Hit@5 by category")

    print("-" * 80)

    for category, results in sorted(

        category_results.items()

    ):

        print(

            f"{category:<20} "

            f"{hit_at_k(results, 5):.3f}"

        )

if __name__ == "__main__":

    main()
