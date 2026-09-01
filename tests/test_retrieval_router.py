"""Tests for query-aware retrieval routing."""

from __future__ import annotations

from industrial_copilot.retrieval.router import (

    RetrievalMode,

    choose_retrieval_mode,

)

def test_alarm_code_routes_to_hybrid() -> None:

    decision = choose_retrieval_mode(

        "What does HX-417 mean?"

    )

    assert decision.mode == RetrievalMode.HYBRID

def test_procedure_id_routes_to_hybrid() -> None:

    decision = choose_retrieval_mode(

        "What does SOP-MNT-002 cover?"

    )

    assert decision.mode == RetrievalMode.HYBRID

def test_part_number_routes_to_hybrid() -> None:

    decision = choose_retrieval_mode(

        "Is HF-300-R10 compatible with MX-300?"

    )

    assert decision.mode == RetrievalMode.HYBRID

def test_machine_model_alone_does_not_force_hybrid() -> None:

    decision = choose_retrieval_mode(

        "When should the MX-300 hydraulic pump be inspected?"

    )

    assert decision.mode == RetrievalMode.DENSE

def test_semantic_query_routes_to_dense() -> None:

    decision = choose_retrieval_mode(

        "What should maintenance check if hydraulic pressure is unstable?"

    )

    assert decision.mode == RetrievalMode.DENSE

def test_parts_lookup_routes_to_hybrid() -> None:

    decision = choose_retrieval_mode(

        "Which replacement filter is compatible with the MX-300?"

    )

    assert decision.mode == RetrievalMode.HYBRID

def test_filter_maintenance_stays_dense() -> None:

    decision = choose_retrieval_mode(

        "When should the MX-300 return filter be replaced?"

    )

    assert decision.mode == RetrievalMode.DENSE
