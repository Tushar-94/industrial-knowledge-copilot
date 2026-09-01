"""Utilities for understanding user queries before retrieval."""

from __future__ import annotations

from enum import Enum

import re

from dataclasses import dataclass

MACHINE_MODEL_PATTERN = re.compile(r"\bMX-\d{3}\b", re.IGNORECASE)

ALARM_PATTERN = re.compile(

    r"\b(?:HX|SF|CL|EX)-\d{3}\b",

    re.IGNORECASE,

)

PROCEDURE_PATTERN = re.compile(

    r"\bSOP-[A-Z]+-\d{3}\b",

    re.IGNORECASE,

)

PART_PATTERN = re.compile(

    r"\b[A-Z]{2,4}-\d{3}-[A-Z0-9]+\b",

    re.IGNORECASE,

)

class QueryIntent(str, Enum):

    """High-level user intents relevant to retrieval."""

    PARTS_LOOKUP = "parts_lookup"

    GENERAL = "general"

@dataclass(frozen=True)

class QueryAnalysis:

    machine_models: list[str]

    alarm_codes: list[str]

    procedure_ids: list[str]

    part_numbers: list[str]

    intent: QueryIntent

    @property

    def has_identifier(self) -> bool:

        return any(

            (

                self.machine_models,

                self.alarm_codes,

                self.procedure_ids,

                self.part_numbers,

            )

        )

def _detect_intent(query: str) -> QueryIntent:

    """Detect simple deterministic retrieval intent."""

    normalized = query.lower()

    parts_phrases = (

        "spare part",

        "part number",

        "replacement part",

        "replacement filter",

        "replacement sensor",

        "which part",

        "which filter is compatible",

        "which sensor is compatible",

    )

    if any(

        phrase in normalized

        for phrase in parts_phrases

    ):

        return QueryIntent.PARTS_LOOKUP

    return QueryIntent.GENERAL

def _unique(matches: list[str]) -> list[str]:

    """Remove duplicates while preserving order."""

    return list(dict.fromkeys(match.upper() for match in matches))

def analyze_query(query: str) -> QueryAnalysis:

    """Extract structured identifiers from a user query."""

    return QueryAnalysis(

        machine_models=_unique(

            MACHINE_MODEL_PATTERN.findall(query)

        ),

        alarm_codes=_unique(

            ALARM_PATTERN.findall(query)

        ),

        procedure_ids=_unique(

            PROCEDURE_PATTERN.findall(query)

        ),

        part_numbers=_unique(

            PART_PATTERN.findall(query)

        ),

        intent=_detect_intent(query),

    )