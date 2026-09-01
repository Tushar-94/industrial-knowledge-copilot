"""Held-out retrieval benchmark for generalization testing."""

from __future__ import annotations

from industrial_copilot.evaluation.benchmark import (

    ExpectedEvidence,

    RetrievalCase,

)

HELDOUT_RETRIEVAL_BENCHMARK = [

    RetrievalCase(

        case_id="heldout-001",

        category="maintenance",

        query=(

            "The MX-300 return-line filter has reached "

            "760 operating hours. Is it already due for replacement?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Return-Line Filter",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-002",

        category="alarm",

        query=(

            "Our MX-220 panel is showing HX-421. "

            "What condition does that alarm represent?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "TSG-MX220-001",

                "HX-421",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-003",

        category="parts",

        query=(

            "I need to order a replacement return-line filter "

            "for an MX-300. Which item should purchasing request?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-002",

                "Related Spare Parts",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-004",

        category="procedure",

        query=(

            "Which maintenance procedure should a technician follow "

            "when changing the hydraulic return filter?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-002",

                "Purpose and Scope",

            ),

            ExpectedEvidence(

                "SOP-MNT-002",

                "Procedure",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-005",

        category="maintenance",

        query=(

            "The MX-200 hydraulic pump is becoming noisy and "

            "pressure is fluctuating. Should it be inspected early?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pump",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-006",

        category="safety",

        query=(

            "Production wants to keep the machine running even though "

            "the light curtain is interrupted. Is bypassing it allowed?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Safety and Operating Boundaries",

            ),

            ExpectedEvidence(

                "MAN-MX200-001",

                "Safety Light Curtain",

            ),

            ExpectedEvidence(

                "TSG-MX200-001",

                "SF-108",

            ),

            ExpectedEvidence(

                "TSG-MX220-001",

                "SF-108",

            ),

            ExpectedEvidence(

                "TSG-MX300-001",

                "SF-108",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-007",

        category="specification",

        query=(

            "What pressure limit must the hydraulic system on "

            "the MX-220 stay below?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX220-001",

                "Technical Specifications",

            ),

            ExpectedEvidence(

                "MAN-MX220-001",

                "Safety and Operating Boundaries",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-008",

        category="component",

        query=(

            "Which component removes excess heat from the "

            "hydraulic fluid?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Oil Cooler",

            ),

            ExpectedEvidence(

                "MAN-MX220-001",

                "Hydraulic Oil Cooler",

            ),

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Oil Cooler",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-009",

        category="alarm",

        query=(

            "HX-417 appeared after the press began losing hydraulic "

            "pressure. What should maintenance investigate?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "TSG-MX200-001",

                "HX-417",

            ),

            ExpectedEvidence(

                "TSG-MX220-001",

                "HX-417",

            ),

            ExpectedEvidence(

                "TSG-MX300-001",

                "HX-417",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-010",

        category="procedure",

        query=(

            "I need the controlled steps for checking and calibrating "

            "the hydraulic pressure sensor."

        ),

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-003",

                "Procedure",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-011",

        category="parts",

        query=(

            "Which pressure sensor part is suitable for the MX-220?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-003",

                "Related Spare Parts",

            ),

        ),

    ),

    RetrievalCase(

        case_id="heldout-012",

        category="maintenance",

        query=(

            "When does the hydraulic fluid on the MX-300 need to be changed?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Fluid",

            ),

        ),

    ),

]
