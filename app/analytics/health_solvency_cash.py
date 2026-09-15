"""Solvency & Cash Flow Scoring Engine for Financial Analytics (Module 8.2).

Responsible for:
1. Scoring Liquidity dimension (20% weight) based on Current Ratio (optimal between 1.5 and 2.5).
2. Scoring Leverage dimension (20% weight) based on Debt-to-Equity ratio (penalizing D/E > 2.0x, 0 pts for negative equity).
3. Scoring Cash Flow Quality dimension (15% weight) based on CFO / Net Income ratio (>= 1.0 -> 100),
   penalizing paper earnings not backed by operational cash collections.
4. Returning structured DimensionScoreDTO objects with scores (0-100), qualitative grades, and explainable deductions.
"""

from decimal import Decimal
from typing import List, Optional, Tuple

from app.analytics.health_growth_profit import DimensionScoreDTO, _determine_grade


class SolvencyCashScorer: #Evaluates corporate solvency, liquidity, and cash flow conversion dimensions using deterministic benchmarks
    """Evaluates corporate solvency, liquidity, and cash flow conversion dimensions using deterministic benchmarks.

    Technical Tasks:
    1. Liquidity & Leverage Scoring (40% total weight in 5D model):
       - Liquidity (20%): Current Ratio optimal between 1.5 and 2.5.
       - Leverage (20%): Debt-to-Equity optimal < 1.0x, penalizing D/E > 2.0x, 0 for negative equity.
    2. Cash Flow Quality Scoring (15% total weight in 5D model):
       - CFO / PAT ratio (>= 1.0 -> 100 pts), penalizing paper earnings not backed by operational cash.
    """

    # Benchmark thresholds
    CR_LOWER_OPTIMAL: float = 1.50 #Optimal lower bound for current ratio (1.5x)
    CR_UPPER_OPTIMAL: float = 2.50 #Optimal upper bound for current ratio (2.5x)
    DE_CONSERVATIVE_BENCHMARK: float = 1.00 #Conservative debt ceiling (D/E <= 1.0x)
    DE_CRITICAL_THRESHOLD: float = 2.00 #High debt risk threshold (D/E > 2.0x)
    CFO_PAT_BENCHMARK: float = 1.00 #Cash conversion standard: CFO should equal or exceed reported PAT

    def score_liquidity_leverage( #Helper method scoring both Liquidity (20%) and Leverage (20%) dimensions together
        self, current_ratio: Optional[float], debt_to_equity: Optional[float]
    ) -> Tuple[DimensionScoreDTO, DimensionScoreDTO]:
        """Scores Liquidity (20%) and Leverage (20%) dimensions.

        Args:
            current_ratio: Current Assets / Current Liabilities ratio (e.g., 2.1).
            debt_to_equity: Total Debt / Shareholder Equity ratio (e.g., 0.85).

        Returns:
            Tuple[DimensionScoreDTO, DimensionScoreDTO]: (liquidity_score_dto, leverage_score_dto)
        """
        liquidity_dto = self._score_liquidity(current_ratio) #Score Liquidity dimension
        leverage_dto = self._score_leverage(debt_to_equity) #Score Leverage dimension
        return liquidity_dto, leverage_dto

    def _score_liquidity(self, current_ratio: Optional[float]) -> DimensionScoreDTO: #Evaluates short-term liquidity buffer based on Current Ratio
        """Evaluates Liquidity dimension based on Current Ratio.

        Piecewise linear mapping:
        - None: 0.0 pts (unavailable)
        - CR in [1.5, 2.5]: 100.0 pts (optimal liquidity buffer)
        - CR in [1.0, 1.5): 50.0 to 100.0 pts (linear)
        - CR in [0.0, 1.0): 0.0 to 50.0 pts (linear, negative working capital penalty)
        - CR < 0.0: 0.0 pts (distressed/invalid)
        - CR in (2.5, 4.0]: 90.0 to 100.0 pts (mild capital inefficiency deduction)
        - CR > 4.0: 75.0 to 90.0 pts (substantial idle liquidity deduction, floored at 75.0)

        Args:
            current_ratio: Current Assets / Current Liabilities.

        Returns:
            DimensionScoreDTO containing final score (0-100), grade, and deductions.
        """
        deductions: List[str] = [] #Collector for audit explanations

        if current_ratio is None: #Metric missing
            score = 0.0
            deductions.append("Current Ratio metric unavailable (0.0 / 100.0 pts assigned).")
        elif current_ratio < 0.0: #Negative ratio is an invalid balance sheet state
            score = 0.0
            deductions.append(
                f"Negative current ratio of {current_ratio:.2f} indicates severe capital distortion or distressed balance sheet (-100.00 pts)."
            )
        elif self.CR_LOWER_OPTIMAL <= current_ratio <= self.CR_UPPER_OPTIMAL: #Sweet spot [1.5, 2.5] receives full 100 points
            score = 100.0
        elif 1.0 <= current_ratio < self.CR_LOWER_OPTIMAL: #Buffer is tight [1.0, 1.5), scale score from 50 to 100
            # Linear between 50.0 and 100.0
            score = 50.0 + ((current_ratio - 1.0) / (self.CR_LOWER_OPTIMAL - 1.0)) * 50.0
            lost = 100.0 - score
            deductions.append(
                f"Current ratio of {current_ratio:.2f} is below optimal {self.CR_LOWER_OPTIMAL:.2f} benchmark (-{lost:.2f} pts), indicating potential short-term working capital pressure."
            )
        elif 0.0 <= current_ratio < 1.0: #Current liabilities exceed current assets (negative working capital)
            # Linear between 0.0 and 50.0
            score = max(0.0, (current_ratio / 1.0) * 50.0) #Scale score from 0 to 50
            lost = 100.0 - score
            deductions.append(
                f"Current ratio of {current_ratio:.2f} is below 1.00 (-{lost:.2f} pts); current liabilities exceed current assets (negative working capital)."
            )
        elif self.CR_UPPER_OPTIMAL < current_ratio <= 4.0: #Mild deduction for holding excess cash or inventory
            # Linear between 90.0 and 100.0
            score = 100.0 - ((current_ratio - self.CR_UPPER_OPTIMAL) / (4.0 - self.CR_UPPER_OPTIMAL)) * 10.0
            lost = 100.0 - score
            deductions.append(
                f"Current ratio of {current_ratio:.2f} exceeds {self.CR_UPPER_OPTIMAL:.2f} threshold (-{lost:.2f} pts), suggesting mildly suboptimal cash or inventory deployment."
            )
        else:
            # Excessive liquidity > 4.0: linear down from 90.0 to 75.0
            score = max(75.0, 90.0 - ((current_ratio - 4.0) / 4.0) * 15.0) #Floored at 75.0 pts
            lost = 100.0 - score
            deductions.append(
                f"Excessive current ratio of {current_ratio:.2f} significantly exceeds {self.CR_UPPER_OPTIMAL:.2f} (-{lost:.2f} pts), indicating substantial idle liquidity or asset underutilization."
            )

        score = round(max(0.0, min(100.0, score)), 2) #Round and clamp score between 0 and 100
        grade = _determine_grade(score) #Assign grade category

        return DimensionScoreDTO( #Return structured score DTO
            score=score,
            grade=grade,
            deductions=deductions,
        )

    def _score_leverage(self, debt_to_equity: Optional[float]) -> DimensionScoreDTO: #Evaluates solvency risk based on Debt-to-Equity ratio
        """Evaluates Leverage dimension based on Debt-to-Equity ratio.

        Piecewise linear mapping:
        - None: 0.0 pts (unavailable)
        - D/E < 0.0: 0.0 pts (negative shareholder equity = capital erosion / distress)
        - D/E in [0.0, 0.5]: 100.0 pts (minimal leverage, pristine balance sheet)
        - D/E in (0.5, 1.0]: 90.0 to 100.0 pts (conservative, healthy leverage)
        - D/E in (1.0, 2.0]: 50.0 to 90.0 pts (elevated leverage exceeding 1.0x benchmark)
        - D/E in (2.0, 4.0]: 10.0 to 50.0 pts (high debt burden exceeding 2.0x threshold)
        - D/E > 4.0: 0.0 pts (severe overleveraging / insolvency vulnerability)

        Args:
            debt_to_equity: Total Debt / Shareholder Equity.

        Returns:
            DimensionScoreDTO containing final score (0-100), grade, and deductions.
        """
        deductions: List[str] = [] #Collector for audit explanations

        if debt_to_equity is None: #Metric missing
            score = 0.0
            deductions.append("Debt-to-Equity (D/E) ratio unavailable (0.0 / 100.0 pts assigned).")
        elif debt_to_equity < 0.0: #Negative shareholder equity indicates accumulated losses exceeding all capital
            score = 0.0
            deductions.append(
                f"Negative shareholder equity (D/E = {debt_to_equity:.2f}x) indicates balance sheet distress and complete net worth erosion (-100.00 pts)."
            )
        elif 0.0 <= debt_to_equity <= 0.50: #Pristine debt-free or low-debt balance sheet yields full 100 points
            score = 100.0
        elif 0.50 < debt_to_equity <= self.DE_CONSERVATIVE_BENCHMARK: #Conservative leverage (D/E <= 1.0x) scales 90 to 100
            # Linear between 90.0 and 100.0
            score = 100.0 - ((debt_to_equity - 0.50) / 0.50) * 10.0
            lost = 100.0 - score
            deductions.append(
                f"Debt-to-Equity ratio of {debt_to_equity:.2f}x reflects moderate leverage (-{lost:.2f} pts)."
            )
        elif self.DE_CONSERVATIVE_BENCHMARK < debt_to_equity <= self.DE_CRITICAL_THRESHOLD: #Elevated debt (1.0x to 2.0x) scales 50 to 90
            # Linear between 50.0 and 90.0
            score = 90.0 - ((debt_to_equity - self.DE_CONSERVATIVE_BENCHMARK) / (self.DE_CRITICAL_THRESHOLD - self.DE_CONSERVATIVE_BENCHMARK)) * 40.0
            lost = 100.0 - score
            deductions.append(
                f"Debt-to-Equity ratio of {debt_to_equity:.2f}x exceeds conservative {self.DE_CONSERVATIVE_BENCHMARK:.2f}x benchmark (-{lost:.2f} pts)."
            )
        elif self.DE_CRITICAL_THRESHOLD < debt_to_equity <= 4.00: #Heavy debt burden (2.0x to 4.0x) scales 10 to 50
            # Linear between 10.0 and 50.0
            score = 50.0 - ((debt_to_equity - self.DE_CRITICAL_THRESHOLD) / (4.00 - self.DE_CRITICAL_THRESHOLD)) * 40.0
            lost = 100.0 - score
            deductions.append(
                f"High leverage alert: Debt-to-Equity ratio of {debt_to_equity:.2f}x exceeds critical {self.DE_CRITICAL_THRESHOLD:.2f}x threshold (-{lost:.2f} pts), posing elevated solvency risk."
            )
        else: #Extreme overleveraging > 4.0x
            score = 0.0
            deductions.append(
                f"Severe overleveraging: Debt-to-Equity ratio of {debt_to_equity:.2f}x exceeds 4.00x (-100.00 pts), indicating high bankruptcy or refinancing vulnerability."
            )

        score = round(max(0.0, min(100.0, score)), 2) #Round and clamp score
        grade = _determine_grade(score) #Assign grade

        return DimensionScoreDTO( #Return structured score DTO
            score=score,
            grade=grade,
            deductions=deductions,
        )

    def score_cash_flow(self, cfo: Optional[Decimal], pat: Optional[Decimal]) -> DimensionScoreDTO: #Scores Cash Flow Quality (15% weight) by verifying cash supports net profit
        """Scores Cash Flow Quality (15% weight) dimension based on CFO to Net Income (PAT) ratio.

        Benchmark:
        - CFO / PAT >= 1.0 -> 100 pts.
        - Penalizes paper earnings not backed by operational cash collections.

        Piecewise mapping:
        - If cfo or pat is None -> 0.0 pts (unavailable)
        - When PAT > 0:
            - CFO / PAT >= 1.0 -> 100.0 pts (ideal cash conversion)
            - CFO / PAT in [0.5, 1.0) -> 60.0 to 100.0 pts (moderate cash conversion)
            - CFO / PAT in [0.0, 0.5) -> 20.0 to 60.0 pts (weak cash conversion)
            - CFO < 0 -> 0.0 pts (severe divergence: positive accounting net profit with operational cash drain)
        - When PAT < 0:
            - CFO > 0 -> 65.0 pts (operational cash flow resilience despite accounting net loss)
            - CFO <= 0 -> 0.0 pts (dual operational and accounting burn)
        - When PAT == 0:
            - CFO > 0 -> 75.0 pts
            - CFO <= 0 -> 0.0 pts

        Args:
            cfo: Operating Cash Flow (from Cash Flow Statement).
            pat: Net Income / Profit After Tax (from P&L Statement).

        Returns:
            DimensionScoreDTO containing final score (0-100), grade, and deductions.
        """
        deductions: List[str] = [] #Collector for audit explanations

        if cfo is None or pat is None: #If either cash flow or profit is missing
            score = 0.0
            deductions.append(
                "Operating Cash Flow (CFO) or Net Income (PAT) metric unavailable (0.0 / 100.0 pts assigned)."
            )
            return DimensionScoreDTO(score=0.0, grade="Poor", deductions=deductions)

        cfo_val = float(cfo) #Convert Decimal to float
        pat_val = float(pat)

        if pat_val > 0.0: #When business reports positive net income
            ratio = cfo_val / pat_val #Cash conversion ratio
            if ratio >= self.CFO_PAT_BENCHMARK: #CFO >= PAT: Real cash generation matches or beats accounting profits (100 pts)
                score = 100.0
            elif 0.50 <= ratio < self.CFO_PAT_BENCHMARK: #CFO covers 50-100% of PAT
                # Linear between 60.0 and 100.0
                score = 60.0 + ((ratio - 0.50) / (self.CFO_PAT_BENCHMARK - 0.50)) * 40.0
                lost = 100.0 - score
                deductions.append(
                    f"Cash flow conversion of {ratio:.2f}x is below the {self.CFO_PAT_BENCHMARK:.2f}x benchmark (-{lost:.2f} pts); operational cash lags reported net income."
                )
            elif 0.0 <= ratio < 0.50: #Weak cash conversion (under 50% of PAT)
                # Linear between 20.0 and 60.0
                score = 20.0 + (ratio / 0.50) * 40.0
                lost = 100.0 - score
                deductions.append(
                    f"Poor cash flow quality: CFO/PAT ratio of {ratio:.2f}x indicates weak operational cash generation relative to reported profits (-{lost:.2f} pts)."
                )
            else: #CRITICAL RED FLAG: Positive net profit on paper, but negative operating cash flow in reality
                # CFO is negative while PAT is positive
                score = 0.0
                deductions.append(
                    f"Severe earnings quality red flag: Positive net profit of {pat_val:.2f} accompanied by negative operating cash flow (CFO = {cfo_val:.2f}) (-100.00 pts)."
                )
        elif pat_val < 0.0: #When business reports accounting net loss
            if cfo_val > 0.0: #Operational cash flow is positive despite net loss (e.g., due to non-cash depreciation)
                score = 65.0
                deductions.append(
                    f"Operating cash flow is positive ({cfo_val:.2f}) despite accounting net loss ({pat_val:.2f}), reflecting operational cash resilience (-35.00 pts)."
                )
            else: #Both accounting and operational cash flows are negative (severe double burn)
                score = 0.0
                deductions.append(
                    f"Operational cash burn: Both operating cash flow ({cfo_val:.2f}) and net profit ({pat_val:.2f}) are negative (-100.00 pts)."
                )
        else:
            # pat_val == 0.0 (Break-even net income)
            if cfo_val > 0.0:
                score = 75.0
                deductions.append(
                    f"Positive operating cash flow ({cfo_val:.2f}) with break-even net income (-25.00 pts)."
                )
            else:
                score = 0.0
                deductions.append(
                    "Break-even net income with non-positive operating cash flow (-100.00 pts)."
                )

        score = round(max(0.0, min(100.0, score)), 2) #Round and clamp score between 0 and 100
        grade = _determine_grade(score) #Assign grade

        return DimensionScoreDTO( #Return structured score DTO
            score=score,
            grade=grade,
            deductions=deductions,
        )
