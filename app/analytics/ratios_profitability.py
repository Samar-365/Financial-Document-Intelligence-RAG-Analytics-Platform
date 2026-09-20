"""Profitability Ratios Calculator for Financial Analytics Engine (Module 7.1).

Responsible for:
1. Computing Operating Profit Margin (OPM) and Net Profit Margin (NPM) with zero-revenue division guards.
2. Computing Return on Equity (ROE) and Return on Capital Employed (ROCE), asserting capital employed > 0.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO


class ProfitabilityRatiosDTO(BaseModel): #DTO containing computed profitability ratios (OPM, NPM, ROE, ROCE) and diagnostic warnings
    """Data Transfer Object for profitability ratio calculation results."""

    operating_profit_margin: Optional[float] = Field( #Operating profit percentage of revenue (Operating Income / Revenue * 100)
        default=None,
        description="Operating Profit Margin (%) = Operating Income / Revenue × 100.",
    )
    net_profit_margin: Optional[float] = Field( #Net profit percentage of revenue (Net Income / Revenue * 100)
        default=None,
        description="Net Profit Margin (%) = Net Income / Revenue × 100.",
    )
    return_on_equity: Optional[float] = Field( #Return on shareholder equity (Net Income / Shareholder Equity * 100)
        default=None,
        description="Return on Equity (%) = Net Income / Shareholder Equity × 100.",
    )
    return_on_capital_employed: Optional[float] = Field( #Operating efficiency on invested capital (EBIT / Capital Employed * 100)
        default=None,
        description="Return on Capital Employed (%) = Operating Income / Capital Employed × 100.",
    )
    warnings: List[str] = Field( #Human-readable warnings if inputs are missing or denominator is zero
        default_factory=list,
        description="Human-readable warnings for missing inputs or zero-division guards.",
    )


class ProfitabilityCalculator: #Deterministic profitability ratios calculator with zero-division protections
    """Deterministic profitability ratios calculator with zero-division protections.

    Technical Tasks:
    1. Operating & Net Margin Formulas: OPM and NPM with zero-revenue division guards.
    2. Return Ratios Formulas: ROE and ROCE with capital employed > 0 assertion.
    """

    @staticmethod
    def calculate(metrics: ExtractedFinancialMetricsDTO) -> ProfitabilityRatiosDTO: #Main entrypoint: executes all profitability formulas with division guards
        """Computes OPM, NPM, ROE, ROCE with zero-division protections.

        Args:
            metrics: Extracted financial line items from the analytics pipeline.

        Returns:
            ProfitabilityRatiosDTO with computed ratios and any guard warnings.
        """
        warnings: List[str] = [] #Collector for warnings when data is missing or invalid
        opm: Optional[float] = None
        npm: Optional[float] = None
        roe: Optional[float] = None
        roce: Optional[float] = None

        # ── Task 1: Operating Profit Margin (OPM) ──
        opm = ProfitabilityCalculator._compute_opm(metrics, warnings) #Calculate Operating Profit Margin

        # ── Task 1: Net Profit Margin (NPM) ──
        npm = ProfitabilityCalculator._compute_npm(metrics, warnings) #Calculate Net Profit Margin

        # ── Task 2: Return on Equity (ROE) ──
        roe = ProfitabilityCalculator._compute_roe(metrics, warnings) #Calculate Return on Equity

        # ── Task 2: Return on Capital Employed (ROCE) ──
        roce = ProfitabilityCalculator._compute_roce(metrics, warnings) #Calculate Return on Capital Employed

        return ProfitabilityRatiosDTO( #Return packaged profitability results
            operating_profit_margin=opm,
            net_profit_margin=npm,
            return_on_equity=roe,
            return_on_capital_employed=roce,
            warnings=warnings,
        )

    @staticmethod
    def _compute_opm( #Computes Operating Profit Margin: (Operating Income / Revenue) * 100
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """OPM = Operating Income / Revenue × 100."""
        if metrics.operating_income is None: #Check if operating income exists
            warnings.append("OPM: operating_income is not available.")
            return None
        if metrics.revenue is None: #Check if revenue exists
            warnings.append("OPM: revenue is not available.")
            return None
        if metrics.revenue == Decimal("0"): #Guard against division by zero if revenue is 0
            warnings.append("OPM: revenue is zero; cannot compute margin.")
            return None
        return float( #Calculate percentage rounded to 2 decimal places
            (metrics.operating_income / metrics.revenue * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_npm( #Computes Net Profit Margin: (Net Income / Revenue) * 100
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """NPM = Net Income / Revenue × 100."""
        if metrics.net_income is None: #Check if net income exists
            warnings.append("NPM: net_income is not available.")
            return None
        if metrics.revenue is None: #Check if revenue exists
            warnings.append("NPM: revenue is not available.")
            return None
        if metrics.revenue == Decimal("0"): #Guard against division by zero if revenue is 0
            warnings.append("NPM: revenue is zero; cannot compute margin.")
            return None
        return float( #Calculate percentage rounded to 2 decimal places
            (metrics.net_income / metrics.revenue * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_roe( #Computes Return on Equity: (Net Income / Shareholder Equity) * 100
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """ROE = Net Income / Shareholder Equity × 100."""
        if metrics.net_income is None: #Check if net income exists
            warnings.append("ROE: net_income is not available.")
            return None
        if metrics.shareholder_equity is None: #Check if shareholder equity exists
            warnings.append("ROE: shareholder_equity is not available.")
            return None
        if metrics.shareholder_equity <= Decimal("0"): #Equity must be positive (negative equity means liabilities exceed assets)
            warnings.append(
                "ROE: shareholder_equity is zero or negative; cannot compute return."
            )
            return None
        return float( #Calculate return percentage rounded to 2 decimal places
            (metrics.net_income / metrics.shareholder_equity * Decimal("100")).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_roce( #Computes ROCE: (Operating Income / Capital Employed) * 100
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """ROCE = Operating Income / Capital Employed × 100.

        Capital Employed = Total Assets − Current Liabilities.
        """
        if metrics.operating_income is None: #Check if operating income exists
            warnings.append("ROCE: operating_income is not available.")
            return None
        if metrics.total_assets is None: #Check if total assets exists
            warnings.append("ROCE: total_assets is not available.")
            return None
        if metrics.current_liabilities is None: #Check if current liabilities exists
            warnings.append("ROCE: current_liabilities is not available.")
            return None

        capital_employed = metrics.total_assets - metrics.current_liabilities #Capital Employed = Total Assets - Current Liabilities
        if capital_employed <= Decimal("0"): #Guard: capital employed must be strictly positive
            warnings.append(
                "ROCE: capital_employed (total_assets − current_liabilities) is zero or negative."
            )
            return None
        return float( #Calculate ROCE percentage rounded to 2 decimal places
            (
                metrics.operating_income / capital_employed * Decimal("100")
            ).quantize(Decimal("0.01"))
        )
