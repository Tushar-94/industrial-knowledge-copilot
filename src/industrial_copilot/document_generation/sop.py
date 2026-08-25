"""Generate standard operating procedures from canonical procedure data."""

from __future__ import annotations

from industrial_copilot.domain.models import (

    DocumentDefinition,

    ProcedureDefinition,

)

from industrial_copilot.domain.repository import CanonicalRepository

def _find_procedure(

    repository: CanonicalRepository,

    procedure_id: str,

) -> ProcedureDefinition:

    """Return one canonical procedure by ID."""

    for procedure in repository.procedures.procedures:

        if procedure.procedure_id == procedure_id:

            return procedure

    raise ValueError(

        f"Unknown procedure: {procedure_id}"

    )

def _find_component_names(

    *,

    repository: CanonicalRepository,

    component_ids: list[str],

) -> list[str]:

    """Translate canonical component IDs into readable names."""

    component_names = {

        component.component_id: component.name

        for component in repository.components.components

    }

    return [

        component_names[component_id]

        for component_id in component_ids

    ]

def _find_related_parts(

    *,

    repository: CanonicalRepository,

    component_ids: list[str],

    applicable_models: list[str],

) -> list[tuple[str, str, list[str]]]:

    """Find spare parts relevant to the procedure's components and models."""

    related_parts: list[

        tuple[str, str, list[str]]

    ] = []

    component_id_set = set(component_ids)

    applicable_model_set = set(applicable_models)

    for part in repository.parts.parts:

        if part.component_id not in component_id_set:

            continue

        compatible_models = sorted(

            set(part.compatible_models)

            & applicable_model_set

        )

        if not compatible_models:

            continue

        related_parts.append(

            (

                part.part_number,

                part.part_name,

                compatible_models,

            )

        )

    return related_parts

def generate_sop_markdown(

    repository: CanonicalRepository,

    document: DocumentDefinition,

) -> str:

    """Generate Markdown for one standard operating procedure."""

    if len(document.procedure_ids) != 1:

        raise ValueError(

            "V1 SOP generation requires exactly one procedure ID."

        )

    procedure_id = document.procedure_ids[0]

    procedure = _find_procedure(

        repository=repository,

        procedure_id=procedure_id,

    )

    component_names = _find_component_names(

        repository=repository,

        component_ids=procedure.applicable_components,

    )

    related_parts = _find_related_parts(

        repository=repository,

        component_ids=procedure.applicable_components,

        applicable_models=procedure.applicable_models,

    )

    lines = [

        f"# {document.title}",

        "",

        "> **Synthetic technical demonstrator:** "

        "This procedure is fictional and is not approved for use "

        "on real machinery.",

        "",

        "## 1. Document Control",

        "",

        "| Field | Value |",

        "|---|---|",

        f"| Document ID | {document.document_id} |",

        f"| Procedure ID | {procedure.procedure_id} |",

        f"| Procedure type | {procedure.procedure_type.value.title()} |",

        f"| Revision | {procedure.revision} |",

        f"| Effective date | {procedure.effective_date.isoformat()} |",

        f"| Status | {procedure.status.value.title()} |",

        f"| Language | {document.language.value} |",

        "",

        "## 2. Purpose and Scope",

        "",

        (

            f"This procedure provides the synthetic controlled workflow "

            f"for **{procedure.title}**."

        ),

        "",

        "## 3. Applicable Machine Models",

        "",

    ]

    for model_id in procedure.applicable_models:

        lines.append(f"- {model_id}")

    lines.extend(

        [

            "",

            "## 4. Applicable Components",

            "",

        ]

    )

    if component_names:

        for component_name in component_names:

            lines.append(f"- {component_name}")

    else:

        lines.append(

            "- This procedure applies at machine level rather than "

            "to one specific component."

        )

    lines.extend(

        [

            "",

            "## 5. Prerequisites",

            "",

        ]

    )

    for prerequisite in procedure.prerequisites:

        lines.append(f"- {prerequisite}")

    lines.extend(

        [

            "",

            "## 6. Safety Warnings",

            "",

        ]

    )

    if procedure.warnings:

        for warning in procedure.warnings:

            lines.append(f"- **WARNING:** {warning}")

    else:

        lines.append(

            "- Follow applicable site safety and authorization requirements."

        )

    lines.extend(

        [

            "",

            "## 7. Procedure",

            "",

        ]

    )

    for step_number, step in enumerate(

        procedure.steps,

        start=1,

    ):

        lines.append(

            f"{step_number}. {step}"

        )

    lines.extend(

        [

            "",

            "## 8. Related Spare Parts",

            "",

        ]

    )

    if related_parts:

        lines.extend(

            [

                "| Part number | Part name | Compatible models |",

                "|---|---|---|",

            ]

        )

        for (

            part_number,

            part_name,

            compatible_models,

        ) in related_parts:

            lines.append(

                f"| {part_number} "

                f"| {part_name} "

                f"| {', '.join(compatible_models)} |"

            )

    else:

        lines.append(

            "No component-specific spare parts are defined for this procedure."

        )

    lines.extend(

        [

            "",

            "## 9. Document Limitations",

            "",

            (

                "All machines, procedures, technical values, parts, and "

                "maintenance instructions in this document are synthetic. "

                "They exist solely for development and evaluation of the "

                "Industrial Knowledge Copilot."

            ),

            "",

        ]

    )

    return "\n".join(lines)
