"""Repository for loading NovaTech canonical source-of-truth data."""

from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from industrial_copilot.domain.loader import load_yaml_model

from industrial_copilot.domain.models import (

    AlarmCollection,

    ComponentCollection,

    DocumentCollection,

    MachineCollection,

    MachineModelCollection,

    MaintenanceRuleCollection,

    PlantCollection,

    ProcedureCollection,

    SparePartCollection,

)

from industrial_copilot.domain.validation import (

    validate_canonical_relationships,

)

@dataclass(frozen=True)

class CanonicalRepository:

    """Validated in-memory representation of canonical NovaTech data."""

    plants: PlantCollection

    machine_models: MachineModelCollection

    machines: MachineCollection

    components: ComponentCollection

    maintenance_rules: MaintenanceRuleCollection

    alarms: AlarmCollection

    parts: SparePartCollection

    procedures: ProcedureCollection

    documents: DocumentCollection

def load_canonical_repository(

    canonical_dir: Path,

) -> CanonicalRepository:

    """Load and validate the complete canonical dataset."""

    repository = CanonicalRepository(

        plants=load_yaml_model(

            canonical_dir / "plants.yaml",

            PlantCollection,

        ),

        machine_models=load_yaml_model(

            canonical_dir / "machine_models.yaml",

            MachineModelCollection,

        ),

        machines=load_yaml_model(

            canonical_dir / "machines.yaml",

            MachineCollection,

        ),

        components=load_yaml_model(

            canonical_dir / "components.yaml",

            ComponentCollection,

        ),

        maintenance_rules=load_yaml_model(

            canonical_dir / "maintenance_rules.yaml",

            MaintenanceRuleCollection,

        ),

        alarms=load_yaml_model(

            canonical_dir / "alarms.yaml",

            AlarmCollection,

        ),

        parts=load_yaml_model(

            canonical_dir / "parts.yaml",

            SparePartCollection,

        ),

        procedures=load_yaml_model(

            canonical_dir / "procedures.yaml",

            ProcedureCollection,

        ),

        documents=load_yaml_model(

            canonical_dir / "documents.yaml",

            DocumentCollection,

        ),

    )

    validate_canonical_relationships(

        plants=repository.plants,

        machine_models=repository.machine_models,

        machines=repository.machines,

        components=repository.components,

        maintenance_rules=repository.maintenance_rules,

        alarms=repository.alarms,

        parts=repository.parts,

        procedures=repository.procedures,

        documents=repository.documents,

    )

    return repository
