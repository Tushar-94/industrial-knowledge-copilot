"""Validate NovaTech canonical source-of-truth files."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.repository import (

    load_canonical_repository,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def main() -> None:

    """Load and validate the complete canonical dataset."""

    repository = load_canonical_repository(CANONICAL_DIR)

    print("Canonical data validation passed.")

    print(f"Plants: {len(repository.plants.plants)}")

    print(

        "Machine models: "

        f"{len(repository.machine_models.machine_models)}"

    )

    print(

        f"Physical machines: "

        f"{len(repository.machines.machines)}"

    )

    print(

        f"Components: "

        f"{len(repository.components.components)}"

    )

    print(

        "Maintenance rules: "

        f"{len(repository.maintenance_rules.maintenance_rules)}"

    )

    print(

        f"Alarm definitions: "

        f"{len(repository.alarms.alarms)}"

    )

    print(f"Spare parts: {len(repository.parts.parts)}")

    print(

        f"Procedures: "

        f"{len(repository.procedures.procedures)}"

    )

    print(

        "Document definitions: "

        f"{len(repository.documents.documents)}"

    )

if __name__ == "__main__":

    main()