"""Financial quantitative analytics engine: metrics extraction, ratios, health scores, and risk analysis."""

from app.analytics.synonym_matcher import StatementDomain, SynonymMatcher
from app.analytics.unit_normalizer import FinancialUnitNormalizer
from app.analytics.regex_extractor import RegexMetricExtractor
from app.analytics.llm_extractor import (
    ExtractedFinancialMetricsDTO,
    MetricAuditMetadata,
    LLMMetricExtractor,
)
from app.analytics.ratios_profitability import (
    ProfitabilityRatiosDTO,
    ProfitabilityCalculator,
)
from app.analytics.ratios_liquidity import (
    LiquidityRatiosDTO,
    LiquidityCalculator,
)
from app.analytics.ratios_leverage import (
    LeverageRatiosDTO,
    LeverageCalculator,
)

__all__ = [
    "StatementDomain",
    "SynonymMatcher",
    "FinancialUnitNormalizer",
    "RegexMetricExtractor",
    "ExtractedFinancialMetricsDTO",
    "MetricAuditMetadata",
    "LLMMetricExtractor",
    "ProfitabilityRatiosDTO",
    "ProfitabilityCalculator",
    "LiquidityRatiosDTO",
    "LiquidityCalculator",
    "LeverageRatiosDTO",
    "LeverageCalculator",
]
