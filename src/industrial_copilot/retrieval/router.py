"""Query-aware retrieval routing."""

from __future__ import annotations

from dataclasses import dataclass

from enum import Enum

from industrial_copilot.retrieval.query_analyzer import (

    QueryAnalysis,

    QueryIntent,

    analyze_query,

)

class RetrievalMode(str, Enum):

    """Supported retrieval strategies."""

    DENSE = "dense"

    HYBRID = "hybrid"

@dataclass(frozen=True)

class RoutingDecision:

    """Result of analyzing which retrieval strategy to use."""

    mode: RetrievalMode

    analysis: QueryAnalysis

def choose_retrieval_mode(

    query: str,

) -> RoutingDecision:

    """Choose dense or hybrid retrieval for one query."""

    analysis = analyze_query(query)

    should_use_hybrid = (
        any(

            (

                analysis.alarm_codes,

                analysis.procedure_ids,

                analysis.part_numbers,

            )
        )
        or analysis.intent == QueryIntent.PARTS_LOOKUP
    )


    mode = (

        RetrievalMode.HYBRID

        if should_use_hybrid

        else RetrievalMode.DENSE

    )

    return RoutingDecision(

        mode=mode,

        analysis=analysis,

    )
