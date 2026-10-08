"""Shared retrieval constraints derived from query analysis."""

from __future__ import annotations

from dataclasses import dataclass

from industrial_copilot.retrieval.models import Chunk

from industrial_copilot.retrieval.query_analyzer import (

    QueryAnalysis,

    QueryIntent,

)

@dataclass(frozen=True)

class RetrievalConstraints:

    """Hard eligibility constraints shared by retrieval branches."""

    machine_model: str | None = None

    alarm_code: str | None = None

    procedure_id: str | None = None

    part_number: str | None = None

    contains_spare_parts: bool | None = None

def build_retrieval_constraints(

    analysis: QueryAnalysis,

) -> RetrievalConstraints:

    """Translate analyzed query metadata into retrieval constraints."""

    return RetrievalConstraints(

        machine_model=(

            analysis.machine_models[0]

            if len(analysis.machine_models) == 1

            else None

        ),

        alarm_code=(

            analysis.alarm_codes[0]

            if len(analysis.alarm_codes) == 1

            else None

        ),

        procedure_id=(

            analysis.procedure_ids[0]

            if len(analysis.procedure_ids) == 1

            else None

        ),

        part_number=(

            analysis.part_numbers[0]

            if len(analysis.part_numbers) == 1

            else None

        ),

        contains_spare_parts=(

            True

            if analysis.intent == QueryIntent.PARTS_LOOKUP

            else None

        ),

    )

def chunk_matches_constraints(

    chunk: Chunk,

    constraints: RetrievalConstraints,

) -> bool:

    """Return whether a chunk satisfies all hard constraints."""

    if (

        constraints.machine_model is not None

        and constraints.machine_model not in chunk.machine_models

    ):

        return False

    if (

        constraints.alarm_code is not None

        and constraints.alarm_code not in chunk.alarm_codes

    ):

        return False

    if (

        constraints.procedure_id is not None

        and chunk.document_id != constraints.procedure_id

    ):

        return False

    if (

        constraints.part_number is not None

        and constraints.part_number not in chunk.part_numbers

    ):

        return False

    if constraints.contains_spare_parts is not None:

        contains_spare_parts = bool(chunk.part_numbers)

        if (

            contains_spare_parts

            != constraints.contains_spare_parts

        ):

            return False

    return True
