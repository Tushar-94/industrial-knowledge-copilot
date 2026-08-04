"""Tests for canonical-domain loading and relationship validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from pydantic import ValidationError

from industrial_copilot.domain.loader import load_yaml_model

from industrial_copilot.domain.models import (

    ComponentCollection,

    MachineCollection,

    MachineModel,

    MachineModelCollection,

    PlantCollection,

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

]:

    """Load the valid canonical fixture files."""

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

    return plants, machine_models, machines, components

def test_valid_canonical_data_passes_relationship_validation() -> None:

    plants, machine_models, machines, components = (

        load_valid_collections()

    )

    validate_canonical_relationships(

        plants=plants,

        machine_models=machine_models,

        machines=machines,

        components=components,

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

    plants, machine_models, machines, components = (

        load_valid_collections()

    )

    invalid_machine = machines.machines[0].model_copy(

        update={"model_id": "MX-999"}

    )

    invalid_machines = MachineCollection(

        machines=[

            invalid_machine,

            *machines.machines[1:],

        ]

    )

    with pytest.raises(

        ValueError,

        match="references unknown model MX-999",

    ):

        validate_canonical_relationships(

            plants=plants,

            machine_models=machine_models,

            machines=invalid_machines,

            components=components,

        )

def test_machine_line_must_match_plant() -> None:

    plants, machine_models, machines, components = (

        load_valid_collections()

    )

    invalid_machine = machines.machines[0].model_copy(

        update={"production_line": "HAM-L9"}

    )

    invalid_machines = MachineCollection(

        machines=[

            invalid_machine,

            *machines.machines[1:],

        ]

    )

    with pytest.raises(

        ValueError,

        match="does not match plant BER",

    ):

        validate_canonical_relationships(

            plants=plants,

            machine_models=machine_models,

            machines=invalid_machines,

            components=components,

        )
