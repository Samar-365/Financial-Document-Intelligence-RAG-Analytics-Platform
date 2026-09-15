"""Growth and Profitability Scoring Engine for Financial Analytics (Module 8.1).

Responsible for:
1. Scoring YoY Revenue Growth (>10% -> 100) and PAT Growth (>15% -> 100) using piecewise linear mapping.
2. Scoring Operating Profit Margin (>15% -> 100) and Net Profit Margin (>10% -> 100) with margin contraction deductions.
3. Generating structured DimensionScoreDTO with scores (0-100), qualitative grades, and explainable deductions.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DimensionScoreDTO(BaseModel): #DTO representing a dimensional health evaluation score (0-100), qualitative grade, and audit deductions
    """Data Transfer Object representing a dimension score in the 5D corporate health model."""

    score: float = Field( #Deterministic dimensional score bounded strictly between 0.0 and 100.0
        ...,
        ge=0.0,
        le=100.0,
        description="Deterministic dimensional score bounded strictly between 0.0 and 100.0.",
    )
    grade: str = Field( #Qualitative rating tier: 'Excellent', 'Good', 'Fair', or 'Poor'
        ...,
        description="Qualitative rating category: 'Excellent', 'Good', 'Fair', or 'Poor'.",
    )
    deductions: List[str] = Field( #Detailed list of explainable deduction rationale strings
        default_factory=list,
        description="Detailed list of explainable deduction rationale strings.",
    )


def _determine_grade(score: float) -> str: #Helper function mapping numeric score (0-100) to qualitative rating category
    """Maps a numerical score (0-100) to a qualitative grade tier."""
    if score >= 80.0: #80-100: Excellent financial health
        return "Excellent"
    if score >= 60.0: #60-79: Good financial health
        return "Good"
    if score >= 40.0: #40-59: Fair financial health
        return "Fair"
    return "Poor" #Below 40: Poor financial health / elevated risk


class GrowthProfitScorer: #Evaluates corporate growth and profitability dimensions using deterministic financial benchmarks
    """Evaluates corporate growth and profitability dimensions using deterministic financial benchmarks.

    Technical Tasks:
    1. Growth Scoring Engine (20% weight): YoY Revenue Growth and PAT Growth with piecewise linear mapping.
    2. Profitability Scoring Engine (25% weight): OPM and NPM scoring with margin contraction penalties.
    """

    # Industry benchmark standards for full marks
    REV_GROWTH_BENCHMARK: float = 10.0  # >10% YoY revenue growth yields full 100 pts
    PAT_GROWTH_BENCHMARK: float = 15.0  # >15% YoY net profit growth yields full 100 pts
    OPM_BENCHMARK: float = 15.0         # >15% Operating Profit Margin yields full 100 pts
    NPM_BENCHMARK: float = 10.0         # >10% Net Profit Margin yields full 100 pts

    def score_growth( #Scores Growth dimension (20% of overall corporate health): 50% revenue growth + 50% PAT growth
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
        deductions: List[str] = [] #List of reasons explaining any lost points

        # 1. Score Revenue Growth component
        if rev_growth is None: #If metric was not found
            rev_score = 0.0
            deductions.append("YoY Revenue Growth metric unavailable (0.0 / 100.0 pts assigned).")
        elif rev_growth >= self.REV_GROWTH_BENCHMARK: #Exceeds 10% growth target
            rev_score = 100.0
        elif rev_growth >= 0.0: #Positive growth but below 10% benchmark
            # Linear between 40.0 and 100.0
            rev_score = 40.0 + (rev_growth / self.REV_GROWTH_BENCHMARK) * 60.0 #Scale score from 40 to 100
            lost = 100.0 - rev_score
            deductions.append(
                f"Revenue growth of {rev_growth:.2f}% is below the {self.REV_GROWTH_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        elif rev_growth >= -20.0: #Negative growth between -20% and 0%
            # Linear between 0.0 and 40.0
            rev_score = max(0.0, 40.0 + (rev_growth / 20.0) * 40.0) #Scale score from 0 to 40
            lost = 100.0 - rev_score
            deductions.append(
                f"Revenue contraction of {abs(rev_growth):.2f}% severely penalizes growth (-{lost:.2f} pts)."
            )
        else: #Severe revenue contraction worse than -20%
            rev_score = 0.0
            deductions.append(
                f"Severe revenue contraction of {abs(rev_growth):.2f}% exceeds -20.0% (-100.00 pts)."
            )

        # 2. Score PAT Growth component
        if pat_growth is None: #If PAT growth is unavailable
            pat_score = 0.0
            deductions.append("YoY PAT Growth metric unavailable (0.0 / 100.0 pts assigned).")
        elif pat_growth >= self.PAT_GROWTH_BENCHMARK: #Exceeds 15% PAT growth target
            pat_score = 100.0
        elif pat_growth >= 0.0: #Positive profit growth but below 15% benchmark
            # Linear between 40.0 and 100.0
            pat_score = 40.0 + (pat_growth / self.PAT_GROWTH_BENCHMARK) * 60.0 #Scale score from 40 to 100
            lost = 100.0 - pat_score
            deductions.append(
                f"PAT growth of {pat_growth:.2f}% is below the {self.PAT_GROWTH_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        elif pat_growth >= -20.0: #Profit contraction down to -20%
            # Linear between 0.0 and 40.0
            pat_score = max(0.0, 40.0 + (pat_growth / 20.0) * 40.0) #Scale score from 0 to 40
            lost = 100.0 - pat_score
            deductions.append(
                f"PAT contraction of {abs(pat_growth):.2f}% severely penalizes bottom-line growth (-{lost:.2f} pts)."
            )
        else: #Severe profit collapse worse than -20%
            pat_score = 0.0
            deductions.append(
                f"Severe PAT contraction of {abs(pat_growth):.2f}% exceeds -20.0% (-100.00 pts)."
            )

        # Equal weighting within Growth dimension: 50% Revenue + 50% PAT
        composite_score = round(0.5 * rev_score + 0.5 * pat_score, 2) #Combine 50% revenue + 50% PAT
        composite_score = max(0.0, min(100.0, composite_score)) #Clamp cleanly between 0 and 100
        grade = _determine_grade(composite_score) #Assign qualitative tier (Excellent, Good, Fair, Poor)

        return DimensionScoreDTO( #Return structured score DTO
            score=composite_score,
            grade=grade,
            deductions=deductions,
        )

    def score_profitability( #Scores Profitability dimension (25% of overall corporate health): 50% OPM + 50% NPM
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
        deductions: List[str] = [] #List of reasons explaining any lost points

        # 1. Score Operating Profit Margin component
        if opm is None: #Metric missing
            opm_score = 0.0
            deductions.append("Operating Profit Margin (OPM) unavailable (0.0 / 100.0 pts assigned).")
        elif opm >= self.OPM_BENCHMARK: #Exceeds 15% operating margin target
            opm_score = 100.0
        elif opm >= 0.0: #Positive operating margin but below 15% benchmark
            # Linear between 30.0 and 100.0
            opm_score = 30.0 + (opm / self.OPM_BENCHMARK) * 70.0 #Scale score from 30 to 100
            lost = 100.0 - opm_score
            deductions.append(
                f"Operating margin of {opm:.2f}% is below the {self.OPM_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        else: #Negative operating margin means business loses money on its core operations
            opm_score = 0.0
            deductions.append(
                f"Negative operating margin of {opm:.2f}% indicates operating losses (-100.00 pts)."
            )

        # 2. Score Net Profit Margin component
        if npm is None: #Metric missing
            npm_score = 0.0
            deductions.append("Net Profit Margin (NPM) unavailable (0.0 / 100.0 pts assigned).")
        elif npm >= self.NPM_BENCHMARK: #Exceeds 10% net margin target
            npm_score = 100.0
        elif npm >= 0.0: #Positive net margin but below 10% benchmark
            # Linear between 30.0 and 100.0
            npm_score = 30.0 + (npm / self.NPM_BENCHMARK) * 70.0 #Scale score from 30 to 100
            lost = 100.0 - npm_score
            deductions.append(
                f"Net profit margin of {npm:.2f}% is below the {self.NPM_BENCHMARK:.1f}% benchmark (-{lost:.2f} pts)."
            )
        else: #Negative net margin means net losses
            npm_score = 0.0
            deductions.append(
                f"Negative net profit margin of {npm:.2f}% indicates bottom-line losses (-100.00 pts)."
            )

        # Equal weighting within Profitability dimension: 50% OPM + 50% NPM
        composite_score = 0.5 * opm_score + 0.5 * npm_score #Blend OPM and NPM equally

        # Margin contraction penalty: positive OPM converted to negative NPM (e.g. debt interest wipes out profit)
        if opm is not None and npm is not None:
            if opm > 0.0 and npm < 0.0: #Operating profit was positive, but net loss occurred
                penalty = 10.0
                composite_score = max(0.0, composite_score - penalty) #Deduct 10 penalty points
                deductions.append(
                    f"Severe margin contraction: Operating profit ({opm:.2f}%) erased into net loss ({npm:.2f}%) (-{penalty:.2f} pts)."
                )

        composite_score = round(composite_score, 2) #Round to 2 decimal places
        composite_score = max(0.0, min(100.0, composite_score)) #Clamp between 0 and 100
        grade = _determine_grade(composite_score) #Assign grade (Excellent, Good, Fair, Poor)

        return DimensionScoreDTO( #Return structured score DTO
            score=composite_score,
            grade=grade,
            deductions=deductions,
        )
