"""Tests for structure-aware Markdown chunking."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

from industrial_copilot.retrieval.markdown_chunker import (

    chunk_markdown_file,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

DOCUMENT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def load_mx200_chunks():

    """Load chunks produced from the generated MX-200 manual."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == "MAN-MX200-001"

    )

    return chunk_markdown_file(

        path=DOCUMENT_DIR / "MAN-MX200-001.md",

        document=document,

    )

def test_mx200_manual_produces_multiple_chunks() -> None:

    chunks = load_mx200_chunks()

    assert len(chunks) > 5

def test_hydraulic_pump_section_becomes_a_chunk() -> None:

    chunks = load_mx200_chunks()

    pump_chunk = next(

        chunk

        for chunk in chunks

        if chunk.section_title == "Hydraulic Pump"

    )

    assert "2,000 operating hours" in pump_chunk.text

    assert pump_chunk.machine_models == ["MX-200"]

def test_heading_is_in_embedding_text() -> None:

    chunks = load_mx200_chunks()

    pump_chunk = next(

        chunk

        for chunk in chunks

        if chunk.section_title == "Hydraulic Pump"

    )

    assert "Section: Hydraulic Pump" in pump_chunk.embedding_text

    assert "Machine models: MX-200" in pump_chunk.embedding_text

def test_chunk_keeps_source_metadata() -> None:

    chunks = load_mx200_chunks()

    pump_chunk = next(

        chunk

        for chunk in chunks

        if chunk.section_title == "Hydraulic Pump"

    )

    assert pump_chunk.document_id == "MAN-MX200-001"

    assert pump_chunk.revision == "2.2"

    assert pump_chunk.language == "en"
