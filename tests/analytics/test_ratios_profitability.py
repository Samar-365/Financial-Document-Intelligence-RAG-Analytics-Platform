"""Unit tests for Module 7.1: Profitability Ratios Calculator."""

from decimal import Decimal

import pytest

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO
from app.analytics.ratios_profitability import (
    ProfitabilityCalculator,
    ProfitabilityRatiosDTO,
)


def _make_metrics(**overrides) -> ExtractedFinancialMetricsDTO:
    """Helper to construct metrics DTO with sane defaults for ratio tests."""
    defaults = {
        "document_id": "test-doc",
        "fiscal_year": "FY25",
        "revenue": Decimal("1000"),
        "operating_income": Decimal("155"),
        "net_income": Decimal("100"),
        "shareholder_equity": Decimal("500"),
        "total_assets": Decimal("2000"),
        "current_liabilities": Decimal("400"),
    }
    defaults.update(overrides)
    return ExtractedFinancialMetricsDTO(**defaults)


# ── OPM Tests ──


class TestOperatingProfitMargin:
    def test_opm_happy_path(self):
        """DoD: OPM = 15.5 for Revenue 1000 and EBIT 155."""
        result = ProfitabilityCalculator.calculate(_make_metrics())
        assert result.operating_profit_margin == 15.50

    def test_opm_zero_revenue(self):
        """Zero revenue should yield None with a warning."""
        result = ProfitabilityCalculator.calculate(
            _make_metrics(revenue=Decimal("0"))
        )
        assert result.operating_profit_margin is None
        assert any("revenue is zero" in w for w in result.warnings)

    def test_opm_missing_operating_income(self):
        """Missing operating_income yields None with a warning."""
        result = ProfitabilityCalculator.calculate(
            _make_metrics(operating_income=None)
        )
        assert result.operating_profit_margin is None
        assert any("operating_income is not available" in w for w in result.warnings)

    def test_opm_missing_revenue(self):
        """Missing revenue yields None with a warning."""
        result = ProfitabilityCalculator.calculate(_make_metrics(revenue=None))
        assert result.operating_profit_margin is None
        assert any("revenue is not available" in w for w in result.warnings)


# ── NPM Tests ──


class TestNetProfitMargin:
    def test_npm_happy_path(self):
        """NPM = 10.0 for Net Income 100 and Revenue 1000."""
        result = ProfitabilityCalculator.calculate(_make_metrics())
        assert result.net_profit_margin == 10.00

    def test_npm_zero_revenue(self):
        result = ProfitabilityCalculator.calculate(
            _make_metrics(revenue=Decimal("0"))
        )
        assert result.net_profit_margin is None
        assert any("NPM" in w and "zero" in w for w in result.warnings)


# ── ROE Tests ──


class TestReturnOnEquity:
    def test_roe_happy_path(self):
        """ROE = 100 / 500 × 100 = 20.00."""
        result = ProfitabilityCalculator.calculate(_make_metrics())
        assert result.return_on_equity == 20.00

    def test_roe_zero_equity(self):
        result = ProfitabilityCalculator.calculate(
            _make_metrics(shareholder_equity=Decimal("0"))
        )
        assert result.return_on_equity is None
        assert any("zero or negative" in w for w in result.warnings)

    def test_roe_negative_equity(self):
        result = ProfitabilityCalculator.calculate(
            _make_metrics(shareholder_equity=Decimal("-200"))
        )
        assert result.return_on_equity is None
        assert any("zero or negative" in w for w in result.warnings)


# ── ROCE Tests ──


class TestReturnOnCapitalEmployed:
    def test_roce_happy_path(self):
        """ROCE = 155 / (2000 − 400) × 100 = 9.69."""
        result = ProfitabilityCalculator.calculate(_make_metrics())
        assert result.return_on_capital_employed == 9.69

    def test_roce_zero_capital_employed(self):
        """Capital Employed = 0 should yield None."""
        result = ProfitabilityCalculator.calculate(
            _make_metrics(total_assets=Decimal("400"), current_liabilities=Decimal("400"))
        )
        assert result.return_on_capital_employed is None
        assert any("capital_employed" in w for w in result.warnings)

    def test_roce_negative_capital_employed(self):
        """Capital Employed < 0 should yield None."""
        result = ProfitabilityCalculator.calculate(
            _make_metrics(total_assets=Decimal("300"), current_liabilities=Decimal("500"))
        )
        assert result.return_on_capital_employed is None


# ── Edge Cases ──


class TestProfitabilityEdgeCases:
    def test_all_none_metrics(self):
        """All-None input should return all-None ratios without crashing."""
        metrics = ExtractedFinancialMetricsDTO(
            document_id="empty", fiscal_year="FY25"
        )
        result = ProfitabilityCalculator.calculate(metrics)
        assert result.operating_profit_margin is None
        assert result.net_profit_margin is None
        assert result.return_on_equity is None
        assert result.return_on_capital_employed is None
        assert len(result.warnings) > 0

    def test_dto_type(self):
        """Result must be a ProfitabilityRatiosDTO."""
        result = ProfitabilityCalculator.calculate(_make_metrics())
        assert isinstance(result, ProfitabilityRatiosDTO)

    def test_negative_margins(self):
        """Negative operating income should produce negative margins."""
        result = ProfitabilityCalculator.calculate(
            _make_metrics(operating_income=Decimal("-50"), net_income=Decimal("-30"))
        )
        assert result.operating_profit_margin == -5.00
        assert result.net_profit_margin == -3.00
