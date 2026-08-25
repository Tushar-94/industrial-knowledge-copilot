"""Tests for retrieval evaluation metrics."""

from __future__ import annotations

from industrial_copilot.evaluation.benchmark import (

    ExpectedEvidence,

    RetrievalCase,

)
from industrial_copilot.evaluation.retrieval import (

    CaseResult,

    hit_at_k,

    mean_reciprocal_rank,

)

def make_result(rank: int | None) -> CaseResult:

    """Create a minimal evaluation result for metric testing."""

    case = RetrievalCase(

    case_id="test",

    category="test",

    query="test query",

    expected_evidence=(

        ExpectedEvidence(

            document_id="DOC",

            section_contains="Section",

        ),

    ),

)

    return CaseResult(

        case=case,

        first_relevant_rank=rank,

        results=[],

    )

def test_hit_at_one() -> None:

    results = [

        make_result(1),

        make_result(2),

        make_result(None),

    ]

    assert hit_at_k(results, 1) == 1 / 3

def test_hit_at_three() -> None:

    results = [

        make_result(1),

        make_result(2),

        make_result(None),

    ]

    assert hit_at_k(results, 3) == 2 / 3

def test_mean_reciprocal_rank() -> None:

    results = [

        make_result(1),

        make_result(2),

        make_result(None),

    ]

    expected = (

        1.0

        + 0.5

        + 0.0

    ) / 3

    assert mean_reciprocal_rank(results) == expected
