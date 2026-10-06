"""Tests for Qdrant-backed hybrid retrieval."""

from __future__ import annotations

from datetime import date

import numpy as np

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.retrieval.query_analyzer import analyze_query

from industrial_copilot.vector_store.retriever import QdrantSearchResult

def make_chunk(

    *,

    chunk_id: str,

    text: str,

    machine_models: list[str] | None = None,

) -> Chunk:

    return Chunk(

        chunk_id=chunk_id,

        text=text,

        document_id="DOC-001",

        document_type="test",

        machine_models=machine_models or ["MX-200"],

        section_title="Test Section",

        heading_path=["Test Section"],

        revision="1.0",

        effective_date=date(2026, 1, 1),

        language="en",

        embedding_text=text,

    )

def make_qdrant_result(

    *,

    chunk_id: str,

    score: float,

) -> QdrantSearchResult:

    return QdrantSearchResult(

        point_id="point-1",

        score=score,

        chunk_id=chunk_id,

        document_id="DOC-001",

        document_type="test",

        machine_models=["MX-200"],

        section_title="Test Section",

        heading_path=["Test Section"],

        revision="1.0",

        effective_date="2026-01-01",

        language="en",

        text="HX-417 indicates low hydraulic pressure.",

    )

def test_hybrid_retriever_uses_qdrant_dense_results(

    monkeypatch,

) -> None:

    from industrial_copilot.retrieval import hybrid_retriever

    exact = make_chunk(

        chunk_id="exact",

        text="HX-417 indicates low hydraulic pressure.",

    )

    generic = make_chunk(

        chunk_id="generic",

        text="General alarm troubleshooting guidance.",

    )

    chunks = [exact, generic]

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return [

            make_qdrant_result(

                chunk_id="exact",

                score=0.8,

            )

        ]

    monkeypatch.setattr(

        hybrid_retriever,

        "search_qdrant",

        fake_search_qdrant,

    )

    retriever = hybrid_retriever.HybridRetriever(

        chunks=chunks,

        client=object(),

    )

    analysis = analyze_query(

        "What does HX-417 mean on MX-200?"

    )

    results = retriever.search(

        query="What does HX-417 mean on MX-200?",

        query_embedding=np.array(

            [0.1, 0.2, 0.3],

            dtype=np.float32,

        ),

        analysis=analysis,

        top_k=2,

        candidate_k=2,

    )

    assert captured["machine_model"] == "MX-200"

    assert captured["alarm_code"] == "HX-417"

    assert results[0].chunk.chunk_id == "exact"
