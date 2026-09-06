"""Evaluate metadata-aware Qdrant retrieval on dev and held-out benchmarks."""

from __future__ import annotations

from collections import defaultdict

from industrial_copilot.evaluation.benchmark import (

    RETRIEVAL_BENCHMARK,

    RetrievalCase,

)

from industrial_copilot.evaluation.heldout_benchmark import (

    HELDOUT_RETRIEVAL_BENCHMARK,

)

from industrial_copilot.evaluation.retrieval import (

    CaseResult,

    hit_at_k,

    mean_reciprocal_rank,

)

from industrial_copilot.retrieval.embedder import Embedder

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

)

from industrial_copilot.vector_store.query_service import (

    retrieve_query,

)

from industrial_copilot.vector_store.retriever import (

    QdrantSearchResult,

)

def is_expected_result(

    result: QdrantSearchResult,

    case: RetrievalCase,

) -> bool:

    """Return whether one Qdrant result matches acceptable evidence."""

    for expected in case.expected_evidence:

        document_matches = (

            result.document_id

            == expected.document_id

        )

        section_matches = (

            expected.section_contains.lower()

            in result.section_title.lower()

        )

        if document_matches and section_matches:

            return True

    return False

def evaluate_benchmark(

    *,

    name: str,

    benchmark: list[RetrievalCase],

    client,

    embedder: Embedder,

) -> None:

    """Evaluate one benchmark using metadata-aware Qdrant retrieval."""

    case_results: list[CaseResult] = []

    for case in benchmark:

        results = retrieve_query(

            query=case.query,

            client=client,

            embedder=embedder,

            top_k=5,

        )

        first_relevant_rank: int | None = None

        for rank, result in enumerate(

            results,

            start=1,

        ):

            if is_expected_result(

                result=result,

                case=case,

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

        if first_relevant_rank is None:

            print("     Expected:")

            for expected in case.expected_evidence:

                print(

                    "       - "

                    f"{expected.document_id} | "

                    f"{expected.section_contains}"

                )

            print("     Retrieved:")

            for rank, result in enumerate(

                results,

                start=1,

            ):

                print(

                    f"       {rank}. "

                    f"{result.score:.4f} | "

                    f"{result.document_id} | "

                    f"{result.section_title}"

                )

    print()

    print("=" * 80)

    print(name)

    print("=" * 80)

    print(

        f"Cases: {len(case_results)}"

    )

    print(

        f"Hit@1: "

        f"{hit_at_k(case_results, 1):.3f}"

    )

    print(

        f"Hit@3: "

        f"{hit_at_k(case_results, 3):.3f}"

    )

    print(

        f"Hit@5: "

        f"{hit_at_k(case_results, 5):.3f}"

    )

    print(

        "MRR:   "

        f"{mean_reciprocal_rank(case_results):.3f}"

    )

    category_results: dict[

        str,

        list[CaseResult],

    ] = defaultdict(list)

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

    print()

    print(

        f"Failures: {len(failures)}"

    )

def main() -> None:

    """Evaluate metadata-aware Qdrant retrieval."""

    client = create_qdrant_client()

    embedder = Embedder()

    print()

    print("#" * 80)

    print("DEVELOPMENT BENCHMARK")

    print("#" * 80)

    print()

    evaluate_benchmark(

        name="Metadata-Aware Qdrant Retrieval — Development",

        benchmark=RETRIEVAL_BENCHMARK,

        client=client,

        embedder=embedder,

    )

    print()

    print()

    print("#" * 80)

    print("HELD-OUT BENCHMARK")

    print("#" * 80)

    print()

    evaluate_benchmark(

        name="Metadata-Aware Qdrant Retrieval — Held-Out",

        benchmark=HELDOUT_RETRIEVAL_BENCHMARK,

        client=client,

        embedder=embedder,

    )

    client.close()

if __name__ == "__main__":

    main()
