from decimal import Decimal
import pytest

from app.analytics.regex_extractor import RegexMetricExtractor


def test_extract_metrics_dod():
    """Verifies Definition of Done (DoD):

    Accurately extracts Revenue, EBIT, and PAT from standard annual report tabular disclosures.
    """
    table = (
        "| Particulars (₹ in Crores) | FY24 | FY25 |\n"
        "| :--- | :--- | :--- |\n"
        "| Revenue from Operations | 10,200.00 | 11,450.00 |\n"
        "| Operating Profit (EBIT) | 1,800.00 | 2,150.00 |\n"
        "| Profit After Tax (PAT) | 1,200.00 | 1,450.00 |\n"
    )

    extractor = RegexMetricExtractor()
    metrics = extractor.extract_from_tables([table], target_year="FY25")

    # Verify Revenue, EBIT, and PAT are accurately extracted
    assert "revenue" in metrics
    assert "operating_income" in metrics
    assert "net_income" in metrics

    assert metrics["revenue"] == Decimal("114500000000.00")
    assert metrics["operating_income"] == Decimal("21500000000.00")
    assert metrics["net_income"] == Decimal("14500000000.00")


def test_multi_year_column_alignment():
    """Verifies Task 2 (Multi-Year Column Alignment): correctly aligns FY24 vs FY25 column data."""
    table = (
        "| Financial Summary | FY 2024 | FY 2025 |\n"
        "| :--- | :--- | :--- |\n"
        "| Net Sales (USD in Millions) | 5,000.00 | 6,200.00 |\n"
        "| Operating Income | 750.00 | 950.00 |\n"
    )

    extractor = RegexMetricExtractor()

    # Extract FY 2024
    metrics_24 = extractor.extract_from_tables([table], target_year="2024")
    assert metrics_24["revenue"] == Decimal("5000000000.00")
    assert metrics_24["operating_income"] == Decimal("750000000.00")

    # Extract FY 2025
    metrics_25 = extractor.extract_from_tables([table], target_year="FY25")
    assert metrics_25["revenue"] == Decimal("6200000000.00")
    assert metrics_25["operating_income"] == Decimal("950000000.00")


def test_indian_unit_crores_and_lakhs():
    """Verifies table unit scaling with Crores and Lakhs."""
    crore_table = (
        "Statement of Profit and Loss (Rs in Crores)\n"
        "| Metric | 31-Mar-2024 | 31-Mar-2025 |\n"
        "| :--- | :--- | :--- |\n"
        "| Turnover | 800.50 | 950.25 |\n"
    )

    extractor = RegexMetricExtractor()
    m_cr = extractor.extract_from_tables([crore_table], target_year="2025")
    assert m_cr["revenue"] == Decimal("9502500000.00")

    lakh_table = (
        "Income Statement (in Lakhs)\n"
        "| Line Item | FY24 | FY25 |\n"
        "| :--- | :--- | :--- |\n"
        "| EBITDA | 250.00 | 320.00 |\n"
    )
    m_lakh = extractor.extract_from_tables([lakh_table], target_year="FY25")
    assert m_lakh["ebitda"] == Decimal("32000000.00")


def test_accounting_parentheses_loss_extraction():
    """Verifies extraction of negative figures in parentheses from tables."""
    table = (
        "| Statement of Income (in Millions) | FY25 |\n"
        "| :--- | :--- |\n"
        "| Total Revenues | 1,200.00 |\n"
        "| Operating Profit (Loss) | (150.50) |\n"
    )

    extractor = RegexMetricExtractor()
    metrics = extractor.extract_from_tables([table], target_year="FY25")
    assert metrics["revenue"] == Decimal("1200000000.00")
    assert metrics["operating_income"] == Decimal("-150500000.00")


def test_multiple_tables_aggregation():
    """Verifies that metrics across multiple financial statement tables are combined."""
    pnl_table = (
        "| Income Statement (in Millions) | 2025 |\n"
        "| :--- | :--- |\n"
        "| Revenue from operations | 3,500.00 |\n"
        "| Profit after tax | 420.00 |\n"
    )

    balance_sheet = (
        "| Balance Sheet (in Millions) | 2025 |\n"
        "| :--- | :--- |\n"
        "| Total Assets | 12,000.00 |\n"
        "| Total Borrowings | 2,800.00 |\n"
        "| Cash and Cash Equivalents | 650.00 |\n"
    )

    extractor = RegexMetricExtractor()
    combined = extractor.extract_from_tables([pnl_table, balance_sheet], target_year="2025")

    assert combined["revenue"] == Decimal("3500000000.00")
    assert combined["net_income"] == Decimal("420000000.00")
    assert combined["total_assets"] == Decimal("12000000000.00")
    assert combined["total_debt"] == Decimal("2800000000.00")
    assert combined["cash"] == Decimal("650000000.00")


def test_unmatched_year_returns_empty():
    """Verifies that when target_year is not present in the table headers, no metrics are extracted."""
    table = (
        "| Particulars | FY20 | FY21 |\n"
        "| :--- | :--- | :--- |\n"
        "| Revenue | 100 | 120 |\n"
    )

    extractor = RegexMetricExtractor()
    assert extractor.extract_from_tables([table], target_year="FY25") == {}


def test_empty_tables_list():
    """Verifies that passing empty tables list returns empty dictionary."""
    extractor = RegexMetricExtractor()
    assert extractor.extract_from_tables([], target_year="FY25") == {}


def test_input_validation_errors():
    """Verifies input validation on extract_from_tables."""
    extractor = RegexMetricExtractor()

    with pytest.raises(TypeError, match="markdown_tables must be a list"):
        extractor.extract_from_tables("not_a_list", "FY25")  # type: ignore

    with pytest.raises(TypeError, match="not a string"):
        extractor.extract_from_tables([123], "FY25")  # type: ignore

    with pytest.raises(TypeError, match="target_year must be a string"):
        extractor.extract_from_tables([], 2025)  # type: ignore

    with pytest.raises(ValueError, match="target_year cannot be empty"):
        extractor.extract_from_tables([], "   ")
