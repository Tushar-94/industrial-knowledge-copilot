"""Generate troubleshooting guides from canonical alarm definitions."""

from __future__ import annotations

from industrial_copilot.domain.models import (

    AlarmDefinition,

    DocumentDefinition,

)

from industrial_copilot.domain.repository import CanonicalRepository

def _find_model_alarms(

    repository: CanonicalRepository,

    model_id: str,

) -> list[AlarmDefinition]:

    """Return all alarms applicable to one machine model."""

    return [

        alarm

        for alarm in repository.alarms.alarms

        if model_id in alarm.applicable_models

    ]

def _format_identifier(value: str) -> str:

    """Convert an internal identifier into readable text."""

    return value.replace("_", " ").capitalize()

def _alarm_section(

    *,

    alarm: AlarmDefinition,

    procedure_titles: dict[str, str],

) -> list[str]:

    """Build one troubleshooting section for an alarm."""

    lines = [

        f"## {alarm.alarm_code} — {alarm.title}",

        "",

        f"**Severity:** {alarm.severity.value.title()}",

        "",

        "### Description",

        "",

        alarm.description,

        "",

        "### Trigger Condition",

        "",

        _format_identifier(alarm.trigger_condition),

        "",

        "### Possible Causes",

        "",

    ]

    for cause in alarm.possible_causes:

        lines.append(f"- {_format_identifier(cause)}")

    lines.extend(

        [

            "",

            "### Diagnostic Checks",

            "",

        ]

    )

    for index, check in enumerate(

        alarm.diagnostic_checks,

        start=1,

    ):

        lines.append(

            f"{index}. {_format_identifier(check)}"

        )

    lines.extend(

        [

            "",

            "### Operator Action",

            "",

            alarm.operator_action,

            "",

            "### Maintenance Action",

            "",

            alarm.maintenance_action,

            "",

            "### Related Procedures",

            "",

        ]

    )

    for procedure_id in alarm.related_procedure_ids:

        procedure_title = procedure_titles[procedure_id]

        lines.append(

            f"- **{procedure_id}** — {procedure_title}"

        )

    lines.append("")

    return lines

def generate_troubleshooting_markdown(

    repository: CanonicalRepository,

    document: DocumentDefinition,

) -> str:

    """Generate Markdown for one troubleshooting guide."""

    if len(document.model_ids) != 1:

        raise ValueError(

            "V1 troubleshooting generation requires exactly one model ID."

        )

    model_id = document.model_ids[0]

    alarms = _find_model_alarms(

        repository=repository,

        model_id=model_id,

    )

    procedure_titles = {

        procedure.procedure_id: procedure.title

        for procedure in repository.procedures.procedures

    }

    lines = [

        f"# {document.title}",

        "",

        "> **Synthetic technical demonstrator:** "

        "This troubleshooting guide is fictional and must not be used "

        "for real machinery.",

        "",

        "## 1. Document Control",

        "",

        "| Field | Value |",

        "|---|---|",

        f"| Document ID | {document.document_id} |",

        f"| Machine model | {model_id} |",

        f"| Revision | {document.revision} |",

        f"| Effective date | {document.effective_date.isoformat()} |",

        f"| Status | {document.status.value.title()} |",

        "",

        "## 2. Purpose",

        "",

        (

            f"This guide provides synthetic troubleshooting information "

            f"for alarms applicable to the NovaTech {model_id}."

        ),

        "",

        "## 3. Alarm Response Principles",

        "",

        (

            "Alarm codes identify abnormal machine conditions. Operators "

            "should follow the stated operator action and escalate faults "

            "requiring maintenance intervention."

        ),

        "",

        (

            "Critical safety alarms must not be bypassed or repeatedly "

            "reset without the underlying cause being corrected."

        ),

        "",

        "## 4. Alarm Reference",

        "",

    ]

    for alarm in alarms:

        lines.extend(

            _alarm_section(

                alarm=alarm,

                procedure_titles=procedure_titles,

            )

        )

    lines.extend(

        [

            "## 5. Document Limitations",

            "",

            (

                "All alarm codes, causes, diagnostic steps, and maintenance "

                "responses in this document are synthetic and exist solely "

                "for software development, retrieval evaluation, and "

                "technical demonstration."

            ),

            "",

        ]

    )

    return "\n".join(lines)
