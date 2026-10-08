"""Tests for shared retrieval constraints."""

from __future__ import annotations

from datetime import date

from industrial_copilot.retrieval.constraints import (

    RetrievalConstraints,

    chunk_matches_constraints,

)

from industrial_copilot.retrieval.models import Chunk

def make_chunk(

    *,

    document_id: str = "DOC-001",

    machine_models: list[str] | None = None,

    alarm_codes: list[str] | None = None,

    part_numbers: list[str] | None = None,

) -> Chunk:

    return Chunk(

        chunk_id="test-chunk",

        text="Test content.",

        document_id=document_id,

        document_type="test",

        machine_models=machine_models or ["MX-200"],

        section_title="Test Section",

        heading_path=["Test Section"],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        alarm_codes=alarm_codes or [],

        part_numbers=part_numbers or [],

        embedding_text="Test content.",

    )

def test_chunk_matches_machine_model_constraint() -> None:

    chunk = make_chunk(

        machine_models=["MX-200", "MX-220"],

    )

    constraints = RetrievalConstraints(

        machine_model="MX-220",

    )

    assert chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_rejects_wrong_machine_model() -> None:

    chunk = make_chunk(

        machine_models=["MX-200"],

    )

    constraints = RetrievalConstraints(

        machine_model="MX-300",

    )

    assert not chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_matches_alarm_constraint() -> None:

    chunk = make_chunk(

        alarm_codes=["HX-417"],

    )

    constraints = RetrievalConstraints(

        alarm_code="HX-417",

    )

    assert chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_matches_procedure_constraint() -> None:

    chunk = make_chunk(

        document_id="SOP-MNT-002",

    )

    constraints = RetrievalConstraints(

        procedure_id="SOP-MNT-002",

    )

    assert chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_matches_part_number_constraint() -> None:

    chunk = make_chunk(

        part_numbers=["HF-300-R10"],

    )

    constraints = RetrievalConstraints(

        part_number="HF-300-R10",

    )

    assert chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_matches_spare_parts_constraint() -> None:

    chunk = make_chunk(

        part_numbers=["HF-300-R10"],

    )

    constraints = RetrievalConstraints(

        contains_spare_parts=True,

    )

    assert chunk_matches_constraints(

        chunk,

        constraints,

    )

def test_chunk_requires_all_constraints_to_match() -> None:

    chunk = make_chunk(

        machine_models=["MX-300"],

        part_numbers=["HF-300-R10"],

    )

    constraints = RetrievalConstraints(

        machine_model="MX-200",

        contains_spare_parts=True,

    )

    assert not chunk_matches_constraints(

        chunk,

        constraints,

    )
