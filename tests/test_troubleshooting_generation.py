"""Tests for synthetic troubleshooting-guide generation."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.document_generation.troubleshooting import (

    generate_troubleshooting_markdown,

)

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def generate_guide(document_id: str) -> str:

    """Generate one troubleshooting guide by document ID."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == document_id

    )

    return generate_troubleshooting_markdown(

        repository=repository,

        document=document,

    )

def test_mx200_guide_contains_hydraulic_alarm() -> None:

    markdown = generate_guide("TSG-MX200-001")

    assert "HX-417" in markdown

    assert "Hydraulic Pressure Below Operating Threshold" in markdown

    assert "Low hydraulic fluid level" in markdown

def test_mx200_guide_contains_filter_alarm() -> None:

    markdown = generate_guide("TSG-MX200-001")

    assert "HX-421" in markdown

    assert "Return Filter Differential Pressure High" in markdown

def test_mx200_guide_contains_safety_alarm() -> None:

    markdown = generate_guide("TSG-MX200-001")

    assert "SF-101" in markdown

    assert "Safety Circuit Not Ready" in markdown

def test_troubleshooting_guide_contains_related_procedure() -> None:

    markdown = generate_guide("TSG-MX200-001")

    assert "SOP-MNT-001" in markdown

    assert "Hydraulic System Inspection" in markdown
