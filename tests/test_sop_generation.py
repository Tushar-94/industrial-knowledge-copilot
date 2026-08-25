"""Tests for synthetic SOP generation."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.document_generation.sop import (

    generate_sop_markdown,

)

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def generate_sop(document_id: str) -> str:

    """Generate one SOP by document ID."""

    repository = load_canonical_repository(

        CANONICAL_DIR

    )

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == document_id

    )

    return generate_sop_markdown(

        repository=repository,

        document=document,

    )

def test_filter_replacement_sop_contains_procedure_steps() -> None:

    markdown = generate_sop("SOP-MNT-002")

    assert "Hydraulic Return Filter Replacement" in markdown

    assert "Clean the exterior of the filter housing" in markdown

    assert "Remove the used filter element" in markdown

def test_filter_replacement_sop_contains_applicable_models() -> None:

    markdown = generate_sop("SOP-MNT-002")

    assert "MX-200" in markdown

    assert "MX-220" in markdown

    assert "MX-300" in markdown

def test_filter_replacement_sop_contains_related_parts() -> None:

    markdown = generate_sop("SOP-MNT-002")

    assert "HF-220-R10" in markdown

    assert "HF-300-R10" in markdown

def test_pressure_sensor_sop_contains_sensor_parts() -> None:

    markdown = generate_sop("SOP-MNT-003")

    assert "PS-210-A" in markdown

    assert "PS-225-B" in markdown

    assert "PS-250-C" in markdown

def test_safety_sop_contains_warning() -> None:

    markdown = generate_sop("SOP-HSE-001")

    assert "WARNING" in markdown

    assert "hazardous-energy isolation" in markdown.lower()
