"""Generate operation and maintenance manuals from canonical data."""

from __future__ import annotations

from collections import defaultdict

from industrial_copilot.domain.models import (

    DocumentDefinition,

    MachineModel,

    MaintenanceRule,

)

from industrial_copilot.domain.repository import CanonicalRepository

CONDITION_DESCRIPTIONS = {

    "differential_pressure_bar >= 1.0": (

        "Investigate the filter when differential pressure reaches "

        "1.0 bar."

    ),

    "differential_pressure_bar >= 1.5": (

        "Replace the filter earlier when differential pressure reaches "

        "1.5 bar."

    ),

    "oil_analysis_out_of_specification": (

        "Replace the hydraulic fluid earlier when laboratory analysis "

        "shows that the approved fluid condition limits are no longer met."

    ),

    "abnormal_noise_or_pressure_instability": (

        "Inspect the pump earlier when abnormal noise or unstable "

        "hydraulic pressure is observed."

    ),

    "sensor_deviation_bar > 3": (

        "Perform a calibration check when sensor deviation exceeds "

        "3 bar compared with the approved reference gauge."

    ),

    "pressure_control_instability": (

        "Inspect the relief valve when unstable pressure control is observed."

    ),

    "oil_temperature_c >= 70": (

        "Inspect the oil cooler when hydraulic-fluid temperature reaches "

        "70 °C or higher."

    ),

    "guide_friction_or_abnormal_noise": (

        "Inspect the guide lubrication system when increased friction "

        "or abnormal guide noise is observed."

    ),

}

def _format_interval(rule: MaintenanceRule) -> str:

    """Return a readable scheduled-maintenance interval."""

    intervals: list[str] = []

    if rule.interval_operating_hours is not None:

        intervals.append(

            f"{rule.interval_operating_hours:,} operating hours"

        )

    if rule.interval_months is not None:

        intervals.append(

            f"{rule.interval_months} months"

        )

    if not intervals:

        return "Condition-based"

    if len(intervals) == 1:

        return intervals[0]

    return f"{intervals[0]} or {intervals[1]}, whichever occurs first"

def _format_condition(rule: MaintenanceRule) -> str:

    """Translate an internal condition expression into readable prose."""

    if rule.condition_trigger is None:

        return "No additional condition-based trigger is defined."

    return CONDITION_DESCRIPTIONS.get(

        rule.condition_trigger,

        rule.condition_trigger.replace("_", " "),

    )

def _find_machine_model(

    repository: CanonicalRepository,

    model_id: str,

) -> MachineModel:

    """Return one machine model by ID."""

    for model in repository.machine_models.machine_models:

        if model.model_id == model_id:

            return model

    raise ValueError(f"Unknown machine model: {model_id}")

def _find_model_rules(

    repository: CanonicalRepository,

    model_id: str,

) -> list[MaintenanceRule]:

    """Return maintenance rules belonging to one machine model."""

    return [

        rule

        for rule in repository.maintenance_rules.maintenance_rules

        if rule.model_id == model_id

    ]

def _rules_by_component(

    rules: list[MaintenanceRule],

) -> dict[str, list[MaintenanceRule]]:

    """Group maintenance rules by component ID."""

    grouped: dict[str, list[MaintenanceRule]] = defaultdict(list)

    for rule in rules:

        grouped[rule.component_id].append(rule)

    return dict(grouped)

def _component_section(

    *,

    title: str,

    description: str,

    rules: list[MaintenanceRule],

    procedure_titles: dict[str, str],

) -> list[str]:

    """Build one component-specific maintenance section."""

    lines = [

        f"## {title}",

        "",

        description,

        "",

        "### Maintenance requirements",

        "",

    ]

    for rule in rules:

        action = rule.maintenance_action.value.replace("_", " ").title()

        lines.extend(

            [

                f"**{action}:** {_format_interval(rule)}.",

                "",

                _format_condition(rule),

                "",

            ]

        )

        if rule.related_procedure_id is not None:

            procedure_title = procedure_titles[

                rule.related_procedure_id

            ]

            lines.extend(

                [

                    (

                        f"**Related procedure:** "

                        f"{rule.related_procedure_id} — "

                        f"{procedure_title}"

                    ),

                    "",

                ]

            )

    return lines

