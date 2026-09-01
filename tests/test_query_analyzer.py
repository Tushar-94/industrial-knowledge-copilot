"""Tests for deterministic query analysis."""

from __future__ import annotations

from industrial_copilot.retrieval.query_analyzer import (

    QueryIntent,

    analyze_query,

)

def test_extracts_alarm_code() -> None:

    analysis = analyze_query(

        "What does HX-417 mean?"

    )

    assert analysis.alarm_codes == ["HX-417"]

    assert analysis.has_identifier is True

def test_extracts_machine_model() -> None:

    analysis = analyze_query(

        "Show maintenance information for MX-300."

    )

    assert analysis.machine_models == ["MX-300"]

def test_extracts_alarm_and_machine_model() -> None:

    analysis = analyze_query(

        "What does HX-421 mean on MX-220?"

    )

    assert analysis.alarm_codes == ["HX-421"]

    assert analysis.machine_models == ["MX-220"]

def test_extracts_procedure_id() -> None:

    analysis = analyze_query(

        "What does SOP-MNT-002 cover?"

    )

    assert analysis.procedure_ids == ["SOP-MNT-002"]

def test_extracts_part_number() -> None:

    analysis = analyze_query(

        "Is HF-300-R10 compatible with MX-300?"

    )

    assert analysis.part_numbers == ["HF-300-R10"]

    assert analysis.machine_models == ["MX-300"]

def test_normalizes_identifiers_to_uppercase() -> None:

    analysis = analyze_query(

        "what does hx-417 mean on mx-300?"

    )

    assert analysis.alarm_codes == ["HX-417"]

    assert analysis.machine_models == ["MX-300"]

def test_semantic_query_has_no_identifier() -> None:

    analysis = analyze_query(

        "How often should the hydraulic pump be inspected?"

    )

    assert analysis.has_identifier is False

def test_duplicate_identifiers_are_removed() -> None:

    analysis = analyze_query(

        "Compare HX-417 with hx-417."

    )

    assert analysis.alarm_codes == ["HX-417"]

def test_detects_parts_lookup_intent() -> None:

    analysis = analyze_query(

        "Which replacement filter is compatible with the MX-300?"

    )

    assert analysis.intent == QueryIntent.PARTS_LOOKUP

def test_part_number_query_is_parts_lookup() -> None:

    analysis = analyze_query(

        "What spare part should I order for MX-300?"

    )

    assert analysis.intent == QueryIntent.PARTS_LOOKUP

def test_maintenance_filter_query_is_not_parts_lookup() -> None:

    analysis = analyze_query(

        "When should the MX-300 return filter be replaced?"

    )

    assert analysis.intent == QueryIntent.GENERAL
