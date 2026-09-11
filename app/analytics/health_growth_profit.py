"""Growth and Profitability Scoring Engine for Financial Analytics (Module 8.1).

Responsible for:
1. Scoring YoY Revenue Growth (>10% -> 100) and PAT Growth (>15% -> 100) using piecewise linear mapping.
2. Scoring Operating Profit Margin (>15% -> 100) and Net Profit Margin (>10% -> 100) with margin contraction deductions.
3. Generating structured DimensionScoreDTO with scores (0-100), qualitative grades, and explainable deductions.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DimensionScoreDTO(BaseModel):
    """Data Transfer Object representing a dimension score in the 5D corporate health model."""

    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Deterministic dimensional score bounded strictly between 0.0 and 100.0.",
    )
    grade: str = Field(
        ...,
        description="Qualitative rating category: 'Excellent', 'Good', 'Fair', or 'Poor'.",
    )
    deductions: List[str] = Field(
        default_factory=list,
        description="Detailed list of explainable deduction rationale strings.",
    )


def _determine_grade(score: float) -> str:
    """Maps a numerical score (0-100) to a qualitative grade tier."""
    if score >= 80.0:
        return "Excellent"
    if score >= 60.0:
        return "Good"
    if score >= 40.0:
        return "Fair"
    return "Poor"


class GrowthProfitScorer:
    """Evaluates corporate growth and profitability dimensions using deterministic financial benchmarks.

    Technical Tasks:
    1. Growth Scoring Engine (20% weight): YoY Revenue Growth and PAT Growth with piecewise linear mapping.
    2. Profitability Scoring Engine (25% weight): OPM and NPM scoring with margin contraction penalties.
    """

    # Benchmarks
    REV_GROWTH_BENCHMARK: float = 10.0  # >10% yields 100 pts
    PAT_GROWTH_BENCHMARK: float = 15.0  # >15% yields 100 pts
    OPM_BENCHMARK: float = 15.0         # >15% yields 100 pts
    NPM_BENCHMARK: float = 10.0         # >10% yields 100 pts

    def score_growth(
        self, rev_growth: Optional[float], pat_growth: Optional[float]
    ) -> DimensionScoreDTO:
        """Scores Growth dimension (20% weight) based on YoY Revenue Growth and PAT Growth.

        Piecewise linear mapping:
        - Revenue Growth:
            >= 10%: 100 pts
            [0%, 10%): 40 to 100 pts
            [-20%, 0%): 0 to 40 pts
            < -20%: 0 pts
        - PAT Growth:
            >= 15%: 100 pts
            [0%, 15%): 40 to 100 pts
            [-20%, 0%): 0 to 40 pts
            < -20%: 0 pts

        Args:
            rev_growth: Year-over-Year Revenue Growth percentage (e.g., 12.5 for 12.5%).
            pat_growth: Year-over-Year Profit After Tax Growth percentage (e.g., 18.0 for 18.0%).

        Returns:
            DimensionScoreDTO containing final score (0-100), grade, and deductions.
        """
        deductions: List[str] = []

        # 1. Score Revenue Growth component
        if rev_growth is None:
            rev_score = 0.0
            deductions.append("YoY Revenue Growth metric unavailable (0.0 / 100.0 pts assigned).")
        elif rev_growth >= self.REV_GROWTH_BENCHMARK:
            rev_score = 100.0
        elif rev_growth >= 0.0:
            # Linear between 40.0 and 100.0
            rev_score = 40.0 + (rev_growth / self.REV_GROWTH_BENCHMARK) * 60.0
            lost = 100.0 - rev_score
            deductions.append(
                f"Revenue growth of {rev_growth:.2f}% is below the {self.REV_GROWTH_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        elif rev_growth >= -20.0:
            # Linear between 0.0 and 40.0
            rev_score = max(0.0, 40.0 + (rev_growth / 20.0) * 40.0)
            lost = 100.0 - rev_score
            deductions.append(
                f"Revenue contraction of {abs(rev_growth):.2f}% severely penalizes growth (-{lost:.2f} pts)."
            )
        else:
            rev_score = 0.0
            deductions.append(
                f"Severe revenue contraction of {abs(rev_growth):.2f}% exceeds -20.0% (-100.00 pts)."
            )

        # 2. Score PAT Growth component
        if pat_growth is None:
            pat_score = 0.0
            deductions.append("YoY PAT Growth metric unavailable (0.0 / 100.0 pts assigned).")
        elif pat_growth >= self.PAT_GROWTH_BENCHMARK:
            pat_score = 100.0
        elif pat_growth >= 0.0:
            # Linear between 40.0 and 100.0
            pat_score = 40.0 + (pat_growth / self.PAT_GROWTH_BENCHMARK) * 60.0
            lost = 100.0 - pat_score
            deductions.append(
                f"PAT growth of {pat_growth:.2f}% is below the {self.PAT_GROWTH_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        elif pat_growth >= -20.0:
            # Linear between 0.0 and 40.0
            pat_score = max(0.0, 40.0 + (pat_growth / 20.0) * 40.0)
            lost = 100.0 - pat_score
            deductions.append(
                f"PAT contraction of {abs(pat_growth):.2f}% severely penalizes bottom-line growth (-{lost:.2f} pts)."
            )
        else:
            pat_score = 0.0
            deductions.append(
                f"Severe PAT contraction of {abs(pat_growth):.2f}% exceeds -20.0% (-100.00 pts)."
            )

        # Equal weighting within Growth dimension: 50% Revenue + 50% PAT
        composite_score = round(0.5 * rev_score + 0.5 * pat_score, 2)
        composite_score = max(0.0, min(100.0, composite_score))
        grade = _determine_grade(composite_score)

        return DimensionScoreDTO(
            score=composite_score,
            grade=grade,
            deductions=deductions,
        )

    def score_profitability(
        self, opm: Optional[float], npm: Optional[float]
    ) -> DimensionScoreDTO:
        """Scores Profitability dimension (25% weight) based on Operating Margin and Net Margin.

        Piecewise linear mapping:
        - Operating Profit Margin (OPM):
            >= 15%: 100 pts
            [0%, 15%): 30 to 100 pts
            < 0%: 0 pts (operating loss penalty)
        - Net Profit Margin (NPM):
            >= 10%: 100 pts
            [0%, 10%): 30 to 100 pts
            < 0%: 0 pts (net loss penalty)

        Deductions:
        - Deducts points when margins fall short of benchmark.
        - Deducts extra 10 points for severe margin contraction where operating profit is positive
          but wiped out to negative net profit (severe non-operating drag).

        Args:
            opm: Operating Profit Margin percentage (e.g., 18.5 for 18.5%).
            npm: Net Profit Margin percentage (e.g., 12.0 for 12.0%).

        Returns:
            DimensionScoreDTO containing final score (0-100), grade, and deductions.
        """
        deductions: List[str] = []

        # 1. Score Operating Profit Margin component
        if opm is None:
            opm_score = 0.0
            deductions.append("Operating Profit Margin (OPM) unavailable (0.0 / 100.0 pts assigned).")
        elif opm >= self.OPM_BENCHMARK:
            opm_score = 100.0
        elif opm >= 0.0:
            # Linear between 30.0 and 100.0
            opm_score = 30.0 + (opm / self.OPM_BENCHMARK) * 70.0
            lost = 100.0 - opm_score
            deductions.append(
                f"Operating margin of {opm:.2f}% is below the {self.OPM_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        else:
            opm_score = 0.0
            deductions.append(
                f"Negative operating margin of {opm:.2f}% indicates operating losses (-100.00 pts)."
            )

        # 2. Score Net Profit Margin component
        if npm is None:
            npm_score = 0.0
            deductions.append("Net Profit Margin (NPM) unavailable (0.0 / 100.0 pts assigned).")
        elif npm >= self.NPM_BENCHMARK:
            npm_score = 100.0
        elif npm >= 0.0:
            # Linear between 30.0 and 100.0
            npm_score = 30.0 + (npm / self.NPM_BENCHMARK) * 70.0
            lost = 100.0 - npm_score
            deductions.append(
                f"Net profit margin of {npm:.2f}% is below the {self.NPM_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        else:
            npm_score = 0.0
            deductions.append(
                f"Negative net profit margin of {npm:.2f}% indicates bottom-line losses (-100.00 pts)."
            )

        # Equal weighting within Profitability dimension: 50% OPM + 50% NPM
        composite_score = 0.5 * opm_score + 0.5 * npm_score

        # Margin contraction penalty: positive OPM converted to negative NPM
        if opm is not None and npm is not None:
            if opm > 0.0 and npm < 0.0:
                penalty = 10.0
                composite_score = max(0.0, composite_score - penalty)
                deductions.append(
                    f"Severe margin contraction: Operating profit ({opm:.2f}%) erased into net loss ({npm:.2f}%) (-{penalty:.2f} pts)."
                )

        composite_score = round(composite_score, 2)
        composite_score = max(0.0, min(100.0, composite_score))
        grade = _determine_grade(composite_score)

        return DimensionScoreDTO(
            score=composite_score,
            grade=grade,
            deductions=deductions,
        )
