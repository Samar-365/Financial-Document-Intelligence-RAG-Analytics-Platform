"""Unit tests for Module 7.3: Leverage & Coverage Ratios Calculator."""

from decimal import Decimal

import pytest

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO
from app.analytics.ratios_leverage import (
    LeverageCalculator,
    LeverageRatiosDTO,
)


def _make_metrics(**overrides) -> ExtractedFinancialMetricsDTO:
    """Helper to construct metrics DTO with sane defaults for leverage tests."""
    defaults = {
        "document_id": "test-doc",
        "fiscal_year": "FY25",
        "total_debt": Decimal("400"),
        "shareholder_equity": Decimal("800"),
        "operating_income": Decimal("200"),
    }
    defaults.update(overrides)
    return ExtractedFinancialMetricsDTO(**defaults)


# ── Debt-to-Equity Tests ──


class TestDebtToEquity:
    def test_de_happy_path(self):
        """D/E = 400 / 800 = 0.50."""
        result = LeverageCalculator.calculate(_make_metrics())
        assert result.debt_to_equity == 0.50

    def test_de_zero_debt(self):
        """Zero debt should return D/E = 0.00."""
        result = LeverageCalculator.calculate(
            _make_metrics(total_debt=Decimal("0"))
        )
        assert result.debt_to_equity == 0.00

    def test_de_zero_equity(self):
        """Zero equity should yield None with a warning."""
        result = LeverageCalculator.calculate(
            _make_metrics(shareholder_equity=Decimal("0"))
        )
        assert result.debt_to_equity is None
        assert any("zero" in w for w in result.warnings)

    def test_de_negative_equity(self):
        """Negative equity should yield None with distress warning."""
        result = LeverageCalculator.calculate(
            _make_metrics(shareholder_equity=Decimal("-200"))
        )
        assert result.debt_to_equity is None
        assert any("equity distress" in w for w in result.warnings)

    def test_de_missing_debt(self):
        """Missing total_debt yields None."""
        result = LeverageCalculator.calculate(_make_metrics(total_debt=None))
        assert result.debt_to_equity is None
        assert any("total_debt is not available" in w for w in result.warnings)

    def test_de_missing_equity(self):
        """Missing shareholder_equity yields None."""
        result = LeverageCalculator.calculate(
            _make_metrics(shareholder_equity=None)
        )
        assert result.debt_to_equity is None
        assert any("shareholder_equity is not available" in w for w in result.warnings)


# ── Interest Coverage Ratio Tests ──


class TestInterestCoverageRatio:
    def test_icr_happy_path(self):
        """ICR = 200 / 50 = 4.00."""
        result = LeverageCalculator.calculate(
            _make_metrics(), interest_expense=Decimal("50")
        )
        assert result.interest_coverage_ratio == 4.00

    def test_icr_zero_interest(self):
        """Zero interest expense should yield None with a warning."""
        result = LeverageCalculator.calculate(
            _make_metrics(), interest_expense=Decimal("0")
        )
        assert result.interest_coverage_ratio is None
        assert any("interest_expense is zero" in w for w in result.warnings)

    def test_icr_missing_interest(self):
        """Missing interest_expense yields None."""
        result = LeverageCalculator.calculate(_make_metrics(), interest_expense=None)
        assert result.interest_coverage_ratio is None
        assert any("interest_expense is not available" in w for w in result.warnings)

    def test_icr_missing_operating_income(self):
        """Missing operating_income yields None."""
        result = LeverageCalculator.calculate(
            _make_metrics(operating_income=None), interest_expense=Decimal("50")
        )
        assert result.interest_coverage_ratio is None
        assert any("operating_income" in w for w in result.warnings)


# ── Edge Cases ──


class TestLeverageEdgeCases:
    def test_all_none_metrics(self):
        """All-None input should return all-None ratios without crashing."""
        metrics = ExtractedFinancialMetricsDTO(
            document_id="empty", fiscal_year="FY25"
        )
        result = LeverageCalculator.calculate(metrics)
        assert result.debt_to_equity is None
        assert result.interest_coverage_ratio is None
        assert len(result.warnings) > 0

    def test_dto_type(self):
        """Result must be a LeverageRatiosDTO."""
        result = LeverageCalculator.calculate(_make_metrics())
        assert isinstance(result, LeverageRatiosDTO)

    def test_high_leverage(self):
        """High D/E should compute correctly."""
        result = LeverageCalculator.calculate(
            _make_metrics(total_debt=Decimal("5000"), shareholder_equity=Decimal("1000"))
        )
        assert result.debt_to_equity == 5.00
