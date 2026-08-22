"""Structure-aware chunking for generated Markdown documents."""

from __future__ import annotations

import re

from pathlib import Path

from industrial_copilot.domain.models import DocumentDefinition

from industrial_copilot.retrieval.models import Chunk

SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)

def _slugify(value: str) -> str:

    """Convert a heading into a stable lowercase identifier."""

    value = value.lower()

    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-")

def _clean_section_title(title: str) -> str:

    """Remove a leading numeric prefix such as '10. '."""

    return re.sub(r"^\d+\.\s*", "", title).strip()

def _build_embedding_text(

    *,

    machine_models: list[str],

    section_title: str,

    text: str,

) -> str:

    """Build the text that will later be sent to the embedding model."""

    parts: list[str] = []

    if machine_models:

        parts.append(

            "Machine models: " + ", ".join(machine_models)

        )

    parts.append(f"Section: {section_title}")

    parts.append(text)

    return "\n\n".join(parts)

def _create_chunk(

    *,

    document: DocumentDefinition,

    section_title: str,

    text: str,

    chunk_suffix: str,

) -> Chunk:

    """Create one validated retrieval chunk."""

    embedding_text = _build_embedding_text(

        machine_models=document.model_ids,

        section_title=section_title,

        text=text,

    )

    return Chunk(

        chunk_id=(

            f"{document.document_id}::"

            f"{_slugify(section_title)}::"

            f"{chunk_suffix}"

        ),

        text=text,

        document_id=document.document_id,

        document_type=document.document_type.value,

        machine_models=document.model_ids,

        section_title=section_title,

        heading_path=[

            document.title,

            section_title,

        ],

        revision=document.revision,

        effective_date=document.effective_date,

        language=document.language.value,

        embedding_text=embedding_text,

    )

def _split_markdown_table_by_first_column(

    section_text: str,

) -> list[tuple[str, str]]:

    """Split a Markdown table into smaller tables grouped by column one."""

    lines = [

        line.strip()

        for line in section_text.splitlines()

        if line.strip()

    ]

    table_lines = [

        line

        for line in lines

        if line.startswith("|") and line.endswith("|")

    ]

    if len(table_lines) < 3:

        return []

    header = table_lines[0]

    separator = table_lines[1]

    data_rows = table_lines[2:]

    grouped_rows: dict[str, list[str]] = {}

    for row in data_rows:

        cells = [

            cell.strip()

            for cell in row.strip("|").split("|")

        ]

        if not cells or not cells[0]:

            continue

        group_name = cells[0]

        grouped_rows.setdefault(

            group_name,

            [],

        ).append(row)

    return [

        (

            group_name,

            "\n".join(

                [

                    header,

                    separator,

                    *rows,

                ]

            ),

        )

        for group_name, rows in grouped_rows.items()

    ]

def chunk_markdown_document(

    *,

    markdown: str,

    document: DocumentDefinition,

) -> list[Chunk]:

    """Split one Markdown document into structure-aware chunks."""

    matches = list(

        SECTION_PATTERN.finditer(markdown)

    )

    if not matches:

        raise ValueError(

            f"Document {document.document_id} contains no level-2 sections."

        )

    chunks: list[Chunk] = []

    for index, match in enumerate(matches):

        raw_title = match.group(1).strip()

        section_title = _clean_section_title(raw_title)

        content_start = match.end()

        if index + 1 < len(matches):

            content_end = matches[index + 1].start()

        else:

            content_end = len(markdown)

        section_text = markdown[

            content_start:content_end

        ].strip()

        if not section_text:

            continue

        if section_title == "Preventive Maintenance Schedule":

            table_groups = _split_markdown_table_by_first_column(

                section_text

            )

            if table_groups:

                for group_index, (

                    group_name,

                    table_text,

                ) in enumerate(table_groups):

                    grouped_title = (

                        f"{section_title} — {group_name}"

                    )

                    chunks.append(

                        _create_chunk(

                            document=document,

                            section_title=grouped_title,

                            text=table_text,

                            chunk_suffix=(

                                f"{index:03d}-{group_index:02d}"

                            ),

                        )

                    )

                continue

        chunks.append(

            _create_chunk(

                document=document,

                section_title=section_title,

                text=section_text,

                chunk_suffix=f"{index:03d}",

            )

        )

    return chunks

def chunk_markdown_file(

    *,

    path: Path,

    document: DocumentDefinition,

) -> list[Chunk]:

    """Read a Markdown file and return its chunks."""

    markdown = path.read_text(

        encoding="utf-8"

    )

    return chunk_markdown_document(

        markdown=markdown,

        document=document,

    )