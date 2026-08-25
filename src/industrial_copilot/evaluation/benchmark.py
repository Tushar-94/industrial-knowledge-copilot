"""Retrieval benchmark definitions for the Industrial Knowledge Copilot."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)

class ExpectedEvidence:

    """One acceptable source of evidence for a benchmark question."""

    document_id: str

    section_contains: str

@dataclass(frozen=True)

class RetrievalCase:

    """One retrieval-evaluation question and its valid evidence."""

    case_id: str

    category: str

    query: str

    expected_evidence: tuple[ExpectedEvidence, ...]

RETRIEVAL_BENCHMARK = [

    RetrievalCase(

        case_id="spec-001",

        category="specification",

        query="What is the maximum hydraulic pressure of the MX-200?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Technical Specifications",

            ),

        ),

    ),

    RetrievalCase(

        case_id="spec-002",

        category="specification",

        query="How much forming force does the MX-300 provide?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX300-001",

                "Technical Specifications",

            ),

        ),

    ),

    RetrievalCase(

        case_id="maint-001",

        category="maintenance",

        query="How often should the hydraulic pump on the MX-200 be inspected?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pump",

            ),

        ),

    ),

    RetrievalCase(

        case_id="maint-002",

        category="maintenance",

        query="When should the MX-300 return filter be replaced?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Return-Line Filter",

            ),

        ),

    ),

    RetrievalCase(

        case_id="maint-003",

        category="maintenance",

        query="When does the MX-200 hydraulic fluid need replacement?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Fluid",

            ),

        ),

    ),

    RetrievalCase(

        case_id="maint-004",

        category="maintenance",

        query="How often should the MX-200 pressure sensor be calibrated?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pressure Sensor",

            ),

        ),

    ),

    RetrievalCase(

        case_id="condition-001",

        category="condition",

        query=(

            "When should the MX-200 return filter "

            "be replaced earlier than scheduled?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Return-Line Filter",

            ),

        ),

    ),

    RetrievalCase(

        case_id="condition-002",

        category="condition",

        query=(

            "What condition should trigger an early "

            "hydraulic pump inspection?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pump",

            ),

            ExpectedEvidence(

                "MAN-MX220-001",

                "Hydraulic Pump",

            ),

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Pump",

            ),

        ),

    ),

    RetrievalCase(

        case_id="alarm-001",

        category="alarm",

        query="What does alarm HX-417 mean?",

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

        case_id="alarm-002",

        category="alarm",

        query="What can cause HX-417?",

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

        case_id="alarm-003",

        category="alarm",

        query="What does HX-421 indicate?",

        expected_evidence=(

            ExpectedEvidence(

                "TSG-MX200-001",

                "HX-421",

            ),

            ExpectedEvidence(

                "TSG-MX220-001",

                "HX-421",

            ),

            ExpectedEvidence(

                "TSG-MX300-001",

                "HX-421",

            ),

        ),

    ),

    RetrievalCase(

        case_id="alarm-004",

        category="alarm",

        query="Why might hydraulic oil temperature alarm HX-471 occur?",

        expected_evidence=(

            ExpectedEvidence(

                "TSG-MX200-001",

                "HX-471",

            ),

            ExpectedEvidence(

                "TSG-MX220-001",

                "HX-471",

            ),

            ExpectedEvidence(

                "TSG-MX300-001",

                "HX-471",

            ),

        ),

    ),

    RetrievalCase(

        case_id="safety-001",

        category="safety",

        query=(

            "Can the safety light curtain be bypassed "

            "to keep production running?"

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

                "MAN-MX220-001",

                "Safety and Operating Boundaries",

            ),

            ExpectedEvidence(

                "MAN-MX300-001",

                "Safety and Operating Boundaries",

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

        case_id="safety-002",

        category="safety",

        query=(

            "What should be done before performing maintenance "

            "involving hazardous energy?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "SOP-HSE-001",

                "Procedure",

            ),

            ExpectedEvidence(

                "SOP-HSE-001",

                "Safety Warnings",

            ),

        ),

    ),

    RetrievalCase(

        case_id="procedure-001",

        category="procedure",

        query="Which procedure explains hydraulic return filter replacement?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-002",

                "Purpose and Scope",

            ),

        ),

    ),

    RetrievalCase(

        case_id="procedure-002",

        category="procedure",

        query="What are the steps for replacing the hydraulic return filter?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-002",

                "Procedure",

            ),

        ),

    ),

    RetrievalCase(

        case_id="procedure-003",

        category="procedure",

        query="Which procedure covers hydraulic pressure sensor calibration?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-003",

                "Purpose and Scope",

            ),

        ),

    ),

    RetrievalCase(

        case_id="procedure-004",

        category="procedure",

        query="How do I verify and calibrate the hydraulic pressure sensor?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-003",

                "Procedure",

            ),

        ),

    ),

    RetrievalCase(

        case_id="parts-001",

        category="parts",

        query="Which replacement filter is compatible with the MX-300?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-002",

                "Related Spare Parts",

            ),

        ),

    ),

    RetrievalCase(

        case_id="parts-002",

        category="parts",

        query="Which pressure sensor spare part is used for the MX-220?",

        expected_evidence=(

            ExpectedEvidence(

                "SOP-MNT-003",

                "Related Spare Parts",

            ),

        ),

    ),

    RetrievalCase(

        case_id="component-001",

        category="component",

        query="What does the hydraulic oil cooler do?",

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

        case_id="component-002",

        category="component",

        query="What is the purpose of the hydraulic pressure sensor?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pressure Sensor",

            ),

        ),

    ),

    RetrievalCase(

        case_id="paraphrase-001",

        category="paraphrase",

        query="When does the MX-200 pump need servicing?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pump",

            ),

        ),

    ),

    RetrievalCase(

        case_id="paraphrase-002",

        category="paraphrase",

        query="How frequently should I change the MX-300 return-line filter?",

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX300-001",

                "Hydraulic Return-Line Filter",

            ),

        ),

    ),

    RetrievalCase(

        case_id="paraphrase-003",

        category="paraphrase",

        query=(

            "What should maintenance check if the press "

            "has unstable hydraulic pressure?"

        ),

        expected_evidence=(

            ExpectedEvidence(

                "MAN-MX200-001",

                "Hydraulic Pump",

            ),

            ExpectedEvidence(

                "SOP-MNT-001",

                "Procedure",

            ),

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

]