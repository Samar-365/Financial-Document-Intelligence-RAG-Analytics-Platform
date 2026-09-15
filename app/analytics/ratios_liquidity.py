"""Liquidity & Solvency Ratios Calculator for Financial Analytics Engine (Module 7.2).

Responsible for:
1. Computing Current Ratio (Current Assets / Current Liabilities) with zero-denominator protection.
2. Computing Quick Ratio ((Current Assets − Inventories) / Current Liabilities) with fallback
   to Current Assets if inventory is unstated.
"""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.analytics.llm_extractor import ExtractedFinancialMetricsDTO


class LiquidityRatiosDTO(BaseModel): #DTO containing computed liquidity ratios (Current Ratio, Quick Ratio) and diagnostic warnings
    """Data Transfer Object for liquidity ratio calculation results."""

    current_ratio: Optional[float] = Field( #Ability to cover short-term liabilities with short-term assets (Current Assets / Current Liabilities)
        default=None,
        description="Current Ratio = Current Assets / Current Liabilities.",
    )
    quick_ratio: Optional[float] = Field( #Acid-test ratio measuring immediate liquidity ((Current Assets - Inventories) / Current Liabilities)
        default=None,
        description="Quick Ratio = (Current Assets − Inventories) / Current Liabilities.",
    )
    warnings: List[str] = Field( #Human-readable warnings for missing line items or zero-division guards
        default_factory=list,
        description="Human-readable warnings for missing inputs or zero-division guards.",
    )


class LiquidityCalculator: #Deterministic liquidity ratios calculator with zero-denominator safeguards
    """Deterministic liquidity ratios calculator with zero-denominator safeguards.

    Technical Tasks:
    1. Current Ratio Formula with zero-denominator protection.
    2. Quick Ratio Formula with inventory fallback to Current Assets if unstated.
    """

    @staticmethod
    def calculate( #Main entrypoint: computes Current Ratio and Quick Ratio
        metrics: ExtractedFinancialMetricsDTO,
        inventories: Optional[Decimal] = None,
    ) -> LiquidityRatiosDTO:
        """Computes Current and Quick ratios with zero-liability safeguards.

        Args:
            metrics: Extracted financial line items from the analytics pipeline.
            inventories: Optional inventory value. If None, Quick Ratio falls back
                         to Current Ratio (assumes zero inventories).

        Returns:
            LiquidityRatiosDTO with computed ratios and any guard warnings.
        """
        warnings: List[str] = [] #Collects warning messages if data is missing

        current_ratio = LiquidityCalculator._compute_current_ratio(metrics, warnings) #Compute Current Ratio
        quick_ratio = LiquidityCalculator._compute_quick_ratio( #Compute Quick Ratio
            metrics, inventories, warnings
        )

        return LiquidityRatiosDTO( #Return liquidity DTO
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            warnings=warnings,
        )

    @staticmethod
    def _compute_current_ratio( #Computes Current Ratio = Current Assets / Current Liabilities
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """Current Ratio = Current Assets / Current Liabilities."""
        if metrics.current_assets is None: #Check if current assets was extracted
            warnings.append("Current Ratio: current_assets is not available.")
            return None
        if metrics.current_liabilities is None: #Check if current liabilities was extracted
            warnings.append("Current Ratio: current_liabilities is not available.")
            return None
        if metrics.current_liabilities == Decimal("0"): #Guard against division by zero if liabilities are zero
            warnings.append(
                "Current Ratio: current_liabilities is zero; cannot compute ratio."
            )
            return None
        return float( #Calculate ratio rounded to 2 decimal places (healthy benchmark is typically >= 1.5)
            (metrics.current_assets / metrics.current_liabilities).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_quick_ratio( #Computes Quick Ratio = (Current Assets - Inventories) / Current Liabilities
        metrics: ExtractedFinancialMetricsDTO,
        inventories: Optional[Decimal],
        warnings: List[str],
    ) -> Optional[float]:
        """Quick Ratio = (Current Assets − Inventories) / Current Liabilities.

        Falls back to Current Assets if inventories is None (inventory unstated).
        """
        if metrics.current_assets is None: #Check if current assets was extracted
            warnings.append("Quick Ratio: current_assets is not available.")
            return None
        if metrics.current_liabilities is None: #Check if current liabilities was extracted
            warnings.append("Quick Ratio: current_liabilities is not available.")
            return None
        if metrics.current_liabilities == Decimal("0"): #Guard against division by zero
            warnings.append(
                "Quick Ratio: current_liabilities is zero; cannot compute ratio."
            )
            return None

        if inventories is not None: #If inventory was provided, subtract it from current assets
            numerator = metrics.current_assets - inventories
        else: #If inventory was not reported, assume zero inventory as safe fallback
            warnings.append(
                "Quick Ratio: inventories not provided; falling back to current_assets (assumes zero inventory)."
            )
            numerator = metrics.current_assets

        return float( #Calculate quick ratio rounded to 2 decimal places (healthy benchmark is typically >= 1.0)
            (numerator / metrics.current_liabilities).quantize(Decimal("0.01"))
        )
