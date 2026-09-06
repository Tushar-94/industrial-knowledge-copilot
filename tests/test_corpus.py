"""Tests for construction of the complete retrieval corpus."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.corpus import (

    build_markdown_corpus,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def load_corpus():

    """Load the complete generated retrieval corpus."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    return build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

def test_corpus_contains_chunks_from_all_documents() -> None:

    chunks = load_corpus()

    document_ids = {

        chunk.document_id

        for chunk in chunks

    }

    assert len(document_ids) == 12

def test_corpus_contains_manual_chunks() -> None:

    chunks = load_corpus()

    assert any(

        chunk.document_id == "MAN-MX200-001"

        for chunk in chunks

    )

def test_corpus_contains_troubleshooting_chunks() -> None:

    chunks = load_corpus()

    assert any(

        chunk.document_id == "TSG-MX200-001"

        for chunk in chunks

    )

def test_corpus_contains_sop_chunks() -> None:

    chunks = load_corpus()

    assert any(

        chunk.document_id == "SOP-MNT-002"

        for chunk in chunks

    )

def test_every_chunk_has_source_metadata() -> None:

    chunks = load_corpus()

    for chunk in chunks:

        assert chunk.document_id

        assert chunk.document_type

        assert chunk.section_title

        assert chunk.revision

        assert chunk.language

def test_alarm_chunk_contains_alarm_metadata() -> None:

    chunks = load_corpus()

    chunk = next(

        chunk

        for chunk in chunks

        if (

            chunk.document_id == "TSG-MX200-001"

            and "HX-417" in chunk.section_title

        )

    )

    assert chunk.alarm_codes == ["HX-417"]

def test_alarm_chunk_contains_related_procedure_metadata() -> None:

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    chunk = next(

        chunk

        for chunk in chunks

        if (

            chunk.document_id == "TSG-MX200-001"

            and "HX-417" in chunk.section_title

        )

    )

    alarm = next(

        alarm

        for alarm in repository.alarms.alarms

        if alarm.alarm_code == "HX-417"

    )

    assert chunk.related_procedures == sorted(

        alarm.related_procedure_ids

    )

def test_sop_chunk_contains_related_component_metadata():

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    matching = [

        chunk

        for chunk in chunks

        if (

            chunk.document_id == "SOP-MNT-002"

            and chunk.section_title == "Procedure"

        )

    ]

    assert len(matching) == 1

    assert (

        "HYD_RETURN_FILTER"

        in matching[0].related_components

    )

def test_spare_parts_chunk_contains_part_numbers():

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    chunks = build_markdown_corpus(

        repository=repository,

        document_dir=DOCUMENT_DIR,

    )

    matching = [

        chunk

        for chunk in chunks

        if (

            chunk.document_id == "SOP-MNT-002"

            and chunk.section_title

            == "Related Spare Parts"

        )

    ]

    assert len(matching) == 1

    assert set(

        matching[0].part_numbers

    ) == {

        "HF-220-R10",

        "HF-300-R10",

    }