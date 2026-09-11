"""Unit tests for Module 7.2: Liquidity & Solvency Ratios Calculator."""

from decimal import Decimal

import pytest

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO
from app.analytics.ratios_liquidity import (
    LiquidityCalculator,
    LiquidityRatiosDTO,
)


def _make_metrics(**overrides) -> ExtractedFinancialMetricsDTO:
    """Helper to construct metrics DTO with sane defaults for liquidity tests."""
    defaults = {
        "document_id": "test-doc",
        "fiscal_year": "FY25",
        "current_assets": Decimal("500"),
        "current_liabilities": Decimal("250"),
    }
    defaults.update(overrides)
    return ExtractedFinancialMetricsDTO(**defaults)


# ── Current Ratio Tests ──


class TestCurrentRatio:
    def test_current_ratio_happy_path(self):
        """Current Ratio = 500 / 250 = 2.00."""
        result = LiquidityCalculator.calculate(_make_metrics())
        assert result.current_ratio == 2.00

    def test_current_ratio_zero_liabilities(self):
        """Zero current liabilities should yield None with a warning."""
        result = LiquidityCalculator.calculate(
            _make_metrics(current_liabilities=Decimal("0"))
        )
        assert result.current_ratio is None
        assert any("current_liabilities is zero" in w for w in result.warnings)

    def test_current_ratio_missing_assets(self):
        """Missing current_assets yields None."""
        result = LiquidityCalculator.calculate(_make_metrics(current_assets=None))
        assert result.current_ratio is None
        assert any("current_assets is not available" in w for w in result.warnings)

    def test_current_ratio_missing_liabilities(self):
        """Missing current_liabilities yields None."""
        result = LiquidityCalculator.calculate(
            _make_metrics(current_liabilities=None)
        )
        assert result.current_ratio is None
        assert any("current_liabilities is not available" in w for w in result.warnings)


# ── Quick Ratio Tests ──


class TestQuickRatio:
    def test_quick_ratio_with_inventories(self):
        """Quick Ratio = (500 − 100) / 250 = 1.60."""
        result = LiquidityCalculator.calculate(
            _make_metrics(), inventories=Decimal("100")
        )
        assert result.quick_ratio == 1.60

    def test_quick_ratio_without_inventories_fallback(self):
        """Without inventories, Quick Ratio falls back to Current Ratio."""
        result = LiquidityCalculator.calculate(_make_metrics(), inventories=None)
        assert result.quick_ratio == 2.00
        assert any("falling back to current_assets" in w for w in result.warnings)

    def test_quick_ratio_zero_liabilities(self):
        result = LiquidityCalculator.calculate(
            _make_metrics(current_liabilities=Decimal("0")),
            inventories=Decimal("50"),
        )
        assert result.quick_ratio is None
        assert any("Quick Ratio" in w and "zero" in w for w in result.warnings)

    def test_quick_ratio_large_inventories(self):
        """Inventories larger than current assets yields negative Quick Ratio."""
        result = LiquidityCalculator.calculate(
            _make_metrics(), inventories=Decimal("600")
        )
        # (500 - 600) / 250 = -0.40
        assert result.quick_ratio == -0.40


# ── Edge Cases ──


class TestLiquidityEdgeCases:
    def test_all_none_metrics(self):
        """All-None input should return all-None ratios without crashing."""
        metrics = ExtractedFinancialMetricsDTO(
            document_id="empty", fiscal_year="FY25"
        )
        result = LiquidityCalculator.calculate(metrics)
        assert result.current_ratio is None
        assert result.quick_ratio is None
        assert len(result.warnings) > 0

    def test_dto_type(self):
        """Result must be a LiquidityRatiosDTO."""
        result = LiquidityCalculator.calculate(_make_metrics())
        assert isinstance(result, LiquidityRatiosDTO)

    def test_fractional_ratios(self):
        """Fractional values should be properly quantized."""
        result = LiquidityCalculator.calculate(
            _make_metrics(
                current_assets=Decimal("333"),
                current_liabilities=Decimal("200"),
            )
        )
        assert result.current_ratio == 1.66  # 333 / 200 = 1.665 → 1.66 (banker's rounding)
