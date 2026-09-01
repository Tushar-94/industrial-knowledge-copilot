"""Inspect structured information extracted from user queries."""

from __future__ import annotations

from industrial_copilot.retrieval.query_analyzer import analyze_query

QUERIES = [

    "What does HX-417 mean?",

    "What does HX-417 mean on the MX-300?",

    "Which replacement filter is compatible with the MX-300?",

    "What does SOP-MNT-002 cover?",

    "Is HF-300-R10 compatible with the MX-300?",

    "How often should the hydraulic pump be inspected?",

]

def main() -> None:

    """Analyze representative industrial user queries."""

    for query in QUERIES:

        analysis = analyze_query(query)

        print("=" * 80)

        print(f"Query: {query}")

        print()

        print(f"Machine models: {analysis.machine_models}")

        print(f"Alarm codes: {analysis.alarm_codes}")

        print(f"Procedure IDs: {analysis.procedure_ids}")

        print(f"Part numbers: {analysis.part_numbers}")

        print(f"Has identifier: {analysis.has_identifier}")

        print()

if __name__ == "__main__":

    main()
