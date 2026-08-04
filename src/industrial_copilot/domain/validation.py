"""Cross-file validation for NovaTech canonical data."""

from __future__ import annotations

from collections import Counter

from industrial_copilot.domain.models import (

    ComponentCollection,

    MachineCollection,

    MachineModelCollection,

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

) -> None:

    """Validate uniqueness and references across canonical datasets.

    Raises:

        ValueError: If duplicate identifiers or broken references are found.

    """

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

    duplicate_groups = {

        "plant IDs": _find_duplicates(plant_ids),

        "machine-model IDs": _find_duplicates(model_ids),

        "machine IDs": _find_duplicates(machine_ids),

        "component IDs": _find_duplicates(component_ids),

    }

    for label, duplicates in duplicate_groups.items():

        if duplicates:

            errors.append(

                f"Duplicate {label}: {', '.join(duplicates)}"

            )

    known_plant_ids = set(plant_ids)

    known_model_ids = set(model_ids)

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

        if not machine.production_line.startswith(expected_line_prefix):

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

    if errors:

        formatted_errors = "\n".join(

            f"- {error}"

            for error in errors

        )

        raise ValueError(

            "Canonical relationship validation failed:\n"

            f"{formatted_errors}"

        )
