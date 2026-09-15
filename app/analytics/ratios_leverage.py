"""Leverage & Coverage Ratios Calculator for Financial Analytics Engine (Module 7.3).

Responsible for:
1. Computing Debt-to-Equity (Total Debt / Shareholder Equity) with negative equity distress flag.
2. Computing Interest Coverage Ratio (EBIT / Interest Expense) with zero-debt check.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO


class LeverageRatiosDTO(BaseModel): #DTO containing computed leverage and coverage ratios (Debt-to-Equity, ICR) and diagnostic warnings
    """Data Transfer Object for leverage and coverage ratio calculation results."""

    debt_to_equity: Optional[float] = Field( #Capital structure leverage ratio (Total Debt / Shareholder Equity)
        default=None,
        description="Debt-to-Equity Ratio = Total Debt / Shareholder Equity.",
    )
    interest_coverage_ratio: Optional[float] = Field( #Debt servicing ability (Operating Income / Interest Expense)
        default=None,
        description="Interest Coverage Ratio = EBIT (Operating Income) / Interest Expense.",
    )
    warnings: List[str] = Field( #Warnings for missing inputs, zero division, or negative equity distress
        default_factory=list,
        description="Human-readable warnings for missing inputs or zero-division guards.",
    )


class LeverageCalculator: #Deterministic leverage and coverage ratios calculator with negative equity distress flags
    """Deterministic leverage and coverage ratios calculator with negative equity distress flags.

    Technical Tasks:
    1. Debt-to-Equity Formula with zero/negative equity safeguards.
    2. Interest Coverage Ratio Formula with zero-interest check.
    """

    @staticmethod
    def calculate( #Main entrypoint: computes Debt-to-Equity and Interest Coverage Ratio
        metrics: ExtractedFinancialMetricsDTO,
        interest_expense: Optional[Decimal] = None,
    ) -> LeverageRatiosDTO:
        """Computes D/E and ICR with negative equity distress flags.

        Args:
            metrics: Extracted financial line items from the analytics pipeline.
            interest_expense: Interest expense value for ICR calculation.
                              Passed separately as it is not a canonical 12-metric field.

        Returns:
            LeverageRatiosDTO with computed ratios and any guard warnings.
        """
        warnings: List[str] = [] #Collector for diagnostic warnings

        de = LeverageCalculator._compute_debt_to_equity(metrics, warnings) #Compute Debt-to-Equity
        icr = LeverageCalculator._compute_interest_coverage( #Compute Interest Coverage Ratio
            metrics, interest_expense, warnings
        )

        return LeverageRatiosDTO( #Return leverage DTO
            debt_to_equity=de,
            interest_coverage_ratio=icr,
            warnings=warnings,
        )

    @staticmethod
    def _compute_debt_to_equity( #Computes D/E = Total Debt / Shareholder Equity
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """D/E = Total Debt / Shareholder Equity.

        Handles:
        - total_debt == 0 → returns 0.0 (company has no debt).
        - shareholder_equity == 0 → None + warning.
        - shareholder_equity < 0 → None + negative-equity distress warning.
        """
        if metrics.total_debt is None: #Check if total debt was extracted
            warnings.append("D/E: total_debt is not available.")
            return None
        if metrics.shareholder_equity is None: #Check if shareholder equity was extracted
            warnings.append("D/E: shareholder_equity is not available.")
            return None
        if metrics.shareholder_equity == Decimal("0"): #Guard against division by zero if equity is zero
            warnings.append(
                "D/E: shareholder_equity is zero; cannot compute debt-to-equity ratio."
            )
            return None
        if metrics.shareholder_equity < Decimal("0"): #Negative equity indicates insolvency distress (accumulated losses exceed capital)
            warnings.append(
                "D/E: shareholder_equity is negative — company is in equity distress."
            )
            return None

        return float( #Calculate D/E ratio rounded to 2 decimal places (healthy benchmark is typically <= 1.5)
            (metrics.total_debt / metrics.shareholder_equity).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_interest_coverage( #Computes ICR = EBIT (Operating Income) / Interest Expense
        metrics: ExtractedFinancialMetricsDTO,
        interest_expense: Optional[Decimal],
        warnings: List[str],
    ) -> Optional[float]:
        """ICR = EBIT (Operating Income) / Interest Expense."""
        if metrics.operating_income is None: #Check if operating income was extracted
            warnings.append("ICR: operating_income (EBIT) is not available.")
            return None
        if interest_expense is None: #Check if interest expense was provided
            warnings.append("ICR: interest_expense is not available.")
            return None
        if interest_expense == Decimal("0"): #Guard against division by zero (zero interest means debt is debt-free or interest-free)
            warnings.append(
                "ICR: interest_expense is zero; cannot compute coverage ratio."
            )
            return None
        return float( #Calculate ICR rounded to 2 decimal places (healthy benchmark is typically >= 3.0)
            (metrics.operating_income / interest_expense).quantize(Decimal("0.01"))
        )
