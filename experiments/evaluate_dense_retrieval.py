"""Evaluate dense semantic retrieval over the complete corpus."""

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

    evaluate_case,

    hit_at_k,

    mean_reciprocal_rank,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

from industrial_copilot.retrieval.embedder import Embedder

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def main() -> None:

    """Run and print the dense-retrieval benchmark."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    embedder = Embedder()

    chunk_embeddings = embedder.embed_chunks(chunks)

    case_results: list[CaseResult] = []

    for case in RETRIEVAL_BENCHMARK:

        query_embedding = embedder.embed_query(

            case.query

        )

        result = evaluate_case(

            case=case,

            chunks=chunks,

            chunk_embeddings=chunk_embeddings,

            query_embedding=query_embedding,

            top_k=5,

        )

        case_results.append(result)

        rank_display = (

            str(result.first_relevant_rank)

            if result.first_relevant_rank is not None

            else "MISS"

        )

        status = (

            "PASS"

            if result.first_relevant_rank is not None

            else "FAIL"

        )

        print(

            f"{status:<4} | "

            f"{case.case_id:<15} | "

            f"rank={rank_display:<4} | "

            f"{case.query}"

        )

    print()

    print("=" * 80)

    print("Dense Retrieval Baseline")

    print("=" * 80)

    print(f"Cases: {len(case_results)}")

    print(f"Hit@1: {hit_at_k(case_results, 1):.3f}")

    print(f"Hit@3: {hit_at_k(case_results, 3):.3f}")

    print(f"Hit@5: {hit_at_k(case_results, 5):.3f}")

    print(

        "MRR:   "

        f"{mean_reciprocal_rank(case_results):.3f}"

    )

    category_results: dict[str, list[CaseResult]] = defaultdict(list)

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

    failures = [

        result

        for result in case_results

        if result.first_relevant_rank is None

    ]

    if failures:

        print()

        print("Failures")

        print("-" * 80)

        for failure in failures:

            print()

            print(

                f"{failure.case.case_id}: "

                f"{failure.case.query}"

            )

            print("Expected evidence:")

            for expected in failure.case.expected_evidence:

                print(

                    f"  - {expected.document_id} | "

                    f"{expected.section_contains}"

                )

            for rank, search_result in enumerate(

                failure.results,

                start=1,

            ):

                print(

                    f"  {rank}. "

                    f"{search_result.score:.4f} | "

                    f"{search_result.chunk.document_id} | "

                    f"{search_result.chunk.section_title}"

                )

if __name__ == "__main__":

    main()
