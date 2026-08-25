"""Evaluation utilities for semantic retrieval."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from numpy.typing import NDArray

from industrial_copilot.evaluation.benchmark import RetrievalCase

from industrial_copilot.retrieval.in_memory import (

    SearchResult,

    search_embeddings,

)

from industrial_copilot.retrieval.models import Chunk

@dataclass(frozen=True)

class CaseResult:

    """Evaluation result for one benchmark case."""

    case: RetrievalCase

    first_relevant_rank: int | None

    results: list[SearchResult]

def _is_expected_result(

    *,

    result: SearchResult,

    case: RetrievalCase,

) -> bool:

    """Return whether a result matches any acceptable evidence."""

    for expected in case.expected_evidence:

        document_matches = (

            result.chunk.document_id

            == expected.document_id

        )

        section_matches = (

            expected.section_contains.lower()

            in result.chunk.section_title.lower()

        )

        if document_matches and section_matches:

            return True

    return False

def evaluate_case(

    *,

    case: RetrievalCase,

    chunks: list[Chunk],

    chunk_embeddings: NDArray[np.float32],

    query_embedding: NDArray[np.float32],

    top_k: int = 5,

) -> CaseResult:

    """Evaluate retrieval for one benchmark case."""

    results = search_embeddings(

        chunks=chunks,

        chunk_embeddings=chunk_embeddings,

        query_embedding=query_embedding,

        top_k=top_k,

    )

    first_relevant_rank: int | None = None

    for rank, result in enumerate(results, start=1):

        if _is_expected_result(

            result=result,

            case=case,

        ):

            first_relevant_rank = rank

            break

    return CaseResult(

        case=case,

        first_relevant_rank=first_relevant_rank,

        results=results,

    )

def hit_at_k(

    case_results: list[CaseResult],

    k: int,

) -> float:

    """Return the fraction of cases with expected evidence in top-k."""

    hits = sum(

        1

        for result in case_results

        if (

            result.first_relevant_rank is not None

            and result.first_relevant_rank <= k

        )

    )

    return hits / len(case_results)

def mean_reciprocal_rank(

    case_results: list[CaseResult],

) -> float:

    """Return mean reciprocal rank across evaluation cases."""

    reciprocal_ranks = [

        (

            1.0 / result.first_relevant_rank

            if result.first_relevant_rank is not None

            else 0.0

        )

        for result in case_results

    ]

    return sum(reciprocal_ranks) / len(reciprocal_ranks)
