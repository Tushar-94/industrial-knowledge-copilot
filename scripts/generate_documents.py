"""Generate synthetic NovaTech technical documents."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.document_generation.manual import (

    generate_manual_markdown,

)

from industrial_copilot.document_generation.troubleshooting import (

    generate_troubleshooting_markdown,

)

from industrial_copilot.domain.models import DocumentType

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

OUTPUT_DIR = PROJECT_ROOT / "data" / "generated" / "markdown"

def main() -> None:

    """Generate all currently supported synthetic documents."""

    repository = load_canonical_repository(CANONICAL_DIR)

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    generated_count = 0

    for document in repository.documents.documents:

        if (

            document.document_type

            == DocumentType.OPERATION_MAINTENANCE_MANUAL

        ):

            markdown = generate_manual_markdown(

                repository=repository,

                document=document,

            )

        elif (

            document.document_type

            == DocumentType.TROUBLESHOOTING_GUIDE

        ):

            markdown = generate_troubleshooting_markdown(

                repository=repository,

                document=document,

            )

        else:

            continue

        output_path = OUTPUT_DIR / f"{document.document_id}.md"

        output_path.write_text(

            markdown,

            encoding="utf-8",

        )

        print(f"Generated: {output_path}")

        generated_count += 1

    print(f"\nGenerated {generated_count} manual(s).")

if __name__ == "__main__":

    main()