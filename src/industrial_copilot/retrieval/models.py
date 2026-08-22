"""Data models used by the retrieval pipeline."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

class Chunk(BaseModel):

    """One searchable unit extracted from a source document."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)

    text: str = Field(min_length=1)

    document_id: str = Field(min_length=1)

    document_type: str = Field(min_length=1)

    machine_models: list[str]

    section_title: str = Field(min_length=1)

    heading_path: list[str]

    revision: str = Field(min_length=1)

    effective_date: date

    language: str = Field(min_length=1)

    related_components: list[str] = Field(default_factory=list)

    related_procedures: list[str] = Field(default_factory=list)

    alarm_codes: list[str] = Field(default_factory=list)

    embedding_text: str = Field(min_length=1)
