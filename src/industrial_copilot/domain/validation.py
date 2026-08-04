
"""Cross-file validation for NovaTech canonical data."""

from __future__ import annotations

from collections import Counter

from industrial_copilot.domain.models import (

    AlarmCollection,

    ComponentCollection,

    MachineCollection,

    MachineModelCollection,

    MaintenanceRuleCollection,

    PlantCollection,

)

def _find_duplicates(values: list[str]) -> list[str]:

    """Return sorted values that appear more than once."""

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

) -> None:

    """Validate uniqueness and references across canonical datasets.

    Raises:

        ValueError: If duplicate identifiers or broken references are found.

    """

    errors: list[str] = []

    plant_ids = [

        plant.plant_id

        for plant in plants.plants

    ]

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

    duplicate_groups = {

        "plant IDs": _find_duplicates(plant_ids),

        "machine-model IDs": _find_duplicates(model_ids),

        "machine IDs": _find_duplicates(machine_ids),

        "component IDs": _find_duplicates(component_ids),

        "maintenance-rule IDs": _find_duplicates(

            maintenance_rule_ids

        ),

        "alarm codes": _find_duplicates(alarm_codes),

    }

    for label, duplicates in duplicate_groups.items():

        if duplicates:

            errors.append(

                f"Duplicate {label}: {', '.join(duplicates)}"

            )

    known_plant_ids = set(plant_ids)

    known_model_ids = set(model_ids)

    known_component_ids = set(component_ids)

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

    component_by_id = {

        component.component_id: component

        for component in components.components

    }

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

            continue

        component = component_by_id[rule.component_id]

        if rule.model_id not in component.applicable_models:

            errors.append(

                f"Maintenance rule {rule.rule_id} applies model "

                f"{rule.model_id} to incompatible component "

                f"{rule.component_id}."

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

    if errors:

        formatted_errors = "\n".join(

            f"- {error}"

            for error in errors

        )

        raise ValueError(

            "Canonical relationship validation failed:\n"

            f"{formatted_errors}"

        )

