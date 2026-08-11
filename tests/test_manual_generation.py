"""Tests for synthetic operation and maintenance manual generation."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.document_generation.manual import (

    generate_manual_markdown,

)

from industrial_copilot.domain.models import DocumentType

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def generate_mx200_manual() -> str:

    """Generate the MX-200 manual used by document tests."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == "MAN-MX200-001"

    )

    return generate_manual_markdown(

        repository=repository,

        document=document,

    )

def generate_manual(document_id: str) -> str:

    """Generate one manual by document ID."""

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == document_id

    )

    return generate_manual_markdown(

        repository=repository,

        document=document,

    )

def test_mx220_manual_uses_mx220_values() -> None:

    markdown = generate_manual("MAN-MX220-001")

    assert "2,200 kN" in markdown

    assert "225 bar" in markdown

    assert "900 operating hours or 12 months" in markdown

def test_mx300_manual_uses_mx300_values() -> None:

    markdown = generate_manual("MAN-MX300-001")

    assert "3,000 kN" in markdown

    assert "250 bar" in markdown

    assert "750 operating hours or 10 months" in markdown

def test_mx200_manual_contains_correct_model_specifications() -> None:

    markdown = generate_mx200_manual()

    assert "2,000 kN" in markdown

    assert "210 bar" in markdown

    assert "420 L" in markdown

    assert "45 kW" in markdown

def test_mx200_manual_contains_filter_maintenance_rules() -> None:

    markdown = generate_mx200_manual()

    assert "500 operating hours" in markdown

    assert "1,000 operating hours or 12 months" in markdown

    assert "differential pressure reaches 1.5 bar" in markdown

def test_mx200_manual_contains_source_identity() -> None:

    markdown = generate_mx200_manual()

    assert "MAN-MX200-001" in markdown

    assert "MX-200" in markdown

    assert "Revision" in markdown

def test_manual_is_generated_only_for_manual_document_type() -> None:

    repository = load_canonical_repository(CANONICAL_DIR)

    document = next(

        document

        for document in repository.documents.documents

        if document.document_id == "MAN-MX200-001"

    )

    assert (

        document.document_type

        == DocumentType.OPERATION_MAINTENANCE_MANUAL

    )
