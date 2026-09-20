"""Unit tests for 7-Domain Risk Classifier and Severity Ranker (Module 9.2)."""

from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError

from app.analytics.risk_classifier import RiskClassifier, RiskItemDTO
from app.document_processing.metadata_tagger import TextChunkDTO
from app.rag.llm_client import LLMGenerationResultDTO, OpenAIClientWrapper


def _create_mock_llm(json_str: str) -> OpenAIClientWrapper:
    """Helper creating a mocked OpenAIClientWrapper returning a given raw answer."""
    mock_client = MagicMock(spec=OpenAIClientWrapper)
    mock_client.generate.return_value = LLMGenerationResultDTO(
        raw_answer=json_str,
        prompt_tokens=200,
        completion_tokens=100,
        model_name="gpt-4o-mini",
    )
    return mock_client


def _create_chunk(
    chunk_id: str,
    content: str,
    page_number: int = 14,
    document_id: str = "doc_apple_10k_2024",
) -> TextChunkDTO:
    """Helper creating a valid TextChunkDTO for testing."""
    return TextChunkDTO(
        chunk_id=chunk_id,
        document_id=document_id,
        chunk_index=0,
        page_number=page_number,
        content=content,
        token_estimate=max(1, len(content) // 4),
        is_table_chunk=False,
    )


class TestRiskItemDTO:
    """Test suite for RiskItemDTO validation and normalization."""

    def test_valid_dto_canonicalization(self):
        """Verifies valid fields and case-insensitive normalization of category and severity."""
        dto = RiskItemDTO(
            category="operational",
            severity="high",
            title="Supply Chain Bottleneck",
            description="Shortages of semiconductor components may delay device shipments.",
            supporting_quote="Disruptions in our supply chain could materially impact revenue.",
            page_number=14,
        )
        assert dto.category == "Operational"
        assert dto.severity == "High"
        assert dto.page_number == 14

    def test_invalid_category_raises_validation_error(self):
        """Verifies rejection of non-existent risk category."""
        with pytest.raises(ValidationError):
            RiskItemDTO(
                category="Environmental",  # Not in the 7 canonical domains
                severity="High",
                title="Climate Impact",
                description="Heavy storms could damage factories.",
                supporting_quote="Storms may damage facilities.",
                page_number=14,
            )

    def test_invalid_severity_raises_validation_error(self):
        """Verifies rejection of invalid severity string."""
        with pytest.raises(ValidationError):
            RiskItemDTO(
                category="Credit",
                severity="Critical",  # Must be High, Medium, or Low
                title="Counterparty Failure",
                description="Major distributor default risk.",
                supporting_quote="Counterparty may default on payment.",
                page_number=10,
            )

    def test_page_number_bounds(self):
        """Verifies page_number must be >= 1."""
        with pytest.raises(ValidationError):
            RiskItemDTO(
                category="Liquidity",
                severity="Medium",
                title="Refinancing Exposure",
                description="Unable to roll over debt.",
                supporting_quote="Short-term debt maturity risk.",
                page_number=0,  # Invalid
            )


class TestRiskClassifier:
    """Test suite for RiskClassifier logic, prompts, and parsing."""

    def test_classify_risks_definition_of_done(self):
        """Verifies Definition of Done (DoD):

        Output contains at least 3 categorized risk entries with direct supporting quotes and page numbers.
        """
        chunk_text = (
            "Our operations depend on global suppliers; supply chain disruptions and critical component "
            "shortages could severely impair manufacturing. Additionally, foreign currency fluctuations in European "
            "and Asian markets expose our net income to substantial volatility. Furthermore, ongoing antitrust and regulatory "
            "investigations by the Department of Justice could impose severe monetary fines and mandatory structural divestitures."
        )
        chunk = _create_chunk("c_dod", chunk_text, page_number=14)

        llm_response = """{
            "risks": [
                {
                    "category": "Operational",
                    "severity": "High",
                    "title": "Supply Chain and Component Shortages",
                    "description": "Reliance on global suppliers may halt device production during component shortages.",
                    "supporting_quote": "supply chain disruptions and critical component shortages could severely impair manufacturing.",
                    "page_number": 14
                },
                {
                    "category": "Market",
                    "severity": "Medium",
                    "title": "Foreign Exchange Volatility",
                    "description": "Currency swings across Europe and Asia could compress net profit margins.",
                    "supporting_quote": "foreign currency fluctuations in European and Asian markets expose our net income to substantial volatility.",
                    "page_number": 14
                },
                {
                    "category": "Regulatory",
                    "severity": "High",
                    "title": "Antitrust Investigations and Fines",
                    "description": "DOJ antitrust probes could result in major financial penalties and restructuring.",
                    "supporting_quote": "ongoing antitrust and regulatory investigations by the Department of Justice could impose severe monetary fines",
                    "page_number": 14
                }
            ]
        }"""

        mock_llm = _create_mock_llm(llm_response)
        classifier = RiskClassifier(llm_client=mock_llm)

        results = classifier.classify_risks([chunk])

        # DoD: At least 3 categorized risk entries
        assert len(results) >= 3

        # Verify attributes and provenance quotes
        categories = [r.category for r in results]
        assert "Operational" in categories
        assert "Market" in categories
        assert "Regulatory" in categories

        for risk in results:
            assert risk.severity in {"High", "Medium", "Low"}
            assert risk.page_number == 14
            assert len(risk.supporting_quote) > 10
            assert risk.supporting_quote.lower() in chunk_text.lower()

    def test_all_7_domains_coverage(self):
        """Verifies correct classification across all 7 canonical risk domains."""
        llm_response = """{
            "risks": [
                {"category": "Credit", "severity": "Medium", "title": "Customer Default", "description": "Payment failure.", "supporting_quote": "Default risks.", "page_number": 1},
                {"category": "Market", "severity": "Low", "title": "Equity Drop", "description": "Stock price swing.", "supporting_quote": "Market drop.", "page_number": 2},
                {"category": "Liquidity", "severity": "High", "title": "Cash Burn", "description": "Cash exhaustion.", "supporting_quote": "Liquidity shortfall.", "page_number": 3},
                {"category": "Operational", "severity": "High", "title": "Outage", "description": "Server failure.", "supporting_quote": "System outage.", "page_number": 4},
                {"category": "Regulatory", "severity": "Medium", "title": "GDPR Probe", "description": "Data audit.", "supporting_quote": "Regulatory probe.", "page_number": 5},
                {"category": "Strategic", "severity": "Low", "title": "New Competitor", "description": "Market erosion.", "supporting_quote": "Competitor entrant.", "page_number": 6},
                {"category": "Macroeconomic", "severity": "High", "title": "Stagflation", "description": "GDP contraction.", "supporting_quote": "Economic recession.", "page_number": 7}
            ]
        }"""
        chunk = _create_chunk("c_all", "Default risks. Market drop. Liquidity shortfall. System outage. Regulatory probe. Competitor entrant. Economic recession.")
        mock_llm = _create_mock_llm(llm_response)
        classifier = RiskClassifier(llm_client=mock_llm)

        results = classifier.classify_risks([chunk])
        assert len(results) == 7
        domains = {r.category for r in results}
        expected_domains = {"Credit", "Market", "Liquidity", "Operational", "Regulatory", "Strategic", "Macroeconomic"}
        assert domains == expected_domains

    def test_markdown_json_fences_stripped(self):
        """Verifies parser handles markdown code blocks (```json ... ```)."""
        fenced_response = """```json
        {
            "risks": [
                {
                    "category": "Strategic",
                    "severity": "High",
                    "title": "Disruptive AI Competitor",
                    "description": "Generative AI rivals could obsolete core software products.",
                    "supporting_quote": "Rapid technological transitions may displace legacy solutions.",
                    "page_number": 22
                }
            ]
        }
        ```"""
        chunk = _create_chunk("c_fence", "Rapid technological transitions may displace legacy solutions.", page_number=22)
        classifier = RiskClassifier(llm_client=_create_mock_llm(fenced_response))

        results = classifier.classify_risks([chunk])
        assert len(results) == 1
        assert results[0].category == "Strategic"
        assert results[0].page_number == 22

    def test_surrounding_conversational_text_parsed(self):
        """Verifies JSON object extraction when surrounded by conversational LLM prose."""
        conversational_response = """Here is your risk classification analysis:
        {
            "risks": [
                {
                    "category": "Macroeconomic",
                    "severity": "Medium",
                    "title": "Persistent Inflationary Headwinds",
                    "description": "Rising raw material costs could compress operating margins.",
                    "supporting_quote": "Inflationary headwinds could increase input manufacturing costs.",
                    "page_number": 19
                }
            ]
        }
        Let me know if you need further risk breakdowns!"""
        chunk = _create_chunk("c_conv", "Inflationary headwinds could increase input manufacturing costs.", page_number=19)
        classifier = RiskClassifier(llm_client=_create_mock_llm(conversational_response))

        results = classifier.classify_risks([chunk])
        assert len(results) == 1
        assert results[0].category == "Macroeconomic"

    def test_malformed_json_fallback(self):
        """Verifies that invalid or malformed JSON from LLM gracefully returns empty list without crashing."""
        malformed_response = "I am sorry, but I cannot extract risks from this text."
        chunk = _create_chunk("c_bad", "General disclosures.")
        classifier = RiskClassifier(llm_client=_create_mock_llm(malformed_response))

        results = classifier.classify_risks([chunk])
        assert results == []

    def test_empty_chunks_returns_empty(self):
        """Verifies empty chunk list immediately returns empty list."""
        classifier = RiskClassifier(llm_client=MagicMock())
        assert classifier.classify_risks([]) == []

    def test_invalid_input_types_raise_type_error(self):
        """Verifies TypeError on invalid arguments."""
        classifier = RiskClassifier(llm_client=MagicMock())

        with pytest.raises(TypeError, match="risk_chunks must be a list"):
            classifier.classify_risks("not a list")  # type: ignore

        with pytest.raises(TypeError, match="risk_chunks must be a list"):
            classifier.classify_risks(None)  # type: ignore

        valid_chunk = _create_chunk("c1", "Risk statement.")
        with pytest.raises(TypeError, match="Element at index 1.*expected TextChunkDTO"):
            classifier.classify_risks([valid_chunk, "invalid_string_element"])  # type: ignore
