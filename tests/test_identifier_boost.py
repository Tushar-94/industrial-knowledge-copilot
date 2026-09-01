"""Tests for exact-identifier score boosting."""

from __future__ import annotations

from datetime import date

from industrial_copilot.retrieval.hybrid import (

    HybridSearchResult,

)

from industrial_copilot.retrieval.identifier_boost import (

    boost_exact_identifiers,

)

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.retrieval.query_analyzer import (

    analyze_query,

)

def make_chunk(

    *,

    chunk_id: str,

    section_title: str,

    text: str,

) -> Chunk:

    return Chunk(

        chunk_id=chunk_id,

        text=text,

        document_id="DOC",

        document_type="test",

        machine_models=["MX-300"],

        section_title=section_title,

        heading_path=["Test", section_title],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        embedding_text=text,

    )

def test_exact_alarm_identifier_is_boosted() -> None:

    generic = HybridSearchResult(

        chunk=make_chunk(

            chunk_id="generic",

            section_title="Alarm Response Principles",

            text="General alarm guidance.",

        ),

        score=0.04,

    )

    exact = HybridSearchResult(

        chunk=make_chunk(

            chunk_id="exact",

            section_title="HX-417 — Low Hydraulic Pressure",

            text="HX-417 indicates low hydraulic pressure.",

        ),

        score=0.03,

    )

    analysis = analyze_query(

        "What does HX-417 mean?"

    )

    results = boost_exact_identifiers(

        results=[generic, exact],

        analysis=analysis,

    )

    assert results[0].chunk.chunk_id == "exact"

def test_machine_model_alone_is_not_boosted() -> None:

    first = HybridSearchResult(

        chunk=make_chunk(

            chunk_id="first",

            section_title="General Information",

            text="Information for MX-300.",

        ),

        score=0.04,

    )

    second = HybridSearchResult(

        chunk=make_chunk(

            chunk_id="second",

            section_title="Other Information",

            text="More information for MX-300.",

        ),

        score=0.03,

    )

    analysis = analyze_query(

        "Tell me about MX-300."

    )

    results = boost_exact_identifiers(

        results=[first, second],

        analysis=analysis,

    )

    assert results[0].chunk.chunk_id == "first"
