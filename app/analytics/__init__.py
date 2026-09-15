"""Financial quantitative analytics engine: metrics extraction, ratios, health scores, and risk analysis."""

# Module 6.1: Financial terminology synonym matching & statement classification
from app.analytics.synonym_matcher import StatementDomain, SynonymMatcher
# Module 6.2: Financial magnitude unit normalizer (Millions, Billions, Thousands, Crores)
from app.analytics.unit_normalizer import FinancialUnitNormalizer
# Module 6.3: Regex-based financial metric extractor from markdown tables
from app.analytics.regex_extractor import RegexMetricExtractor
# Module 6.4: Few-shot LLM structured metric extractor with fallback
from app.analytics.llm_extractor import (
    ExtractedFinancialMetricsDTO,
    MetricAuditMetadata,
    LLMMetricExtractor,
)
# Module 7.1: Profitability ratios calculation (Net Margin, Operating Margin, ROA, ROE)
from app.analytics.ratios_profitability import (
    ProfitabilityRatiosDTO,
    ProfitabilityCalculator,
)
# Module 7.2: Liquidity ratios calculation (Current Ratio, Quick Ratio, Cash Ratio)
from app.analytics.ratios_liquidity import (
    LiquidityRatiosDTO,
    LiquidityCalculator,
)
# Module 7.3: Leverage & Solvency ratios calculation (Debt-to-Equity, Debt-to-Assets, Interest Coverage)
from app.analytics.ratios_leverage import (
    LeverageRatiosDTO,
    LeverageCalculator,
)
# Module 8.1: Growth & Profitability dimensional health scoring
from app.analytics.health_growth_profit import (
    DimensionScoreDTO,
    GrowthProfitScorer,
)
# Module 8.2: Solvency & Cash Flow dimensional health scoring
from app.analytics.health_solvency_cash import (
    SolvencyCashScorer,
)
# Module 8.3: Corporate health score aggregation, letter grading, and risk classification
from app.analytics.health_scorer import (
    CorporateHealthReportDTO,
    HealthScoreAggregator,
)
# Module 9.1: Risk factor disclosure parser and boilerplate noise filtering
from app.analytics.risk_parser import RiskDisclosureParser

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
    "DimensionScoreDTO",
    "GrowthProfitScorer",
    "SolvencyCashScorer",
    "CorporateHealthReportDTO",
    "HealthScoreAggregator",
    "RiskDisclosureParser",
]


