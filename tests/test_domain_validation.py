
"""Tests for canonical-domain loading and relationship validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from pydantic import ValidationError

from industrial_copilot.domain.loader import load_yaml_model

from industrial_copilot.domain.models import (

    AlarmCollection,

    ComponentCollection,

    DocumentCollection,

    MachineCollection,

    MachineModel,

    MachineModelCollection,

    MaintenanceRuleCollection,

    PlantCollection,

    ProcedureCollection,

    SparePartCollection,

)

from industrial_copilot.domain.validation import (

    validate_canonical_relationships,

)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DIR = PROJECT_ROOT / "data" / "canonical"

def load_valid_collections() -> tuple[

    PlantCollection,

    MachineModelCollection,

    MachineCollection,

    ComponentCollection,

    MaintenanceRuleCollection,

    AlarmCollection,

    SparePartCollection,

    ProcedureCollection,

    DocumentCollection,

]:

    """Load all valid canonical source-of-truth collections."""

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

    return (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    )

def validate_all(

    *,

    plants: PlantCollection,

    machine_models: MachineModelCollection,

    machines: MachineCollection,

    components: ComponentCollection,

    maintenance_rules: MaintenanceRuleCollection,

    alarms: AlarmCollection,

    parts: SparePartCollection,

    procedures: ProcedureCollection,

    documents: DocumentCollection,

) -> None:

    """Call the complete relationship validator."""

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

def test_valid_canonical_data_passes_relationship_validation() -> None:

    collections = load_valid_collections()

    validate_all(

        plants=collections[0],

        machine_models=collections[1],

        machines=collections[2],

        components=collections[3],

        maintenance_rules=collections[4],

        alarms=collections[5],

        parts=collections[6],

        procedures=collections[7],

        documents=collections[8],

    )

def test_negative_pressure_is_rejected() -> None:

    invalid_model = {

        "model_id": "MX-999",

        "manufacturer": "NovaTech",

        "machine_type": "hydraulic_forming_press",

        "rated_force_kn": 2000,

        "max_hydraulic_pressure_bar": -210,

        "reservoir_capacity_l": 420,

        "motor_power_kw": 45,

        "nominal_cycle_time_s": 18,

        "supported_since": "2022-01-01",

    }

    with pytest.raises(ValidationError):

        MachineModel.model_validate(invalid_model)

def test_unknown_machine_model_is_rejected() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_machine = machines.machines[0].model_copy(

        update={"model_id": "MX-999"}

    )

    invalid_machines = MachineCollection(

        machines=[invalid_machine, *machines.machines[1:]]

    )

    with pytest.raises(

        ValueError,

        match="references unknown model MX-999",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=invalid_machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=parts,

            procedures=procedures,

            documents=documents,

        )

def test_machine_line_must_match_plant() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_machine = machines.machines[0].model_copy(

        update={"production_line": "HAM-L9"}

    )

    invalid_machines = MachineCollection(

        machines=[invalid_machine, *machines.machines[1:]]

    )

    with pytest.raises(

        ValueError,

        match="does not match plant BER",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=invalid_machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=parts,

            procedures=procedures,

            documents=documents,

        )

def test_maintenance_rule_requires_a_trigger() -> None:

    invalid_rule = {

        "rule_id": "MR-MX200-TEST",

        "model_id": "MX-200",

        "component_id": "HYD_RETURN_FILTER",

        "maintenance_action": "replace",

        "interval_operating_hours": None,

        "interval_months": None,

        "condition_trigger": None,

        "severity_if_overdue": "high",

        "related_procedure_id": "SOP-MNT-002",

    }

    with pytest.raises(

        ValidationError,

        match="requires at least one interval",

    ):

        MaintenanceRuleCollection.model_validate(

            {"maintenance_rules": [invalid_rule]}

        )

def test_unknown_rule_component_is_rejected() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_rule = maintenance_rules.maintenance_rules[0].model_copy(

        update={"component_id": "UNKNOWN_COMPONENT"}

    )

    invalid_rules = MaintenanceRuleCollection(

        maintenance_rules=[

            invalid_rule,

            *maintenance_rules.maintenance_rules[1:],

        ]

    )

    with pytest.raises(

        ValueError,

        match="references unknown component UNKNOWN_COMPONENT",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=machines,

            components=components,

            maintenance_rules=invalid_rules,

            alarms=alarms,

            parts=parts,

            procedures=procedures,

            documents=documents,

        )

def test_unknown_part_component_is_rejected() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_part = parts.parts[0].model_copy(

        update={"component_id": "UNKNOWN_COMPONENT"}

    )

    invalid_parts = SparePartCollection(

        parts=[invalid_part, *parts.parts[1:]]

    )

    with pytest.raises(

        ValueError,

        match="references unknown component UNKNOWN_COMPONENT",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=invalid_parts,

            procedures=procedures,

            documents=documents,

        )

def test_unknown_procedure_component_is_rejected() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_procedure = procedures.procedures[0].model_copy(

        update={"applicable_components": ["UNKNOWN_COMPONENT"]}

    )

    invalid_procedures = ProcedureCollection(

        procedures=[

            invalid_procedure,

            *procedures.procedures[1:],

        ]

    )

    with pytest.raises(

        ValueError,

        match="references unknown components: UNKNOWN_COMPONENT",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=parts,

            procedures=invalid_procedures,

            documents=documents,

        )

def test_document_unknown_source_entity_is_rejected() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    invalid_document = documents.documents[0].model_copy(

        update={

            "source_entity_ids": [

                *documents.documents[0].source_entity_ids,

                "UNKNOWN-ENTITY",

            ]

        }

    )

    invalid_documents = DocumentCollection(

        documents=[

            invalid_document,

            *documents.documents[1:],

        ]

    )

    with pytest.raises(

        ValueError,

        match="references unknown source entities: UNKNOWN-ENTITY",

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=parts,

            procedures=procedures,

            documents=invalid_documents,

        )

def test_sop_document_model_scope_must_match_procedure() -> None:

    (

        plants,

        machine_models,

        machines,

        components,

        maintenance_rules,

        alarms,

        parts,

        procedures,

        documents,

    ) = load_valid_collections()

    sop_index = next(

        index

        for index, document in enumerate(

            documents.documents

        )

        if document.document_id == "SOP-MNT-002"

    )

    sop_document = documents.documents[

        sop_index

    ]

    invalid_document = sop_document.model_copy(

        update={

            "model_ids": ["MX-200"],

        }

    )

    invalid_document_list = list(

        documents.documents

    )

    invalid_document_list[

        sop_index

    ] = invalid_document

    invalid_documents = DocumentCollection(

        documents=invalid_document_list

    )

    with pytest.raises(

        ValueError,

        match=(

            "Document SOP-MNT-002 model scope "

            "does not match procedure SOP-MNT-002"

        ),

    ):

        validate_all(

            plants=plants,

            machine_models=machine_models,

            machines=machines,

            components=components,

            maintenance_rules=maintenance_rules,

            alarms=alarms,

            parts=parts,

            procedures=procedures,

            documents=invalid_documents,

        )

