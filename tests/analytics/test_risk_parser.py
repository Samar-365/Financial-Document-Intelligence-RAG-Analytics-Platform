"""Unit tests for Risk Factor Disclosure Parser (Module 9.1)."""

import pytest
from app.document_processing.metadata_tagger import TextChunkDTO
from app.analytics.risk_parser import RiskDisclosureParser


def _create_chunk(
    chunk_id: str,
    chunk_index: int,
    content: str,
    page_number: int = 1,
    is_table_chunk: bool = False,
    document_id: str = "doc_apple_10k_2024",
) -> TextChunkDTO:
    """Helper to instantiate a valid TextChunkDTO for testing."""
    return TextChunkDTO(
        chunk_id=chunk_id,
        document_id=document_id,
        chunk_index=chunk_index,
        page_number=page_number,
        content=content,
        token_estimate=max(1, len(content) // 4),
        is_table_chunk=is_table_chunk,
    )


class TestRiskDisclosureParserSectionLocator:
    """Test suite for Item 1A / Risk Disclosures section location and tracking."""

    @pytest.fixture
    def parser(self) -> RiskDisclosureParser:
        return RiskDisclosureParser()

    def test_locate_risk_sections_basic_item_1a_flow(self, parser: RiskDisclosureParser):
        """Verifies sequential extraction between Item 1A header and Item 1B exit."""
        chunks = [
            _create_chunk(
                "c0", 0,
                "Item 1. Business.\nApple designs, manufactures and markets smartphones, personal computers, and tablets.",
                page_number=3,
            ),
            _create_chunk(
                "c1", 1,
                "ITEM 1A. RISK FACTORS\nOur business and financial condition may be adversely affected by supply chain disruptions and critical component shortages.",
                page_number=14,
            ),
            _create_chunk(
                "c2", 2,
                "Cybersecurity breaches and unauthorized network intrusion events could cause catastrophic operational losses and severe reputational impairment.",
                page_number=15,
            ),
            _create_chunk(
                "c3", 3,
                "ITEM 1B. UNRESOLVED STAFF COMMENTS\nAs of the date of this Annual Report, there are no unresolved comments from SEC staff.",
                page_number=25,
            ),
            _create_chunk(
                "c4", 4,
                "ITEM 2. PROPERTIES\nOur corporate headquarters are located in Cupertino, California, comprising approximately 4 million square feet.",
                page_number=26,
            ),
        ]

        result = parser.locate_risk_sections(chunks)

        assert len(result) == 2
        assert result[0].chunk_id == "c1"
        assert result[1].chunk_id == "c2"

    def test_locate_risk_sections_alternative_headers(self, parser: RiskDisclosureParser):
        """Verifies recognition of non-SEC or alternative annual report risk headers."""
        headers = [
            "### Item 1A: Risk Factors\nGlobal macroeconomic inflation and interest rate volatility could trigger significant customer defaults and demand decline.",
            "Principal Risks and Uncertainties\nIntense competition from rival technology providers may erode operating profit margins and cause market share loss.",
            "Key Business Risks\nDependency on single-source suppliers poses extreme manufacturing vulnerabilities and potential factory shutdown exposure.",
            "Risks Related to Our Business\nRegulatory investigations and antitrust litigation could impose severe fines and mandate structural divestitures.",
        ]

        for i, header_text in enumerate(headers):
            chunks = [
                _create_chunk(f"c_{i}", 0, header_text, page_number=10),
                _create_chunk(f"exit_{i}", 1, "Item 7. Management's Discussion and Analysis of Financial Condition.", page_number=20),
            ]
            isolated = parser.locate_risk_sections(chunks)
            assert len(isolated) == 1, f"Failed to locate risk chunk for header: {header_text[:30]}"
            assert isolated[0].chunk_id == f"c_{i}"

    def test_locate_risk_sections_stops_at_various_exit_headers(self, parser: RiskDisclosureParser):
        """Verifies section tracker stops on Item 1B, 1C, 2, 3, 4, 7, and 8."""
        exit_headers = [
            "Item 1B. Unresolved Staff Comments.",
            "Item 1C. Cybersecurity disclosures and oversight.",
            "Item 2. Properties.",
            "Item 3. Legal Proceedings and pending antitrust actions.",
            "Item 4. Mine Safety Disclosures.",
            "Item 7. Management's Discussion and Analysis.",
            "Item 8. Consolidated Financial Statements and Supplementary Data.",
        ]

        for exit_hdr in exit_headers:
            chunks = [
                _create_chunk("c_start", 0, "Item 1A. Risk Factors\nSevere supply chain disruption risks could impair production capacity.", page_number=14),
                _create_chunk("c_exit", 1, exit_hdr, page_number=20),
                _create_chunk("c_after", 2, "General narrative after exit with adverse mentions but outside Item 1A.", page_number=21),
            ]
            isolated = parser.locate_risk_sections(chunks)
            assert len(isolated) == 1
            assert isolated[0].chunk_id == "c_start"

    def test_standalone_risk_chunk_detection(self, parser: RiskDisclosureParser):
        """Verifies that chunks with explicit risk headings are captured even without prior Item 1A header."""
        chunks = [
            _create_chunk(
                "c_non_risk", 0,
                "Overview of company operations and general product description across five geographic reporting segments.",
                page_number=5,
            ),
            _create_chunk(
                "c_standalone", 1,
                "### Operational Risks\nThird-party logistics bottlenecks and freight cost inflation could cause substantial distribution losses.",
                page_number=30,
            ),
            _create_chunk(
                "c_another_non_risk", 2,
                "General governance overview of the board of directors and committee charters.",
                page_number=35,
            ),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c_standalone"


class TestRiskDisclosureParserBoilerplateFilter:
    """Test suite for generic regulatory disclaimer and safe-harbor boilerplate noise filtering."""

    @pytest.fixture
    def parser(self) -> RiskDisclosureParser:
        return RiskDisclosureParser()

    def test_filter_generic_forward_looking_disclaimer(self, parser: RiskDisclosureParser):
        """Verifies that standard PSLRA 1995 cautionary notes are discarded."""
        chunks = [
            _create_chunk("c_start", 0, "Item 1A. Risk Factors\nOverview of company disclosures.", page_number=14),
            _create_chunk(
                "c_boilerplate_1", 1,
                "Cautionary Note Regarding Forward-Looking Statements. This report contains statements within the meaning "
                "of Section 27A of the Securities Act of 1933 and the Private Securities Litigation Reform Act of 1995. "
                "Words such as 'anticipate,' 'believe,' 'continue,' 'could,' 'estimate,' 'expect,' 'intend,' 'may,' 'plan,' "
                "and 'will' indicate forward-looking statements. Actual results could differ materially. We undertake no obligation to update.",
                page_number=14,
            ),
            _create_chunk(
                "c_real_risk", 2,
                "Substantial reliance on proprietary semiconductor fabrication partners exposes our business to operational "
                "disruption, supply shortage, and extreme revenue losses if foundries fail to deliver.",
                page_number=15,
            ),
            _create_chunk("c_exit", 3, "Item 1B. Unresolved Staff Comments.", page_number=25),
        ]

        isolated = parser.locate_risk_sections(chunks)
        #c_start is <60 chars so it will be filtered; c_boilerplate_1 is boilerplate; c_real_risk is preserved
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c_real_risk"

    def test_filter_procedural_sec_filing_boilerplate(self, parser: RiskDisclosureParser):
        """Verifies filtering of SEC procedural check marks and statutory filings."""
        chunks = [
            _create_chunk("c_start", 0, "Item 1A. Risk Factors and business vulnerabilities.", page_number=14),
            _create_chunk(
                "c_sec_box", 1,
                "Indicate by check mark whether the registrant is a large accelerated filer, an accelerated filer, "
                "a non-accelerated filer, smaller reporting company, or an emerging growth company pursuant to Section 13.",
                page_number=14,
            ),
            _create_chunk(
                "c_substantive", 2,
                "Failure to comply with international data privacy regulations could subject us to substantial monetary "
                "fines, regulatory investigations, and immediate suspension of cloud service offerings.",
                page_number=15,
            ),
            _create_chunk("c_exit", 3, "Item 2. Properties.", page_number=20),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c_substantive"

    def test_preserve_substantive_risk_with_forward_looking_phrasing(self, parser: RiskDisclosureParser):
        """Ensures concrete operational threat is preserved even if it contains a hedging phrase."""
        chunks = [
            _create_chunk(
                "c1", 0,
                "Item 1A. Risk Factors\nCustomer concentration is high. Loss of our largest telecommunications customer "
                "could cause significant revenue decline and severe operating margin contraction. Although actual results may differ, "
                "we anticipate ongoing liquidity pressure and credit default risks if economic recession persists.",
                page_number=14,
            ),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c1"

    def test_is_boilerplate_helper(self, parser: RiskDisclosureParser):
        """Directly tests the is_boilerplate helper on varied inputs."""
        boilerplate = (
            "Cautionary note regarding forward-looking statements under the Private Securities Litigation Reform Act of 1995. "
            "Words such as anticipate, expect, plan, will indicate forward-looking statements. We undertake no obligation to update."
        )
        assert parser.is_boilerplate(boilerplate) is True

        substantive = (
            "Foreign exchange currency fluctuations and sharp devaluation in European markets could cause severe revenue decline, "
            "adversely affecting our net profit and creating cash flow insolvency vulnerabilities."
        )
        assert parser.is_boilerplate(substantive) is False
        assert parser.is_boilerplate("") is False
        assert parser.is_boilerplate("   ") is False


class TestRiskDisclosureParserTOCAndContentFilter:
    """Test suite for Table of Contents noise and non-substantive chunk filtering."""

    @pytest.fixture
    def parser(self) -> RiskDisclosureParser:
        return RiskDisclosureParser()

    def test_table_of_contents_dotted_lines_skipped(self, parser: RiskDisclosureParser):
        """Verifies TOC pages with dot leaders do not trigger risk section capture."""
        chunks = [
            _create_chunk(
                "c_toc", 0,
                "TABLE OF CONTENTS\nItem 1. Business ................................. 4\n"
                "Item 1A. Risk Factors ......................... 14\n"
                "Item 1B. Unresolved Staff Comments ............. 28\n"
                "Item 2. Properties ............................. 29",
                page_number=2,
            ),
            _create_chunk(
                "c_biz", 1,
                "Item 1. Business\nWe provide enterprise software infrastructure and SaaS services globally.",
                page_number=4,
            ),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 0

    def test_filter_very_short_headers(self, parser: RiskDisclosureParser):
        """Verifies isolated header lines under 60 characters without paragraphs are filtered."""
        chunks = [
            _create_chunk("c_hdr_only", 0, "Item 1A. Risk Factors", page_number=14),
            _create_chunk(
                "c_real", 1,
                "Geopolitical conflict and tariff escalations could severely disrupt our Asian supply chain partners and increase component costs.",
                page_number=14,
            ),
            _create_chunk("c_exit", 2, "Item 1B. Unresolved Staff Comments.", page_number=20),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c_real"

    def test_pure_table_chunk_without_risk_narrative_filtered(self, parser: RiskDisclosureParser):
        """Verifies that purely numerical table chunks without risk statements are filtered out."""
        table_content = "| Category | FY23 | FY24 |\n| Gross Sales | 100 | 120 |"
        chunks = [
            _create_chunk("c_start", 0, "Item 1A. Risk Factors\nDetailed risk disclosures follow below.", page_number=14),
            _create_chunk("c_table", 1, table_content, page_number=14, is_table_chunk=True),
            _create_chunk(
                "c_narrative", 2,
                "Extreme weather patterns and climate-related disruptions pose grave operational risks to our manufacturing facilities.",
                page_number=15,
            ),
            _create_chunk("c_exit", 3, "Item 1B. Unresolved Staff Comments.", page_number=20),
        ]

        isolated = parser.locate_risk_sections(chunks)
        assert len(isolated) == 1
        assert isolated[0].chunk_id == "c_narrative"


class TestRiskDisclosureParserEdgeCasesAndValidation:
    """Test suite for edge cases, input validation, and negative paths."""

    @pytest.fixture
    def parser(self) -> RiskDisclosureParser:
        return RiskDisclosureParser()

    def test_empty_chunks_list(self, parser: RiskDisclosureParser):
        """Verifies empty list input returns empty list immediately."""
        assert parser.locate_risk_sections([]) == []

    def test_no_risk_section_present(self, parser: RiskDisclosureParser):
        """Verifies document with no risk disclosures returns empty list."""
        chunks = [
            _create_chunk("c1", 0, "Item 1. Business description and corporate overview.", page_number=1),
            _create_chunk("c2", 1, "Item 2. Properties and office leasing agreements.", page_number=5),
            _create_chunk("c3", 2, "Item 8. Consolidated financial statements and auditor reports.", page_number=30),
        ]
        assert parser.locate_risk_sections(chunks) == []

    def test_invalid_chunks_type_raises_type_error(self, parser: RiskDisclosureParser):
        """Verifies TypeError on non-list input."""
        with pytest.raises(TypeError, match="chunks must be a list"):
            parser.locate_risk_sections("not a list")  # type: ignore

        with pytest.raises(TypeError, match="chunks must be a list"):
            parser.locate_risk_sections(None)  # type: ignore

    def test_invalid_chunk_element_type_raises_type_error(self, parser: RiskDisclosureParser):
        """Verifies TypeError if any element in chunks is not a TextChunkDTO."""
        valid_chunk = _create_chunk("c1", 0, "Item 1A. Risk Factors\nSevere supplier default risks.", page_number=1)
        with pytest.raises(TypeError, match="Element at index 1.*expected TextChunkDTO"):
            parser.locate_risk_sections([valid_chunk, "invalid_string_chunk"])  # type: ignore

    def test_header_helpers_with_empty_or_whitespace(self, parser: RiskDisclosureParser):
        """Verifies header helper methods handle empty and whitespace strings gracefully."""
        assert parser.is_risk_section_header("") is False
        assert parser.is_risk_section_header("   ") is False
        assert parser.is_section_exit_header("") is False
        assert parser.is_section_exit_header("   ") is False
        assert parser.is_table_of_contents("") is False
        assert parser.is_table_of_contents("   ") is False
