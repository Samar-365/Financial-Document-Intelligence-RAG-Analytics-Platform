"""Profitability Ratios Calculator for Financial Analytics Engine (Module 7.1).

Responsible for:
1. Computing Operating Profit Margin (OPM) and Net Profit Margin (NPM) with zero-revenue division guards.
2. Computing Return on Equity (ROE) and Return on Capital Employed (ROCE), asserting capital employed > 0.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO


class ProfitabilityRatiosDTO(BaseModel):
    """Data Transfer Object for profitability ratio calculation results."""

    operating_profit_margin: Optional[float] = Field(
        default=None,
        description="Operating Profit Margin (%) = Operating Income / Revenue × 100.",
    )
    net_profit_margin: Optional[float] = Field(
        default=None,
        description="Net Profit Margin (%) = Net Income / Revenue × 100.",
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on Equity (%) = Net Income / Shareholder Equity × 100.",
    )
    return_on_capital_employed: Optional[float] = Field(
        default=None,
        description="Return on Capital Employed (%) = Operating Income / Capital Employed × 100.",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Human-readable warnings for missing inputs or zero-division guards.",
    )


class ProfitabilityCalculator:
    """Deterministic profitability ratios calculator with zero-division protections.

    Technical Tasks:
    1. Operating & Net Margin Formulas: OPM and NPM with zero-revenue division guards.
    2. Return Ratios Formulas: ROE and ROCE with capital employed > 0 assertion.
    """

    @staticmethod
    def calculate(metrics: ExtractedFinancialMetricsDTO) -> ProfitabilityRatiosDTO:
        """Computes OPM, NPM, ROE, ROCE with zero-division protections.

        Args:
            metrics: Extracted financial line items from the analytics pipeline.

        Returns:
            ProfitabilityRatiosDTO with computed ratios and any guard warnings.
        """
        warnings: List[str] = []
        opm: Optional[float] = None
        npm: Optional[float] = None
        roe: Optional[float] = None
        roce: Optional[float] = None

        # ── Task 1: Operating Profit Margin (OPM) ──
        opm = ProfitabilityCalculator._compute_opm(metrics, warnings)

        # ── Task 1: Net Profit Margin (NPM) ──
        npm = ProfitabilityCalculator._compute_npm(metrics, warnings)

        # ── Task 2: Return on Equity (ROE) ──
        roe = ProfitabilityCalculator._compute_roe(metrics, warnings)

        # ── Task 2: Return on Capital Employed (ROCE) ──
        roce = ProfitabilityCalculator._compute_roce(metrics, warnings)

        return ProfitabilityRatiosDTO(
            operating_profit_margin=opm,
            net_profit_margin=npm,
            return_on_equity=roe,
            return_on_capital_employed=roce,
            warnings=warnings,
        )

    @staticmethod
    def _compute_opm(
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """OPM = Operating Income / Revenue × 100."""
        if metrics.operating_income is None:
            warnings.append("OPM: operating_income is not available.")
            return None
        if metrics.revenue is None:
            warnings.append("OPM: revenue is not available.")
            return None
        if metrics.revenue == Decimal("0"):
            warnings.append("OPM: revenue is zero; cannot compute margin.")
            return None
        return float(
            (metrics.operating_income / metrics.revenue * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_npm(
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """NPM = Net Income / Revenue × 100."""
        if metrics.net_income is None:
            warnings.append("NPM: net_income is not available.")
            return None
        if metrics.revenue is None:
            warnings.append("NPM: revenue is not available.")
            return None
        if metrics.revenue == Decimal("0"):
            warnings.append("NPM: revenue is zero; cannot compute margin.")
            return None
        return float(
            (metrics.net_income / metrics.revenue * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_roe(
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """ROE = Net Income / Shareholder Equity × 100."""
        if metrics.net_income is None:
            warnings.append("ROE: net_income is not available.")
            return None
        if metrics.shareholder_equity is None:
            warnings.append("ROE: shareholder_equity is not available.")
            return None
        if metrics.shareholder_equity <= Decimal("0"):
            warnings.append(
                "ROE: shareholder_equity is zero or negative; cannot compute return."
            )
            return None
        return float(
            (metrics.net_income / metrics.shareholder_equity * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_roce(
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """ROCE = Operating Income / Capital Employed × 100.

        Capital Employed = Total Assets − Current Liabilities.
        """
        if metrics.operating_income is None:
            warnings.append("ROCE: operating_income is not available.")
            return None
        if metrics.total_assets is None:
            warnings.append("ROCE: total_assets is not available.")
            return None
        if metrics.current_liabilities is None:
            warnings.append("ROCE: current_liabilities is not available.")
            return None

        capital_employed = metrics.total_assets - metrics.current_liabilities
        if capital_employed <= Decimal("0"):
            warnings.append(
                "ROCE: capital_employed (total_assets − current_liabilities) is zero or negative."
            )
            return None
        return float(
            (
                metrics.operating_income / capital_employed * Decimal("100")
            ).quantize(Decimal("0.01"))
        )
