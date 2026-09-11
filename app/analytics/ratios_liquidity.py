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


class LiquidityRatiosDTO(BaseModel):
    """Data Transfer Object for liquidity ratio calculation results."""

    current_ratio: Optional[float] = Field(
        default=None,
        description="Current Ratio = Current Assets / Current Liabilities.",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick Ratio = (Current Assets − Inventories) / Current Liabilities.",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Human-readable warnings for missing inputs or zero-division guards.",
    )


class LiquidityCalculator:
    """Deterministic liquidity ratios calculator with zero-denominator safeguards.

    Technical Tasks:
    1. Current Ratio Formula with zero-denominator protection.
    2. Quick Ratio Formula with inventory fallback to Current Assets if unstated.
    """

    @staticmethod
    def calculate(
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
        warnings: List[str] = []

        current_ratio = LiquidityCalculator._compute_current_ratio(metrics, warnings)
        quick_ratio = LiquidityCalculator._compute_quick_ratio(
            metrics, inventories, warnings
        )

        return LiquidityRatiosDTO(
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            warnings=warnings,
        )

    @staticmethod
    def _compute_current_ratio(
        metrics: ExtractedFinancialMetricsDTO, warnings: List[str]
    ) -> Optional[float]:
        """Current Ratio = Current Assets / Current Liabilities."""
        if metrics.current_assets is None:
            warnings.append("Current Ratio: current_assets is not available.")
            return None
        if metrics.current_liabilities is None:
            warnings.append("Current Ratio: current_liabilities is not available.")
            return None
        if metrics.current_liabilities == Decimal("0"):
            warnings.append(
                "Current Ratio: current_liabilities is zero; cannot compute ratio."
            )
            return None
        return float(
            (metrics.current_assets / metrics.current_liabilities).quantize(
                Decimal("0.01")
            )
        )

    @staticmethod
    def _compute_quick_ratio(
        metrics: ExtractedFinancialMetricsDTO,
        inventories: Optional[Decimal],
        warnings: List[str],
    ) -> Optional[float]:
        """Quick Ratio = (Current Assets − Inventories) / Current Liabilities.

        Falls back to Current Assets if inventories is None (inventory unstated).
        """
        if metrics.current_assets is None:
            warnings.append("Quick Ratio: current_assets is not available.")
            return None
        if metrics.current_liabilities is None:
            warnings.append("Quick Ratio: current_liabilities is not available.")
            return None
        if metrics.current_liabilities == Decimal("0"):
            warnings.append(
                "Quick Ratio: current_liabilities is zero; cannot compute ratio."
            )
            return None

        if inventories is not None:
            numerator = metrics.current_assets - inventories
        else:
            warnings.append(
                "Quick Ratio: inventories not provided; falling back to current_assets (assumes zero inventory)."
            )
            numerator = metrics.current_assets

        return float(
            (numerator / metrics.current_liabilities).quantize(Decimal("0.01"))
        )
