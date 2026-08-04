
"""Validate NovaTech canonical source-of-truth files."""

from __future__ import annotations

from pathlib import Path

from industrial_copilot.domain.loader import load_yaml_model

from industrial_copilot.domain.models import (

    ComponentCollection,

    MachineCollection,

    MachineModelCollection,

    PlantCollection,

    AlarmCollection,

    MaintenanceRuleCollection,

    DocumentCollection,

    ProcedureCollection,

    SparePartCollection,

)

from industrial_copilot.domain.validation import (

    validate_canonical_relationships,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def main() -> None:

    """Load and validate the initial canonical datasets."""

    plants = load_yaml_model(

        CANONICAL_DIR / "plants.yaml",

        PlantCollection,

    )

    machine_models = load_yaml_model(

        CANONICAL_DIR / "machine_models.yaml",

        MachineModelCollection,

    )

    machines = load_yaml_model(

        CANONICAL_DIR / "machines.yaml",

        MachineCollection,

    )

    components = load_yaml_model(

        CANONICAL_DIR / "components.yaml",

        ComponentCollection,

    )

    maintenance_rules = load_yaml_model(

        CANONICAL_DIR / "maintenance_rules.yaml",

        MaintenanceRuleCollection,

    )

    alarms = load_yaml_model(

        CANONICAL_DIR / "alarms.yaml",

        AlarmCollection,

    )

    parts = load_yaml_model(

        CANONICAL_DIR / "parts.yaml",

        SparePartCollection,

    )

    procedures = load_yaml_model(

        CANONICAL_DIR / "procedures.yaml",

        ProcedureCollection,

    )

    documents = load_yaml_model(

        CANONICAL_DIR / "documents.yaml",

        DocumentCollection,

    )

    validate_canonical_relationships(

        plants=plants,

        machine_models=machine_models,

        machines=machines,

        components=components,

        maintenance_rules=maintenance_rules,

        alarms=alarms,

        parts=parts,

        procedures=procedures,

        documents=documents,

    )

    print("Canonical data validation passed.")

    print(f"Plants: {len(plants.plants)}")

    print(f"Machine models: {len(machine_models.machine_models)}")

    print(f"Physical machines: {len(machines.machines)}")

    print(f"Components: {len(components.components)}")

    print(

        f"Maintenance rules: "

        f"{len(maintenance_rules.maintenance_rules)}"

    )

    print(f"Alarm definitions: {len(alarms.alarms)}")

    print(f"Spare parts: {len(parts.parts)}")

    print(f"Procedures: {len(procedures.procedures)}")

    print(f"Document definitions: {len(documents.documents)}")

if __name__ == "__main__":

    main()

