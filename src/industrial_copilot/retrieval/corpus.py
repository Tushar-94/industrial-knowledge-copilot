"""Build a retrieval corpus from generated technical documents."""

from __future__ import annotations

import re

from pathlib import Path

from industrial_copilot.domain.repository import CanonicalRepository

from industrial_copilot.retrieval.markdown_chunker import (

    chunk_markdown_file,

)

from industrial_copilot.retrieval.models import Chunk

ALARM_CODE_PATTERN = re.compile(r"\b[A-Z]{2}-\d{3}\b")

def _enrich_chunk_metadata(

    *,

    chunk: Chunk,

    repository: CanonicalRepository,

) -> Chunk:

    """Enrich a chunk with canonical domain relationships."""

    alarm_codes = set(chunk.alarm_codes)

    related_procedures = set(chunk.related_procedures)

    related_components = set(

        chunk.related_components

    )

    part_numbers = set(

        chunk.part_numbers

    )

    candidate_text = (

        f"{chunk.section_title}\n{chunk.text}"

    )

    detected_alarm_codes = set(

        ALARM_CODE_PATTERN.findall(candidate_text)

    )

    alarms_by_code = {

        alarm.alarm_code: alarm

        for alarm in repository.alarms.alarms

    }

    for alarm_code in detected_alarm_codes:

        alarm = alarms_by_code.get(alarm_code)

        if alarm is None:

            continue

        alarm_codes.add(alarm.alarm_code)

        related_procedures.update(

            alarm.related_procedure_ids

        )

    procedures_by_id = {

        procedure.procedure_id: procedure

        for procedure in repository.procedures.procedures

    }

    if chunk.document_id in procedures_by_id:

        procedure = procedures_by_id[

            chunk.document_id

        ]

        related_components.update(

            procedure.applicable_components

        )

        if (

            "related spare parts"

            in chunk.section_title.lower()

        ):

            for part in repository.parts.parts:

                if (

                    part.component_id

                    in procedure.applicable_components

                ):

                    part_numbers.add(

                        part.part_number

                    )

    return chunk.model_copy(

        update={

            "alarm_codes": sorted(alarm_codes),

            "related_procedures": sorted(

                related_procedures

            ),

            "related_components": sorted(

                related_components

            ),

            "part_numbers": sorted(

                part_numbers

            ),

        }

    )

def build_markdown_corpus(

    *,

    repository: CanonicalRepository,

    document_dir: Path,

) -> list[Chunk]:

    """Load and chunk every generated document defined in the repository."""

    chunks: list[Chunk] = []

    for document in repository.documents.documents:

        document_path = (

            document_dir

            / f"{document.document_id}.md"

        )

        if not document_path.exists():

            raise FileNotFoundError(

                "Generated document is missing: "

                f"{document_path}"

            )

        document_chunks = chunk_markdown_file(

            path=document_path,

            document=document,

        )

        enriched_chunks = [

            _enrich_chunk_metadata(

                chunk=chunk,

                repository=repository,

            )

            for chunk in document_chunks

        ]

        chunks.extend(enriched_chunks)

    return chunks