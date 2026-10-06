"""Tests for metadata-aware Qdrant query routing."""

from __future__ import annotations

import numpy as np

from industrial_copilot.vector_store import query_service

class FakeEmbedder:

    """Minimal embedder stub for query-service tests."""

    def embed_query(

        self,

        query: str,

    ) -> np.ndarray:

        return np.array(

            [0.1, 0.2, 0.3],

            dtype=np.float32,

        )

def test_machine_model_is_forwarded_to_qdrant(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query=(

            "How often should the hydraulic pump "

            "on the MX-200 be inspected?"

        ),

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] == "MX-200"

    assert captured["alarm_code"] is None

    assert captured["contains_spare_parts"] is None

def test_alarm_code_is_forwarded_to_qdrant(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query="What does alarm HX-417 mean?",

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] is None

    assert captured["alarm_code"] == "HX-417"

def test_machine_and_alarm_are_both_forwarded(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query="What does HX-417 mean on MX-200?",

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] == "MX-200"

    assert captured["alarm_code"] == "HX-417"

def test_semantic_query_uses_no_metadata_filter(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query=(

            "Why can hydraulic pressure become "

            "unstable during operation?"

        ),

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] is None

    assert captured["alarm_code"] is None

def test_parts_lookup_forwards_spare_parts_filter(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query=(

            "Which replacement filter is compatible "

            "with the MX-300?"

        ),

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] == "MX-300"

    assert captured["alarm_code"] is None

    assert captured["contains_spare_parts"] is True

def test_procedure_id_is_forwarded_to_qdrant(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query="What does SOP-MNT-002 cover?",

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["procedure_id"] == "SOP-MNT-002"

def test_part_number_is_forwarded_to_qdrant(

    monkeypatch,

) -> None:

    captured: dict[str, object] = {}

    def fake_search_qdrant(**kwargs):

        captured.update(kwargs)

        return []

    monkeypatch.setattr(

        query_service,

        "search_qdrant",

        fake_search_qdrant,

    )

    query_service.retrieve_query(

        query=(

            "Is HF-300-R10 compatible "

            "with MX-300?"

        ),

        client=object(),

        embedder=FakeEmbedder(),

    )

    assert captured["machine_model"] == "MX-300"

    assert captured["part_number"] == "HF-300-R10"