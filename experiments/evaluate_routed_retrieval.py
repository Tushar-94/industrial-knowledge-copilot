"""Evaluate query-routed dense/hybrid retrieval."""

from __future__ import annotations

from collections import defaultdict

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.identifier_boost import (

    boost_exact_identifiers,

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

    adapt_qdrant_results,

    build_qdrant_constraints,

)

from industrial_copilot.vector_store.client import (

    create_qdrant_client,

    ensure_collection,

)

from industrial_copilot.vector_store.retriever import (

    search_qdrant,

)

from industrial_copilot.retrieval.router import (

    RetrievalMode,

    choose_retrieval_mode,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = (

    PROJECT_ROOT

    / "data"

    / "generated"

    / "markdown"

)

def is_expected_result(result, case) -> bool:

    """Return whether a retrieved result matches acceptable evidence."""

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

    client = create_qdrant_client()

    ensure_collection(client)

    chunks_by_id = {

        chunk.chunk_id: chunk

        for chunk in chunks

    }

    hybrid_retriever = HybridRetriever(

        chunks=chunks,

        client=client,

    )

    case_results: list[CaseResult] = []

    for case in RETRIEVAL_BENCHMARK:

        query_embedding = embedder.embed_query(

            case.query

        )

        decision = choose_retrieval_mode(

            case.query

        )

        if decision.mode == RetrievalMode.HYBRID:

            hybrid_results = hybrid_retriever.search(

                query=case.query,

                query_embedding=query_embedding,

                analysis=decision.analysis,

                top_k=20,

            )

            results = boost_exact_identifiers(
                results=hybrid_results,
                analysis=decision.analysis,
            )[:5]

        else:

            constraints = build_qdrant_constraints(

                decision.analysis

            )

            qdrant_results = search_qdrant(

                client=client,

                query_embedding=query_embedding,

                top_k=5,

                machine_model=constraints.machine_model,

                alarm_code=constraints.alarm_code,

                procedure_id=constraints.procedure_id,

                part_number=constraints.part_number,

                contains_spare_parts=constraints.contains_spare_parts,

            )

            results = adapt_qdrant_results(

                qdrant_results=qdrant_results,

                chunks_by_id=chunks_by_id,

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

            f"{decision.mode.value:<6} | "

            f"{case.case_id:<15} | "

            f"rank={rank_display:<4} | "

            f"{case.query}"

        )

    print()

    print("=" * 80)

    print("Query-Routed Retrieval")

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
