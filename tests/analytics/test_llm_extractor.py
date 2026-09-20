from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from app.analytics.llm_extractor import (
    ExtractedFinancialMetricsDTO,
    LLMMetricExtractor,
    MetricAuditMetadata,
)
from app.rag.llm_client import LLMGenerationResultDTO, OpenAIClientWrapper


def _create_mock_llm_client(json_response_str: str) -> OpenAIClientWrapper:
    """Helper creating a mocked OpenAIClientWrapper returning a given JSON string."""
    mock_client = MagicMock(spec=OpenAIClientWrapper)
    mock_client.generate.return_value = LLMGenerationResultDTO(
        raw_answer=json_response_str,
        prompt_tokens=150,
        completion_tokens=50,
        model_name="gpt-4o-mini",
    )
    return mock_client


def test_extract_missing_metrics_dod():
    """Verifies Definition of Done (DoD):

    Fills missing metrics with valid Decimal values; returns None when items are genuinely unstated.
    """
    # Suppose regex already extracted revenue and operating_income
    current_metrics = {
        "revenue": Decimal("10000000000.00"),
        "operating_income": Decimal("1500000000.00"),
    }

    # Mock LLM provides ebitda and total_debt, but leaves free_cash_flow and others unstated (null)
    llm_json = """{
        "ebitda": "250 Cr",
        "total_debt": "500 Cr",
        "net_income": "900 Cr",
        "free_cash_flow": null
    }"""

    mock_llm = _create_mock_llm_client(llm_json)
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    statement_text = "EBITDA for the year stood at Rs. 250 Cr with total debt of 500 Cr and Net Profit of 900 Cr."

    result = extractor.extract_missing_metrics(
        statement_text=statement_text,
        current_metrics=current_metrics,
        document_id="RELIANCE-FY25",
        fiscal_year="FY25",
    )

    # 1. Existing regex metrics preserved
    assert result.revenue == Decimal("10000000000.00")
    assert result.operating_income == Decimal("1500000000.00")

    # 2. Missing metrics filled with valid Decimal values
    assert result.ebitda == Decimal("2500000000.00")
    assert result.total_debt == Decimal("5000000000.00")
    assert result.net_income == Decimal("9000000000.00")

    # 3. Unstated items return None
    assert result.free_cash_flow is None
    assert result.total_assets is None


def test_audit_metadata_assignment():
    """Verifies Task 2 (Audit Metadata Assignment):

    Marks extracted values with is_calculated, confidence, and source metadata.
    """
    current_metrics = {
        "revenue": Decimal("5000000000.00"),
    }
    llm_json = '{"ebitda": "800 M", "net_income": null}'
    mock_llm = _create_mock_llm_client(llm_json)
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    result = extractor.extract_missing_metrics(
        statement_text="EBITDA reached 800 M.",
        current_metrics=current_metrics,
    )

    meta = result.audit_metadata

    # Regex metric audit
    assert meta["revenue"].source == "regex"
    assert meta["revenue"].confidence == 1.0
    assert meta["revenue"].is_calculated is False

    # LLM metric audit
    assert meta["ebitda"].source == "llm"
    assert meta["ebitda"].confidence == 0.85
    assert meta["ebitda"].is_calculated is False

    # Unextracted metric audit
    assert meta["net_income"].source == "unextracted"
    assert meta["net_income"].confidence == 0.0


def test_all_metrics_present_skips_llm():
    """Verifies that if all 12 canonical metrics are provided, LLM dispatch is bypassed."""
    mock_llm = MagicMock(spec=OpenAIClientWrapper)
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    all_metrics = {k: Decimal("100000.00") for k in extractor.CANONICAL_METRICS}

    result = extractor.extract_missing_metrics(
        statement_text="Some financial text",
        current_metrics=all_metrics,
    )

    # LLM should never be called
    mock_llm.generate.assert_not_called()
    assert result.revenue == Decimal("100000.00")
    assert all(m.source == "regex" for m in result.audit_metadata.values())


def test_empty_statement_text_handling():
    """Verifies that empty statement text safely returns unextracted missing metrics without calling LLM."""
    mock_llm = MagicMock(spec=OpenAIClientWrapper)
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    result = extractor.extract_missing_metrics(
        statement_text="   ",
        current_metrics={"revenue": Decimal("1000.00")},
    )

    mock_llm.generate.assert_not_called()
    assert result.revenue == Decimal("1000.00")
    assert result.ebitda is None
    assert result.audit_metadata["ebitda"].source == "unextracted"


def test_llm_json_with_markdown_fences():
    """Verifies parsing when LLM wraps response in markdown codeblock fences."""
    fenced_json = "```json\n{\n  \"ebitda\": \"150 M\"\n}\n```"
    mock_llm = _create_mock_llm_client(fenced_json)
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    result = extractor.extract_missing_metrics(
        statement_text="Text context",
        current_metrics={},
    )

    assert result.ebitda == Decimal("150000000.00")
    assert result.audit_metadata["ebitda"].source == "llm"


def test_llm_malformed_json_resilience():
    """Verifies resilience when LLM outputs invalid JSON string."""
    mock_llm = _create_mock_llm_client("This is not valid JSON at all.")
    extractor = LLMMetricExtractor(llm_client=mock_llm)

    result = extractor.extract_missing_metrics(
        statement_text="Some text",
        current_metrics={"revenue": Decimal("500.00")},
    )

    # Does not crash, sets missing to None with unextracted source
    assert result.revenue == Decimal("500.00")
    assert result.ebitda is None
    assert result.audit_metadata["ebitda"].source == "unextracted"


def test_input_validation_errors():
    """Verifies input validation on extract_missing_metrics."""
    extractor = LLMMetricExtractor()

    with pytest.raises(TypeError, match="statement_text must be a string"):
        extractor.extract_missing_metrics(123, {})  # type: ignore

    with pytest.raises(TypeError, match="current_metrics must be a dict"):
        extractor.extract_missing_metrics("text", "not_a_dict")  # type: ignore


def test_dto_serialization_and_fields():
    """Verifies ExtractedFinancialMetricsDTO Pydantic model serialization."""
    dto = ExtractedFinancialMetricsDTO(
        document_id="doc1",
        fiscal_year="FY25",
        revenue=Decimal("1000.00"),
        audit_metadata={"revenue": MetricAuditMetadata(source="regex", confidence=1.0)},
    )
    assert dto.document_id == "doc1"
    assert dto.revenue == Decimal("1000.00")
    assert dto.currency == "INR"
    assert dto.audit_metadata["revenue"].confidence == 1.0
