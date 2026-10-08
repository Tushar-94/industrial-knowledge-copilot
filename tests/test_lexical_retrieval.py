"""Tests for BM25 lexical retrieval utilities."""

from __future__ import annotations

from datetime import date

from industrial_copilot.retrieval.lexical import (

    BM25Retriever,

    tokenize,

)

from industrial_copilot.retrieval.models import Chunk

def make_chunk(

    *,

    chunk_id: str,

    text: str,

) -> Chunk:

    return Chunk(

        chunk_id=chunk_id,

        text=text,

        document_id="DOC-001",

        document_type="test",

        machine_models=["MX-300"],

        section_title="Test",

        heading_path=["Test", "Test"],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        embedding_text=text,

    )

def test_tokenizer_preserves_alarm_code() -> None:

    tokens = tokenize(

        "Alarm HX-421 occurred."

    )

    assert "hx-421" in tokens

def test_tokenizer_preserves_machine_model() -> None:

    tokens = tokenize(

        "The machine is MX-300."

    )

    assert "mx-300" in tokens

def test_bm25_prefers_exact_alarm_identifier() -> None:

    chunks = [

        make_chunk(

            chunk_id="1",

            text="HX-417 means low hydraulic pressure.",

        ),

        make_chunk(

            chunk_id="2",

            text="HX-421 indicates filter differential pressure.",

        ),

        make_chunk(

            chunk_id="3",

            text="Hydraulic maintenance information.",

        ),

    ]

    retriever = BM25Retriever(chunks)

    result = retriever.search(

        "What does HX-421 mean?",

        top_k=1,

    )

    assert result[0].chunk.chunk_id == "2"

def test_bm25_search_respects_eligible_chunk_ids() -> None:

    from datetime import date

    from industrial_copilot.retrieval.lexical import BM25Retriever

    from industrial_copilot.retrieval.models import Chunk

    preferred_by_text = Chunk(

        chunk_id="lexically-strong",

        text="MX-300 replacement filter replacement filter MX-300",

        document_id="DOC-001",

        document_type="test",

        machine_models=["MX-200"],

        section_title="Test Section",

        heading_path=["Test Section"],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        embedding_text=(

            "MX-300 replacement filter replacement filter MX-300"

        ),

    )

    eligible = Chunk(

        chunk_id="eligible",

        text="Replacement filter information.",

        document_id="DOC-002",

        document_type="test",

        machine_models=["MX-300"],

        section_title="Test Section",

        heading_path=["Test Section"],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        embedding_text="Replacement filter information.",

    )

    retriever = BM25Retriever(

        [preferred_by_text, eligible]

    )

    results = retriever.search(

        "MX-300 replacement filter",

        top_k=5,

        eligible_chunk_ids={"eligible"},

    )

    assert [

        result.chunk.chunk_id

        for result in results

    ] == ["eligible"]
