"""Golden Benchmark Dataset Formulator and Validator for RAG Evaluation (Module 10.1).

Responsible for:
1. Defining the BenchmarkQAPair schema with category validation, expected facts, and source page provenance.
2. Formulating exactly 50 curated ground-truth pairs across 5 categories:
   - 20 Factual
   - 10 Analytical
   - 10 Risk
   - 5 Comparative
   - 5 Negative (Zero-hallucination refusal tests)
3. Serializing and validating the benchmark dataset against JSON schema and distribution rules.
"""

import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class BenchmarkQAPair(BaseModel): #Pydantic model representing a single ground-truth question-answer benchmark entry
    """Data Transfer Object representing a validated evaluation question-answer pair with provenance."""

    id: str = Field( #Unique identifier string for traceability (e.g. FACT-001, NEG-001)
        ...,
        min_length=3,
        description="Unique benchmark question identifier (e.g., 'FACT-001').",
    )
    category: str = Field( #Evaluation category: factual, analytical, risk, comparative, or negative
        ...,
        description="Question category: must be one of 'factual', 'analytical', 'risk', 'comparative', 'negative'.",
    )
    question: str = Field( #The exact prompt / question posed to the RAG pipeline
        ...,
        min_length=5,
        description="Evaluation question string.",
    )
    expected_answer_keywords: List[str] = Field( #Keywords or numbers that must appear in a correct grounded answer
        default_factory=list,
        description="List of key facts, figures, or phrases expected in a truthful response.",
    )
    expected_page_numbers: List[int] = Field( #1-based source page numbers containing evidence for citation evaluation
        default_factory=list,
        description="List of 1-based source page numbers where ground-truth evidence is located.",
    )
    should_answer: bool = Field( #Flag indicating whether the system should answer (True) or refuse to hallucinate (False)
        default=True,
        description="True if the document contains sufficient evidence to answer; False for negative/out-of-domain tests.",
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str: #Validates and normalizes the benchmark category into lowercase
        """Ensures category is one of the 5 canonical benchmark categories."""
        valid_categories = {"factual", "analytical", "risk", "comparative", "negative"} #Set of allowed categories
        cleaned = value.strip().lower() #Strip whitespace and normalize to lowercase
        if cleaned not in valid_categories: #Reject unknown categories
            raise ValueError(
                f"Invalid benchmark category '{value}'. Must be one of: {sorted(list(valid_categories))}."
            )
        return cleaned #Return canonical lowercase category name

    @field_validator("expected_page_numbers")
    @classmethod
    def validate_page_numbers(cls, pages: List[int]) -> List[int]: #Ensures all expected page numbers are positive integers >= 1
        """Ensures all page numbers are positive 1-based integers."""
        for p in pages: #Iterate over each provided page number
            if p < 1: #Check 1-based page bound
                raise ValueError(f"Page numbers must be >= 1, got {p}.")
        return pages #Return validated page number list


class BenchmarkDatasetManager: #Manager responsible for loading, serializing, and validating benchmark datasets
    """Curates, validates, and serializes the 50-pair golden benchmark dataset."""

    EXPECTED_DISTRIBUTION: Dict[str, int] = { #Exact category distribution required by DoD
        "factual": 20,
        "analytical": 10,
        "risk": 10,
        "comparative": 5,
        "negative": 5,
    }

    #Curated 50 ground-truth pairs modeled on public 10-K / Annual Report disclosures
    CURATED_50_PAIRS: List[BenchmarkQAPair] = [
        # --- Category 1: Factual Extraction (20 Pairs) ---
        BenchmarkQAPair(
            id="FACT-001",
            category="factual",
            question="What was the total net sales or revenue for the fiscal year 2024?",
            expected_answer_keywords=["revenue", "net sales", "391,035", "391.0 billion"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-002",
            category="factual",
            question="What was the company's net income for fiscal year 2024?",
            expected_answer_keywords=["net income", "93,736", "93.7 billion"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-003",
            category="factual",
            question="What was the operating income (EBIT) reported for FY2024?",
            expected_answer_keywords=["operating income", "123,216", "123.2 billion"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-004",
            category="factual",
            question="What was the total assets figure as of the end of FY2024?",
            expected_answer_keywords=["total assets", "364,980", "365 billion"],
            expected_page_numbers=[50],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-005",
            category="factual",
            question="What were the total liabilities reported on the consolidated balance sheet for FY2024?",
            expected_answer_keywords=["total liabilities", "308,030", "308 billion"],
            expected_page_numbers=[50],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-006",
            category="factual",
            question="What was the total shareholders' equity balance at fiscal year-end 2024?",
            expected_answer_keywords=["shareholders' equity", "56,950", "57 billion"],
            expected_page_numbers=[50, 52],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-007",
            category="factual",
            question="How much cash was generated from operating activities (CFO) in FY2024?",
            expected_answer_keywords=["operating cash flow", "operating activities", "118,254", "118.3 billion"],
            expected_page_numbers=[53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-008",
            category="factual",
            question="What was the capital expenditures (CapEx) amount spent on property, plant, and equipment in FY2024?",
            expected_answer_keywords=["capital expenditures", "property, plant and equipment", "9,451", "9.5 billion"],
            expected_page_numbers=[35, 53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-009",
            category="factual",
            question="What was the calculated free cash flow for FY2024?",
            expected_answer_keywords=["free cash flow", "108,803", "108.8 billion"],
            expected_page_numbers=[35, 53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-010",
            category="factual",
            question="What was the ending balance of cash and cash equivalents as of September 2024?",
            expected_answer_keywords=["cash and cash equivalents", "29,943", "29.9 billion"],
            expected_page_numbers=[50, 53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-011",
            category="factual",
            question="What was the total term debt including current and non-current portions in FY2024?",
            expected_answer_keywords=["term debt", "commercial paper", "106,629", "106.6 billion"],
            expected_page_numbers=[50, 64],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-012",
            category="factual",
            question="What was the diluted earnings per share (EPS) for FY2024?",
            expected_answer_keywords=["diluted earnings per share", "diluted EPS", "6.08"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-013",
            category="factual",
            question="How much did the company invest in Research and Development (R&D) in FY2024?",
            expected_answer_keywords=["research and development", "R&D", "31,370", "31.4 billion"],
            expected_page_numbers=[34, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-014",
            category="factual",
            question="What was the total selling, general, and administrative (SG&A) expense in FY2024?",
            expected_answer_keywords=["selling, general and administrative", "SG&A", "25,108", "25.1 billion"],
            expected_page_numbers=[34, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-015",
            category="factual",
            question="What was the total gross margin or gross profit for FY2024?",
            expected_answer_keywords=["gross margin", "gross profit", "180,683", "180.7 billion"],
            expected_page_numbers=[33, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-016",
            category="factual",
            question="How many diluted common shares were used to compute earnings per share in FY2024?",
            expected_answer_keywords=["shares used in computing", "diluted shares", "15,408", "15.4 billion"],
            expected_page_numbers=[48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-017",
            category="factual",
            question="What was the provision for income taxes in FY2024?",
            expected_answer_keywords=["provision for income taxes", "tax provision", "29,822", "29.8 billion"],
            expected_page_numbers=[48, 68],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-018",
            category="factual",
            question="What was the cash dividend declared per share during FY2024?",
            expected_answer_keywords=["cash dividends declared", "0.99 per share", "0.99"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-019",
            category="factual",
            question="Who is the independent registered public accounting firm that audited the consolidated financial statements?",
            expected_answer_keywords=["Ernst & Young", "independent registered public accounting firm", "auditor"],
            expected_page_numbers=[45, 46],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="FACT-020",
            category="factual",
            question="What was the effective tax rate for FY2024?",
            expected_answer_keywords=["effective tax rate", "24.1%", "24.1"],
            expected_page_numbers=[68],
            should_answer=True,
        ),

        # --- Category 2: Analytical Questions (10 Pairs) ---
        BenchmarkQAPair(
            id="ANAL-001",
            category="analytical",
            question="What was the year-over-year revenue growth percentage from FY2023 to FY2024?",
            expected_answer_keywords=["revenue growth", "2.02%", "increased by 2%", "383,285 to 391,035"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-002",
            category="analytical",
            question="How did the operating margin (OPM) change between FY2023 and FY2024?",
            expected_answer_keywords=["operating margin", "31.5%", "increased", "expansion"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-003",
            category="analytical",
            question="What was the net profit margin (NPM) achieved in FY2024?",
            expected_answer_keywords=["net profit margin", "23.97%", "24%"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-004",
            category="analytical",
            question="What was the Return on Equity (ROE) based on ending shareholder equity in FY2024?",
            expected_answer_keywords=["ROE", "return on equity", "164.6%", "high ROE"],
            expected_page_numbers=[48, 50],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-005",
            category="analytical",
            question="What was the current ratio (current assets divided by current liabilities) at the end of FY2024?",
            expected_answer_keywords=["current ratio", "0.87", "149,944", "172,999"],
            expected_page_numbers=[50],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-006",
            category="analytical",
            question="What was the debt-to-equity (D/E) leverage ratio at the end of FY2024?",
            expected_answer_keywords=["debt to equity", "1.87", "total debt to equity"],
            expected_page_numbers=[50],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-007",
            category="analytical",
            question="What was the cash conversion quality ratio of operating cash flow to net income (CFO/PAT) for FY2024?",
            expected_answer_keywords=["operating cash flow to net income", "CFO/PAT", "1.26", "quality of earnings"],
            expected_page_numbers=[48, 53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-008",
            category="analytical",
            question="Did net income increase or decrease between FY2023 and FY2024, and by what percentage?",
            expected_answer_keywords=["net income decreased", "decreased by 3.36%", "96,995 to 93,736"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-009",
            category="analytical",
            question="What was the interest coverage ratio (Operating Income / Total Interest Expense) in FY2024?",
            expected_answer_keywords=["interest coverage", "over 30x", "31.8x", "interest expense"],
            expected_page_numbers=[48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="ANAL-010",
            category="analytical",
            question="How did R&D expense as a percentage of net sales evolve from FY2023 to FY2024?",
            expected_answer_keywords=["R&D percentage", "8.0%", "increased from 7.8%"],
            expected_page_numbers=[34, 48],
            should_answer=True,
        ),

        # --- Category 3: Qualitative Risk Questions (10 Pairs) ---
        BenchmarkQAPair(
            id="RISK-001",
            category="risk",
            question="What operational risks does the company disclose regarding its single-source component suppliers?",
            expected_answer_keywords=["single-source suppliers", "components", "disruption", "shortages", "manufacturing delay"],
            expected_page_numbers=[14, 15],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-002",
            category="risk",
            question="What cybersecurity and data privacy threats are identified in Item 1A?",
            expected_answer_keywords=["cybersecurity", "breach", "network intrusions", "reputational harm", "confidential data"],
            expected_page_numbers=[16, 17],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-003",
            category="risk",
            question="How could foreign exchange currency fluctuations impact financial results?",
            expected_answer_keywords=["foreign currency", "exchange rate volatility", "adverse effect on net sales", "hedging"],
            expected_page_numbers=[18, 38],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-004",
            category="risk",
            question="What regulatory and antitrust legal proceedings are disclosed as significant business threats?",
            expected_answer_keywords=["antitrust", "Department of Justice", "regulatory investigations", "fines", "App Store practices"],
            expected_page_numbers=[19, 20],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-005",
            category="risk",
            question="What macroeconomic risks does management cite regarding inflation and economic downturns?",
            expected_answer_keywords=["inflation", "macroeconomic", "consumer demand decline", "rising interest rates"],
            expected_page_numbers=[14, 21],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-006",
            category="risk",
            question="What credit risks exist with respect to customer defaults and trade receivables?",
            expected_answer_keywords=["credit risk", "counterparty default", "cellular network carriers", "trade receivables"],
            expected_page_numbers=[22, 58],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-007",
            category="risk",
            question="What risks are disclosed regarding intellectual property disputes and third-party patent claims?",
            expected_answer_keywords=["intellectual property", "patent infringement", "royalties", "licensing disputes", "litigation"],
            expected_page_numbers=[23, 24],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-008",
            category="risk",
            question="What operational risks are associated with third-party cloud infrastructure and data center outages?",
            expected_answer_keywords=["cloud infrastructure", "data center", "outages", "service availability", "disruption"],
            expected_page_numbers=[17, 25],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-009",
            category="risk",
            question="How could geopolitical tensions and international trade tariffs affect global manufacturing?",
            expected_answer_keywords=["geopolitical tensions", "tariffs", "trade barriers", "international supply chain", "China"],
            expected_page_numbers=[15, 26],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="RISK-010",
            category="risk",
            question="What climate-related environmental risks and natural disaster hazards are disclosed in the report?",
            expected_answer_keywords=["climate change", "extreme weather events", "natural disasters", "facility damage", "disruption"],
            expected_page_numbers=[27],
            should_answer=True,
        ),

        # --- Category 4: Comparative Questions (5 Pairs) ---
        BenchmarkQAPair(
            id="COMP-001",
            category="comparative",
            question="How did Products net sales compare to Services net sales in FY2024?",
            expected_answer_keywords=["Products sales", "294,866", "Services sales", "96,169", "Services grew faster"],
            expected_page_numbers=[33, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="COMP-002",
            category="comparative",
            question="Compare the net sales performance between the Americas segment and Greater China in FY2024.",
            expected_answer_keywords=["Americas", "163,894", "Greater China", "66,952", "China declined"],
            expected_page_numbers=[33, 34],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="COMP-003",
            category="comparative",
            question="Compare the total gross profit generated in FY2023 versus FY2024.",
            expected_answer_keywords=["169,148 in 2023", "180,683 in 2024", "increased by 11,535"],
            expected_page_numbers=[32, 48],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="COMP-004",
            category="comparative",
            question="How did operating cash flow in FY2024 compare to FY2023?",
            expected_answer_keywords=["110,543 in 2023", "118,254 in 2024", "increased by 7,711"],
            expected_page_numbers=[35, 53],
            should_answer=True,
        ),
        BenchmarkQAPair(
            id="COMP-005",
            category="comparative",
            question="Compare the carrying amount of short-term commercial paper against long-term debt as of FY2024.",
            expected_answer_keywords=["commercial paper", "long-term debt", "short-term debt", "debt profile"],
            expected_page_numbers=[50, 64],
            should_answer=True,
        ),

        # --- Category 5: Negative / Zero-Hallucination Tests (5 Pairs) ---
        BenchmarkQAPair(
            id="NEG-001",
            category="negative",
            question="What is the company's projected revenue and net profit guidance for fiscal year 2028?",
            expected_answer_keywords=["not available", "cannot find", "not disclosed", "future forecast not provided"],
            expected_page_numbers=[],
            should_answer=False,
        ),
        BenchmarkQAPair(
            id="NEG-002",
            category="negative",
            question="What was the closing stock ticker price of Apple on the NASDAQ exchange at 4:00 PM today?",
            expected_answer_keywords=["not available", "cannot find", "real-time stock price not in annual report"],
            expected_page_numbers=[],
            should_answer=False,
        ),
        BenchmarkQAPair(
            id="NEG-003",
            category="negative",
            question="Who is the Chief Executive Officer of rival tech company Samsung Electronics?",
            expected_answer_keywords=["not available", "cannot find", "competitor CEO not in document"],
            expected_page_numbers=[],
            should_answer=False,
        ),
        BenchmarkQAPair(
            id="NEG-004",
            category="negative",
            question="What are the internal administrative root passwords for the company's Cupertino cloud server clusters?",
            expected_answer_keywords=["not available", "cannot find", "confidential internal credentials not in filing"],
            expected_page_numbers=[],
            should_answer=False,
        ),
        BenchmarkQAPair(
            id="NEG-005",
            category="negative",
            question="What confidential unannounced corporate mergers or acquisition talks are currently taking place in secret?",
            expected_answer_keywords=["not available", "cannot find", "unannounced secret merger talks not in filing"],
            expected_page_numbers=[],
            should_answer=False,
        ),
    ]

    @classmethod
    def load_dataset(cls, path: str) -> List[BenchmarkQAPair]: #Loads and deserializes benchmark Q&A pairs from a JSON file
        """Loads and validates the golden benchmark dataset from a JSON file.

        Args:
            path: Absolute or relative file path to the benchmark JSON file.

        Returns:
            List[BenchmarkQAPair]: Validated list of 50 benchmark Q&A objects.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            ValueError: If the file contents are invalid or fail schema validation.
        """
        if not os.path.exists(path): #Check file existence
            raise FileNotFoundError(f"Benchmark dataset file not found at '{path}'.")

        try:
            with open(path, "r", encoding="utf-8") as f: #Open file in UTF-8
                data = json.load(f) #Parse JSON content
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from '{path}': {str(e)}")

        raw_pairs = data.get("questions", data if isinstance(data, list) else []) #Extract list of question objects
        if not isinstance(raw_pairs, list):
            raise ValueError("Invalid dataset structure: expected list of question pairs.")

        validated_pairs: List[BenchmarkQAPair] = [] #Container for schema-validated pairs
        for idx, item in enumerate(raw_pairs):
            try:
                pair = BenchmarkQAPair(**item) #Validate item against Pydantic schema
                validated_pairs.append(pair)
            except Exception as e:
                raise ValueError(f"Validation failed for benchmark item at index {idx}: {str(e)}")

        return validated_pairs #Return list of validated benchmark Q&A pairs

    @classmethod
    def save_dataset(cls, path: str, pairs: Optional[List[BenchmarkQAPair]] = None) -> None: #Exports dataset to disk
        """Serializes and writes benchmark Q&A pairs to a JSON file on disk.

        Args:
            path: Target file path to write JSON dataset.
            pairs: Optional list of BenchmarkQAPair objects. Defaults to CURATED_50_PAIRS.
        """
        dataset = pairs if pairs is not None else cls.CURATED_50_PAIRS #Default to curated golden dataset

        payload = { #Standard top-level JSON container
            "version": "1.0",
            "total_questions": len(dataset),
            "distribution": cls.validate_distribution(dataset),
            "questions": [pair.model_dump() for pair in dataset],
        }

        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True) #Ensure parent directory exists
        with open(path, "w", encoding="utf-8") as f: #Write to JSON file with indentation
            json.dump(payload, f, indent=2)

    @classmethod
    def validate_distribution(cls, pairs: List[BenchmarkQAPair]) -> Dict[str, int]: #Verifies 20/10/10/5/5 distribution
        """Validates that a dataset strictly conforms to the expected 5-category 50-pair distribution.

        Args:
            pairs: List of BenchmarkQAPair objects to validate.

        Returns:
            Dict[str, int]: Category count distribution mapping.

        Raises:
            ValueError: If total count is not 50 or any category count deviates from specification.
        """
        counts: Dict[str, int] = {cat: 0 for cat in cls.EXPECTED_DISTRIBUTION} #Initialize count dictionary

        for pair in pairs: #Tally counts per category
            cat = pair.category
            if cat in counts:
                counts[cat] += 1
            else:
                counts[cat] = 1

        total = len(pairs)
        if total != 50: #Validate overall dataset size
            raise ValueError(f"Dataset must contain exactly 50 pairs, found {total}.")

        for cat, expected in cls.EXPECTED_DISTRIBUTION.items(): #Validate per-category counts
            actual = counts.get(cat, 0)
            if actual != expected:
                raise ValueError(
                    f"Category '{cat}' count mismatch: expected {expected}, got {actual}."
                )

        return counts #Return validated distribution dictionary
