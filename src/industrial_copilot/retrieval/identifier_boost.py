"""Deterministic score boosts for exact industrial identifiers."""

from __future__ import annotations

from dataclasses import dataclass

from industrial_copilot.retrieval.hybrid import (

    HybridSearchResult,

)

from industrial_copilot.retrieval.query_analyzer import (

    QueryAnalysis,

)

@dataclass(frozen=True)

class BoostedSearchResult:

    """One search result after exact-identifier boosting."""

    chunk: object

    score: float

def _chunk_contains_identifier(

    *,

    identifier: str,

    result: HybridSearchResult,

) -> bool:

    """Return whether a chunk contains an identifier exactly."""

    identifier_upper = identifier.upper()

    searchable_text = " ".join(

        [

            result.chunk.section_title,

            result.chunk.text,

            result.chunk.embedding_text,

        ]

    ).upper()

    return identifier_upper in searchable_text

def boost_exact_identifiers(

    *,

    results: list[HybridSearchResult],

    analysis: QueryAnalysis,

    boost: float = 1.0,

) -> list[BoostedSearchResult]:

    """Boost chunks containing exact identifiers from the query."""

    identifiers = [

        *analysis.alarm_codes,

        *analysis.procedure_ids,

        *analysis.part_numbers,

    ]

    boosted_results: list[BoostedSearchResult] = []

    for result in results:

        exact_matches = sum(

            1

            for identifier in identifiers

            if _chunk_contains_identifier(

                identifier=identifier,

                result=result,

            )

        )

        final_score = (

            result.score

            + boost * exact_matches

        )

        boosted_results.append(

            BoostedSearchResult(

                chunk=result.chunk,

                score=final_score,

            )

        )

    return sorted(

        boosted_results,

        key=lambda result: result.score,

        reverse=True,

    )
