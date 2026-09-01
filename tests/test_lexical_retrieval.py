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
