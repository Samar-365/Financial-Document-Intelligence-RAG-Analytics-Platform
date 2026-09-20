import pytest
from app.analytics.synonym_matcher import StatementDomain, SynonymMatcher


def test_accounting_variations_dod():
    """Verifies Definition of Done (DoD):

    Successfully maps 20+ accounting variations to canonical metric keys.
    """
    variations_to_expected = {
        # Indian GAAP / Ind AS variations
        "Turnover": "revenue",
        "Revenue from Operations": "revenue",
        "Total Turnover": "revenue",
        "Gross Turnover": "revenue",
        "Operating Profit": "operating_income",
        "Profit Before Interest and Tax (PBIT)": "operating_income",
        "PBIT": "operating_income",
        "EBIT": "operating_income",
        "Profit After Tax": "net_income",
        "PAT": "net_income",
        "Profit for the year": "net_income",
        "Net Profit": "net_income",
        "Net Worth": "shareholder_equity",
        "Share Capital and Reserves": "shareholder_equity",
        "Equity Share Capital": "shareholder_equity",
        "Total Borrowings": "total_debt",
        "Borrowings": "total_debt",
        "Cash and Bank Balances": "cash",
        "Cash generated from operations": "operating_cash_flow",
        # US GAAP / IFRS / Global variations
        "Net Sales": "revenue",
        "Sales Revenue": "revenue",
        "Total Revenues": "revenue",
        "Gross Profit": "gross_profit",
        "Gross Margin": "gross_profit",
        "Operating Income": "operating_income",
        "EBITDA": "ebitda",
        "Earnings Before Interest, Taxes, Depreciation and Amortization": "ebitda",
        "Diluted EPS": "eps",
        "Basic Earnings Per Share": "eps",
        "Total Non-Current and Current Assets": "total_assets",
        "Total Liabilities": "total_liabilities",
        "Shareholders' Equity": "shareholder_equity",
        "Total Debt": "total_debt",
        "Cash and Cash Equivalents": "cash",
        "Operating Cash Flow": "operating_cash_flow",
        "Free Cash Flow": "free_cash_flow",
        "FCF": "free_cash_flow",
    }

    assert len(variations_to_expected) >= 20  # Explicitly assert 20+ count for DoD

    for raw_label, expected_metric in variations_to_expected.items():
        resolved = SynonymMatcher.resolve_metric_name(raw_label)
        assert resolved == expected_metric, (
            f"Failed to map '{raw_label}': got '{resolved}', expected '{expected_metric}'"
        )


def test_revenue_aliases():
    """Verifies that all standard revenue variations map to 'revenue'."""
    labels = [
        "Revenue",
        "REVENUE",
        "Revenues",
        "Revenue from operations",
        "Net Sales",
        "Sales",
        "Turnover",
        "Total Revenue",
        "Net Revenues",
        "Gross Sales",
        "Income from Operations",
    ]
    for label in labels:
        assert SynonymMatcher.resolve_metric_name(label) == "revenue"


def test_profitability_aliases():
    """Verifies operating profit, net income, ebitda, and gross profit resolution."""
    assert SynonymMatcher.resolve_metric_name("Gross Profit") == "gross_profit"
    assert SynonymMatcher.resolve_metric_name("Gross Margin") == "gross_profit"

    assert SynonymMatcher.resolve_metric_name("Operating Profit") == "operating_income"
    assert SynonymMatcher.resolve_metric_name("Operating Income") == "operating_income"
    assert SynonymMatcher.resolve_metric_name("EBIT") == "operating_income"
    assert SynonymMatcher.resolve_metric_name("Earnings before interest and tax") == "operating_income"

    assert SynonymMatcher.resolve_metric_name("EBITDA") == "ebitda"
    assert (
        SynonymMatcher.resolve_metric_name(
            "Earnings before interest, tax, depreciation and amortization"
        )
        == "ebitda"
    )

    assert SynonymMatcher.resolve_metric_name("Net Income") == "net_income"
    assert SynonymMatcher.resolve_metric_name("Profit After Tax") == "net_income"
    assert SynonymMatcher.resolve_metric_name("PAT") == "net_income"
    assert SynonymMatcher.resolve_metric_name("Net Profit") == "net_income"


def test_balance_sheet_aliases():
    """Verifies balance sheet metrics resolution."""
    assert SynonymMatcher.resolve_metric_name("Total Assets") == "total_assets"
    assert SynonymMatcher.resolve_metric_name("Total Liabilities") == "total_liabilities"
    assert SynonymMatcher.resolve_metric_name("Shareholders' Equity") == "shareholder_equity"
    assert SynonymMatcher.resolve_metric_name("Net Worth") == "shareholder_equity"
    assert SynonymMatcher.resolve_metric_name("Total Borrowings") == "total_debt"
    assert SynonymMatcher.resolve_metric_name("Total Debt") == "total_debt"
    assert SynonymMatcher.resolve_metric_name("Cash and Cash Equivalents") == "cash"
    assert SynonymMatcher.resolve_metric_name("Cash & Cash Equivalents") == "cash"
    assert SynonymMatcher.resolve_metric_name("Current Assets") == "current_assets"
    assert SynonymMatcher.resolve_metric_name("Current Liabilities") == "current_liabilities"


