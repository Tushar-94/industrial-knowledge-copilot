"""Validated domain models for NovaTech's canonical industrial data."""

from __future__ import annotations

from datetime import date

from enum import StrEnum

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

NonEmptyString = Annotated[str, Field(min_length=1)]

PositiveFloat = Annotated[float, Field(gt=0)]

NonNegativeFloat = Annotated[float, Field(ge=0)]

NonNegativeInt = Annotated[int, Field(ge=0)]

class StrictBaseModel(BaseModel):

    """Base model that rejects unexpected input fields."""

    model_config = ConfigDict(extra="forbid")

class CountryCode(StrEnum):

    """Supported country codes for NovaTech plants."""

    GERMANY = "DE"

class MachineStatus(StrEnum):

    """Operational status of a physical machine."""

    ACTIVE = "active"

    MAINTENANCE = "maintenance"

    OUT_OF_SERVICE = "out_of_service"

class Criticality(StrEnum):

    """Business and production criticality of a machine."""

    MEDIUM = "medium"

    HIGH = "high"

    CRITICAL = "critical"

class SystemType(StrEnum):

    """Major machine systems used to classify components."""

    HYDRAULICS = "hydraulics"

    COOLING = "cooling"

    ELECTRICAL = "electrical"

    SAFETY = "safety"

    LUBRICATION = "lubrication"

class Plant(StrictBaseModel):

    """A NovaTech manufacturing location."""

    plant_id: Annotated[

        str,

        Field(pattern=r"^[A-Z]{3}$"),

    ]

    name: NonEmptyString

    city: NonEmptyString

    country_code: CountryCode

    timezone: Literal["Europe/Berlin"]

    production_focus: NonEmptyString

class MachineModel(StrictBaseModel):

    """Technical specification shared by machines of one model."""

    model_id: Annotated[

        str,

        Field(pattern=r"^MX-\d{3}$"),

    ]

    manufacturer: Literal["NovaTech"]

    machine_type: Literal[

        "hydraulic_forming_press",

        "servo_hydraulic_forming_press",

    ]

    rated_force_kn: PositiveFloat

    max_hydraulic_pressure_bar: PositiveFloat

    reservoir_capacity_l: PositiveFloat

    motor_power_kw: PositiveFloat

    nominal_cycle_time_s: PositiveFloat

    supported_since: date

class Machine(StrictBaseModel):

    """One physical machine installed at a NovaTech plant."""

    machine_id: Annotated[

        str,

        Field(pattern=r"^M\d{3}$"),

    ]

    model_id: Annotated[

        str,

        Field(pattern=r"^MX-\d{3}$"),

    ]

    serial_number: Annotated[

        str,

        Field(pattern=r"^MX\d-\d{6}$"),

    ]

    plant_id: Annotated[

        str,

        Field(pattern=r"^[A-Z]{3}$"),

    ]

    production_line: Annotated[

        str,

        Field(pattern=r"^[A-Z]{3}-L\d+$"),

    ]

    installation_date: date

    current_operating_hours: NonNegativeFloat

    status: MachineStatus

    criticality: Criticality

    downtime_cost_eur_per_hour: NonNegativeFloat

    production_rate_units_per_hour: NonNegativeFloat

class Component(StrictBaseModel):

    """A canonical component or subsystem used by machine models."""

    component_id: Annotated[

        str,

        Field(pattern=r"^[A-Z][A-Z0-9_]+$"),

    ]

    name: NonEmptyString

    system: SystemType

    description: NonEmptyString

    applicable_models: Annotated[

        list[Annotated[str, Field(pattern=r"^MX-\d{3}$")]],

        Field(min_length=1),

    ]

class PlantCollection(StrictBaseModel):

    """Validated contents of plants.yaml."""

    plants: Annotated[list[Plant], Field(min_length=1)]

class MachineModelCollection(StrictBaseModel):

    """Validated contents of machine_models.yaml."""

    machine_models: Annotated[

        list[MachineModel],

        Field(min_length=1),

    ]

class MachineCollection(StrictBaseModel):

    """Validated contents of machines.yaml."""

    machines: Annotated[list[Machine], Field(min_length=1)]

class ComponentCollection(StrictBaseModel):

    """Validated contents of components.yaml."""

    components: Annotated[list[Component], Field(min_length=1)]