def generate_manual_markdown(

    repository: CanonicalRepository,

    document: DocumentDefinition,

) -> str:

    """Generate Markdown for one operation and maintenance manual."""

    if len(document.model_ids) != 1:

        raise ValueError(

            "V1 manual generation requires exactly one model ID."

        )

    model_id = document.model_ids[0]

    model = _find_machine_model(repository, model_id)

    rules = _find_model_rules(repository, model_id)

    grouped_rules = _rules_by_component(rules)

    component_by_id = {

        component.component_id: component

        for component in repository.components.components

    }

    procedure_titles = {

        procedure.procedure_id: procedure.title

        for procedure in repository.procedures.procedures

    }

    lines = [

        f"# {document.title}",

        "",

        "> **Synthetic technical demonstrator:** "

        "This document is fictional and is not approved for the "

        "operation, servicing, or maintenance of real machinery.",

        "",

        "## 1. Document Control",

        "",

        "| Field | Value |",

        "|---|---|",

        f"| Document ID | {document.document_id} |",

        f"| Machine model | {model.model_id} |",

        f"| Revision | {document.revision} |",

        f"| Effective date | {document.effective_date.isoformat()} |",

        f"| Status | {document.status.value.title()} |",

        f"| Language | {document.language.value} |",

        "",

        "## 2. Purpose and Scope",

        "",

        (

            f"This manual provides synthetic technical, operating, and "

            f"preventive-maintenance information for the NovaTech "

            f"{model.model_id}. It is intended solely as source material "

            f"for development and evaluation of the Industrial Knowledge "

            f"Copilot."

        ),

        "",

        "## 3. Machine Overview",

        "",

        (

            f"The NovaTech {model.model_id} is a "

            f"{model.machine_type.replace('_', ' ')} used in the "

            f"fictional NovaTech manufacturing environment."

        ),

        "",

        "## 4. Technical Specifications",

        "",

        "| Specification | Value |",

        "|---|---:|",

        f"| Rated forming force | {model.rated_force_kn:,.0f} kN |",

        (

            "| Maximum hydraulic pressure | "

            f"{model.max_hydraulic_pressure_bar:,.0f} bar |"

        ),

        (

            "| Hydraulic reservoir capacity | "

            f"{model.reservoir_capacity_l:,.0f} L |"

        ),

        f"| Main motor power | {model.motor_power_kw:,.0f} kW |",

        f"| Nominal cycle time | {model.nominal_cycle_time_s:g} s |",

        "",

        "## 5. Safety and Operating Boundaries",

        "",

        (

            f"The hydraulic system must not be operated above the "

            f"synthetic maximum pressure of "

            f"{model.max_hydraulic_pressure_bar:,.0f} bar."

        ),

        "",

        (

            "Maintenance requiring access to hazardous energy must follow "

            "the applicable controlled isolation procedure before work "

            "begins."

        ),

        "",

        (

            "Safety devices, guards, or interlocks must not be bypassed "

            "to maintain production."

        ),

        "",

        "## 6. Hydraulic System Overview",

        "",

        (

            "The hydraulic system provides the pressure and flow required "

            "for press operation. Key serviceable elements represented in "

            "this synthetic manual include the hydraulic pump, return-line "

            "filter, reservoir, hydraulic fluid, pressure sensor, pressure "

            "relief valve, and oil cooler."

        ),

        "",

        "## 7. Preventive Maintenance Schedule",

        "",

        "| Component | Activity | Scheduled interval | Condition-based requirement |",

        "|---|---|---|---|",

    ]

    for rule in rules:

        component_name = component_by_id[rule.component_id].name

        lines.append(

            f"| {component_name} "

            f"| {rule.maintenance_action.value.replace('_', ' ').title()} "

            f"| {_format_interval(rule)} "

            f"| {_format_condition(rule)} |"

        )

    section_specs = [

        (

            "8. Hydraulic Return-Line Filter",

            "HYD_RETURN_FILTER",

        ),

        (

            "9. Hydraulic Fluid",

            "HYD_OIL",

        ),

        (

            "10. Hydraulic Pump",

            "HYD_PUMP",

        ),

        (

            "11. Hydraulic Pressure Sensor",

            "HYD_PRESSURE_SENSOR",

        ),

        (

            "12. Pressure Relief Valve",

            "HYD_RELIEF_VALVE",

        ),

        (

            "13. Hydraulic Oil Cooler",

            "COOL_OIL_COOLER",

        ),

        (

            "14. Safety Light Curtain",

            "SAFE_LIGHT_CURTAIN",

        ),

        (

            "15. Guide Lubrication System",

            "LUBE_GUIDE_SYSTEM",

        ),

    ]

    for section_title, component_id in section_specs:

        rules_for_component = grouped_rules.get(component_id)

        if not rules_for_component:

            continue

        component = component_by_id[component_id]

        lines.extend(

            [

                "",

                *_component_section(

                    title=section_title,

                    description=component.description,

                    rules=rules_for_component,

                    procedure_titles=procedure_titles,

                ),

            ]

        )

    lines.extend(

        [

            "## 16. Related Controlled Procedures",

            "",

        ]

    )

    related_procedures = sorted(

        {

            rule.related_procedure_id

            for rule in rules

            if rule.related_procedure_id is not None

        }

    )

    for procedure_id in related_procedures:

        lines.append(

            f"- **{procedure_id}** — {procedure_titles[procedure_id]}"

        )

    lines.extend(

        [

            "",

            "## 17. Document Limitations",

            "",

            (

                "All machine models, specifications, maintenance intervals, "

                "alarm logic, procedures, parts, and operational values "

                "used in this document are synthetic. They exist solely "

                "for software development, retrieval evaluation, and "

                "technical demonstration."

            ),

            "",

        ]

    )

    return "\n".join(lines)