def test_cash_flow_aliases():
    """Verifies cash flow metrics resolution."""
    assert (
        SynonymMatcher.resolve_metric_name("Cash flow from operating activities")
        == "operating_cash_flow"
    )
    assert (
        SynonymMatcher.resolve_metric_name("Cash generated from operations")
        == "operating_cash_flow"
    )
    assert SynonymMatcher.resolve_metric_name("Free Cash Flow") == "free_cash_flow"
    assert SynonymMatcher.resolve_metric_name("FCF") == "free_cash_flow"


def test_statement_domain_classification():
    """Verifies Task 2 (Statement Classification Rules) into P&L, Balance Sheet, and Cash Flow."""
    # From canonical key
    assert SynonymMatcher.get_statement_domain("revenue") == StatementDomain.P_AND_L
    assert SynonymMatcher.get_statement_domain("operating_income") == StatementDomain.P_AND_L
    assert SynonymMatcher.get_statement_domain("net_income") == StatementDomain.P_AND_L
    assert SynonymMatcher.get_statement_domain("ebitda") == StatementDomain.P_AND_L
    assert SynonymMatcher.get_statement_domain("eps") == StatementDomain.P_AND_L

    assert SynonymMatcher.get_statement_domain("total_assets") == StatementDomain.BALANCE_SHEET
    assert SynonymMatcher.get_statement_domain("total_liabilities") == StatementDomain.BALANCE_SHEET
    assert SynonymMatcher.get_statement_domain("shareholder_equity") == StatementDomain.BALANCE_SHEET
    assert SynonymMatcher.get_statement_domain("total_debt") == StatementDomain.BALANCE_SHEET
    assert SynonymMatcher.get_statement_domain("cash") == StatementDomain.BALANCE_SHEET

    assert (
        SynonymMatcher.get_statement_domain("operating_cash_flow") == StatementDomain.CASH_FLOW
    )
    assert SynonymMatcher.get_statement_domain("free_cash_flow") == StatementDomain.CASH_FLOW

    # From raw labels directly
    assert (
        SynonymMatcher.get_statement_domain("Turnover") == StatementDomain.P_AND_L
    )
    assert (
        SynonymMatcher.get_statement_domain("Total Borrowings")
        == StatementDomain.BALANCE_SHEET
    )
    assert (
        SynonymMatcher.get_statement_domain("Cash generated from operations")
        == StatementDomain.CASH_FLOW
    )


def test_label_normalization_and_formatting_tolerance():
    """Verifies tolerance to enumeration numbers, bullets, footnotes, colons, and formatting."""
    assert SynonymMatcher.resolve_metric_name("1. Revenue from operations:") == "revenue"
    assert SynonymMatcher.resolve_metric_name("• Operating profit") == "operating_income"
    assert SynonymMatcher.resolve_metric_name("Net sales (note 24)") == "revenue"
    assert SynonymMatcher.resolve_metric_name("a) Profit after tax:") == "net_income"
    assert SynonymMatcher.resolve_metric_name("Cash & bank balances") == "cash"
    assert SynonymMatcher.resolve_metric_name("   Total   Assets   ") == "total_assets"


def test_unmatched_unknown_labels():
    """Verifies that non-financial or unrecognized strings return None."""
    assert SynonymMatcher.resolve_metric_name("Director's Report") is None
    assert SynonymMatcher.resolve_metric_name("Auditor Signature") is None
    assert SynonymMatcher.resolve_metric_name("Independent Auditor's Report") is None
    assert SynonymMatcher.resolve_metric_name("Page 45 of 120") is None
    assert SynonymMatcher.resolve_metric_name("") is None
    assert SynonymMatcher.resolve_metric_name("   ") is None

    assert SynonymMatcher.get_statement_domain("NonExistentMetric") is None


def test_input_validation_errors():
    """Verifies that non-string inputs raise TypeError."""
    with pytest.raises(TypeError, match="line_label must be a string"):
        SynonymMatcher.resolve_metric_name(123)  # type: ignore

    with pytest.raises(TypeError, match="line_label must be a string"):
        SynonymMatcher.resolve_metric_name(None)  # type: ignore

    with pytest.raises(TypeError, match="metric_or_label must be a string"):
        SynonymMatcher.get_statement_domain(None)  # type: ignore

    with pytest.raises(TypeError, match="line_label must be a string"):
        SynonymMatcher.normalize_label(["invalid"])  # type: ignore


def test_get_all_aliases():
    """Verifies retrieving all aliases for a canonical metric."""
    revenue_aliases = SynonymMatcher.get_all_aliases("revenue")
    assert len(revenue_aliases) > 5
    assert "turnover" in revenue_aliases
    assert "net sales" in revenue_aliases

    assert SynonymMatcher.get_all_aliases("unknown_metric") == []
