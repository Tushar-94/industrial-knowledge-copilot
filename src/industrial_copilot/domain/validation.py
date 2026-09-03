
"""Cross-file validation for NovaTech canonical data."""

from __future__ import annotations

from collections import Counter

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

def _find_duplicates(values: list[str]) -> list[str]:

    """Return sorted values that occur more than once."""

    counts = Counter(values)

    return sorted(

        value

        for value, count in counts.items()

        if count > 1

    )

def validate_canonical_relationships(

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

    """Validate uniqueness and references across canonical datasets."""

    errors: list[str] = []

    plant_ids = [plant.plant_id for plant in plants.plants]

    model_ids = [

        machine_model.model_id

        for machine_model in machine_models.machine_models

    ]

    machine_ids = [

        machine.machine_id

        for machine in machines.machines

    ]

    component_ids = [

        component.component_id

        for component in components.components

    ]

    maintenance_rule_ids = [

        rule.rule_id

        for rule in maintenance_rules.maintenance_rules

    ]

    alarm_codes = [

        alarm.alarm_code

        for alarm in alarms.alarms

    ]

    part_numbers = [

        part.part_number

        for part in parts.parts

    ]

    procedure_ids = [

        procedure.procedure_id

        for procedure in procedures.procedures

    ]

    document_ids = [

        document.document_id

        for document in documents.documents

    ]

    duplicate_groups = {

        "plant IDs": _find_duplicates(plant_ids),

        "machine-model IDs": _find_duplicates(model_ids),

        "machine IDs": _find_duplicates(machine_ids),

        "component IDs": _find_duplicates(component_ids),

        "maintenance-rule IDs": _find_duplicates(

            maintenance_rule_ids

        ),

        "alarm codes": _find_duplicates(alarm_codes),

        "part numbers": _find_duplicates(part_numbers),

        "procedure IDs": _find_duplicates(procedure_ids),

        "document IDs": _find_duplicates(document_ids),

    }

    for label, duplicates in duplicate_groups.items():

        if duplicates:

            errors.append(

                f"Duplicate {label}: {', '.join(duplicates)}"

            )

    known_plant_ids = set(plant_ids)

    known_model_ids = set(model_ids)

    known_component_ids = set(component_ids)

    known_rule_ids = set(maintenance_rule_ids)

    known_alarm_codes = set(alarm_codes)

    known_part_numbers = set(part_numbers)

    known_procedure_ids = set(procedure_ids)

    component_by_id = {

        component.component_id: component

        for component in components.components

    }

    for machine in machines.machines:

        if machine.plant_id not in known_plant_ids:

            errors.append(

                f"Machine {machine.machine_id} references unknown plant "

                f"{machine.plant_id}."

            )

        if machine.model_id not in known_model_ids:

            errors.append(

                f"Machine {machine.machine_id} references unknown model "

                f"{machine.model_id}."

            )

        expected_line_prefix = f"{machine.plant_id}-L"

        if not machine.production_line.startswith(

            expected_line_prefix

        ):

            errors.append(

                f"Machine {machine.machine_id} has production line "

                f"{machine.production_line}, which does not match plant "

                f"{machine.plant_id}."

            )

    for component in components.components:

        unknown_models = sorted(

            set(component.applicable_models) - known_model_ids

        )

        if unknown_models:

            errors.append(

                f"Component {component.component_id} references unknown "

                f"models: {', '.join(unknown_models)}."

            )

    for rule in maintenance_rules.maintenance_rules:

        if rule.model_id not in known_model_ids:

            errors.append(

                f"Maintenance rule {rule.rule_id} references unknown "

                f"model {rule.model_id}."

            )

        if rule.component_id not in known_component_ids:

            errors.append(

                f"Maintenance rule {rule.rule_id} references unknown "

                f"component {rule.component_id}."

            )

        else:

            component = component_by_id[rule.component_id]

            if rule.model_id not in component.applicable_models:

                errors.append(

                    f"Maintenance rule {rule.rule_id} applies model "

                    f"{rule.model_id} to incompatible component "

                    f"{rule.component_id}."

                )

        if (

            rule.related_procedure_id is not None

            and rule.related_procedure_id not in known_procedure_ids

        ):

            errors.append(

                f"Maintenance rule {rule.rule_id} references unknown "

                f"procedure {rule.related_procedure_id}."

            )

    for alarm in alarms.alarms:

        unknown_models = sorted(

            set(alarm.applicable_models) - known_model_ids

        )

        if unknown_models:

            errors.append(

                f"Alarm {alarm.alarm_code} references unknown models: "

                f"{', '.join(unknown_models)}."

            )

        unknown_procedures = sorted(

            set(alarm.related_procedure_ids)

            - known_procedure_ids

        )

        if unknown_procedures:

            errors.append(

                f"Alarm {alarm.alarm_code} references unknown "

                f"procedures: {', '.join(unknown_procedures)}."

            )

    for part in parts.parts:

        if part.component_id not in known_component_ids:

            errors.append(

                f"Part {part.part_number} references unknown component "

                f"{part.component_id}."

            )

            continue

        unknown_models = sorted(

            set(part.compatible_models) - known_model_ids

        )

        if unknown_models:

            errors.append(

                f"Part {part.part_number} references unknown models: "

                f"{', '.join(unknown_models)}."

            )

        component = component_by_id[part.component_id]

        incompatible_models = sorted(

            set(part.compatible_models)

            - set(component.applicable_models)

        )

        if incompatible_models:

            errors.append(

                f"Part {part.part_number} uses incompatible models for "

                f"component {part.component_id}: "

                f"{', '.join(incompatible_models)}."

            )

    for procedure in procedures.procedures:

        unknown_models = sorted(

            set(procedure.applicable_models) - known_model_ids

        )

        if unknown_models:

            errors.append(

                f"Procedure {procedure.procedure_id} references unknown "

                f"models: {', '.join(unknown_models)}."

            )

        unknown_components = sorted(

            set(procedure.applicable_components)

            - known_component_ids

        )

        if unknown_components:

            errors.append(

                f"Procedure {procedure.procedure_id} references unknown "

                f"components: {', '.join(unknown_components)}."

            )

    valid_source_entity_ids = (

        known_model_ids

        | known_rule_ids

        | known_alarm_codes

        | known_part_numbers

        | known_procedure_ids

    )

    procedures_by_id = {

        procedure.procedure_id: procedure

        for procedure in procedures.procedures

    }

    for document in documents.documents:

        unknown_models = sorted(

            set(document.model_ids) - known_model_ids

        )

        if unknown_models:

            errors.append(

                f"Document {document.document_id} references unknown "

                f"models: {', '.join(unknown_models)}."

            )

        unknown_procedures = sorted(

            set(document.procedure_ids)

            - known_procedure_ids

        )

        if unknown_procedures:

            errors.append(

                f"Document {document.document_id} references unknown "

                f"procedures: {', '.join(unknown_procedures)}."

            )

        unknown_source_entities = sorted(

            set(document.source_entity_ids)

            - valid_source_entity_ids

        )

        if unknown_source_entities:

            errors.append(

                f"Document {document.document_id} references unknown "

                f"source entities: "

                f"{', '.join(unknown_source_entities)}."

            )

        if (

            document.document_type.value

            == "standard_operating_procedure"

        ):

            for procedure_id in document.procedure_ids:

                procedure = procedures_by_id.get(

                    procedure_id

                )

                if procedure is None:

                    continue

                document_models = set(

                    document.model_ids

                )

                procedure_models = set(

                    procedure.applicable_models

                )

                if document_models != procedure_models:

                    errors.append(

                        f"Document {document.document_id} model scope "

                        f"does not match procedure {procedure_id}: "

                        f"document models="

                        f"{sorted(document_models)}, "

                        f"procedure models="

                        f"{sorted(procedure_models)}."

                    )       

    if errors:

        formatted_errors = "\n".join(

            f"- {error}"

            for error in errors

        )

        raise ValueError(

            "Canonical relationship validation failed:\n"

            f"{formatted_errors}"

        )

