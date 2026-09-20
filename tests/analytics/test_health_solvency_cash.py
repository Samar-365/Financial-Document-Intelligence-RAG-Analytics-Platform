"""Unit tests for Solvency & Cash Flow Scoring Engine (Module 8.2)."""

from decimal import Decimal
import pytest

from app.analytics.health_growth_profit import DimensionScoreDTO
from app.analytics.health_solvency_cash import SolvencyCashScorer



class TestLiquidityScoring:
    """Test suite for Liquidity dimension scoring."""

    @pytest.fixture
    def scorer(self):
        return SolvencyCashScorer()

    def test_optimal_current_ratio_range(self, scorer):
        # Boundaries and mid-point of [1.5, 2.5]
        for cr in [1.5, 2.0, 2.5]:
            liq, _ = scorer.score_liquidity_leverage(current_ratio=cr, debt_to_equity=0.5)
            assert liq.score == 100.0
            assert liq.grade == "Excellent"
            assert liq.deductions == []

    def test_current_ratio_moderately_below_benchmark(self, scorer):
        # CR in [1.0, 1.5) -> linear between 50.0 and 100.0
        # CR = 1.25 -> 50 + (0.25 / 0.5) * 50 = 75.0
        liq, _ = scorer.score_liquidity_leverage(current_ratio=1.25, debt_to_equity=0.5)
        assert liq.score == 75.0
        assert liq.grade == "Good"
        assert len(liq.deductions) == 1
        assert "below optimal 1.50 benchmark" in liq.deductions[0]

        # CR = 1.0 -> 50.0
        liq1, _ = scorer.score_liquidity_leverage(current_ratio=1.0, debt_to_equity=0.5)
        assert liq1.score == 50.0
        assert liq1.grade == "Fair"

    def test_current_ratio_below_unity_negative_working_capital(self, scorer):
        # CR in [0.0, 1.0) -> linear between 0.0 and 50.0
        # CR = 0.8 -> 0.8 * 50 = 40.0
        liq, _ = scorer.score_liquidity_leverage(current_ratio=0.8, debt_to_equity=0.5)
        assert liq.score == 40.0
        assert liq.grade == "Fair"
        assert "negative working capital" in liq.deductions[0]

        # CR = 0.4 -> 0.4 * 50 = 20.0
        liq_low, _ = scorer.score_liquidity_leverage(current_ratio=0.4, debt_to_equity=0.5)
        assert liq_low.score == 20.0
        assert liq_low.grade == "Poor"

        # CR = 0.0 -> 0.0
        liq_zero, _ = scorer.score_liquidity_leverage(current_ratio=0.0, debt_to_equity=0.5)
        assert liq_zero.score == 0.0
        assert liq_zero.grade == "Poor"

    def test_negative_current_ratio(self, scorer):
        liq, _ = scorer.score_liquidity_leverage(current_ratio=-0.5, debt_to_equity=0.5)
        assert liq.score == 0.0
        assert liq.grade == "Poor"
        assert "severe capital distortion" in liq.deductions[0]

    def test_current_ratio_mildly_high(self, scorer):
        # CR in (2.5, 4.0] -> linear between 90.0 and 100.0
        # CR = 3.25 -> 100 - ((3.25 - 2.5) / 1.5) * 10 = 95.0
        liq, _ = scorer.score_liquidity_leverage(current_ratio=3.25, debt_to_equity=0.5)
        assert liq.score == 95.0
        assert liq.grade == "Excellent"
        assert "exceeds 2.50 threshold" in liq.deductions[0]

        # CR = 4.0 -> 90.0
        liq_4, _ = scorer.score_liquidity_leverage(current_ratio=4.0, debt_to_equity=0.5)
        assert liq_4.score == 90.0
        assert liq_4.grade == "Excellent"

    def test_current_ratio_excessively_high(self, scorer):
        # CR > 4.0 -> linear down from 90.0 to 75.0 floor
        # CR = 6.0 -> 90 - (2.0 / 4.0) * 15 = 82.5
        liq, _ = scorer.score_liquidity_leverage(current_ratio=6.0, debt_to_equity=0.5)
        assert liq.score == 82.5
        assert liq.grade == "Excellent"
        assert "Excessive current ratio" in liq.deductions[0]

        # CR = 12.0 -> floored at 75.0
        liq_huge, _ = scorer.score_liquidity_leverage(current_ratio=12.0, debt_to_equity=0.5)
        assert liq_huge.score == 75.0
        assert liq_huge.grade == "Good"

    def test_current_ratio_none(self, scorer):
        liq, _ = scorer.score_liquidity_leverage(current_ratio=None, debt_to_equity=0.5)
        assert liq.score == 0.0
        assert liq.grade == "Poor"
        assert "Current Ratio metric unavailable" in liq.deductions[0]


class TestLeverageScoring:
    """Test suite for Leverage dimension scoring."""

    @pytest.fixture
    def scorer(self):
        return SolvencyCashScorer()

    def test_low_leverage_benchmark(self, scorer):
        # D/E in [0.0, 0.50]
        for de in [0.0, 0.25, 0.50]:
            _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=de)
            assert lev.score == 100.0
            assert lev.grade == "Excellent"
            assert lev.deductions == []

    def test_moderate_leverage(self, scorer):
        # D/E in (0.50, 1.00] -> linear between 90.0 and 100.0
        # D/E = 0.75 -> 100 - (0.25 / 0.50) * 10 = 95.0
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=0.75)
        assert lev.score == 95.0
        assert lev.grade == "Excellent"
        assert "reflects moderate leverage" in lev.deductions[0]

        # D/E = 1.00 -> 90.0
        _, lev_1 = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=1.0)
        assert lev_1.score == 90.0
        assert lev_1.grade == "Excellent"

    def test_elevated_leverage_above_conservative(self, scorer):
        # D/E in (1.00, 2.00] -> linear between 50.0 and 90.0
        # D/E = 1.50 -> 90 - (0.5 / 1.0) * 40 = 70.0
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=1.50)
        assert lev.score == 70.0
        assert lev.grade == "Good"
        assert "exceeds conservative 1.00x benchmark" in lev.deductions[0]

        # D/E = 2.00 -> 50.0
        _, lev_2 = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=2.00)
        assert lev_2.score == 50.0
        assert lev_2.grade == "Fair"

    def test_critical_high_leverage(self, scorer):
        # D/E in (2.00, 4.00] -> linear between 10.0 and 50.0
        # D/E = 3.00 -> 50 - (1.0 / 2.0) * 40 = 30.0
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=3.00)
        assert lev.score == 30.0
        assert lev.grade == "Poor"
        assert "High leverage alert" in lev.deductions[0]
        assert "exceeds critical 2.00x threshold" in lev.deductions[0]

        # D/E = 4.00 -> 10.0
        _, lev_4 = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=4.00)
        assert lev_4.score == 10.0
        assert lev_4.grade == "Poor"

    def test_severe_overleveraging(self, scorer):
        # D/E > 4.00 -> 0.0 pts
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=5.50)
        assert lev.score == 0.0
        assert lev.grade == "Poor"
        assert "Severe overleveraging" in lev.deductions[0]

    def test_negative_shareholder_equity_distress(self, scorer):
        # Negative D/E means negative equity / balance sheet insolvency
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=-1.5)
        assert lev.score == 0.0
        assert lev.grade == "Poor"
        assert "Negative shareholder equity" in lev.deductions[0]
        assert "complete net worth erosion" in lev.deductions[0]

    def test_debt_to_equity_none(self, scorer):
        _, lev = scorer.score_liquidity_leverage(current_ratio=2.0, debt_to_equity=None)
        assert lev.score == 0.0
        assert lev.grade == "Poor"
        assert "Debt-to-Equity (D/E) ratio unavailable" in lev.deductions[0]


class TestCashFlowQualityScoring:
    """Test suite for Cash Flow Quality dimension scoring."""

    @pytest.fixture
    def scorer(self):
        return SolvencyCashScorer()

    def test_cfo_exceeds_pat_ideal_conversion(self, scorer):
        # CFO = 150 Cr, PAT = 100 Cr -> ratio = 1.5 >= 1.0
        res = scorer.score_cash_flow(cfo=Decimal("1500000000"), pat=Decimal("1000000000"))
        assert res.score == 100.0
        assert res.grade == "Excellent"
        assert res.deductions == []

    def test_cfo_equals_pat_exact_benchmark(self, scorer):
        # CFO = 100 Cr, PAT = 100 Cr -> ratio = 1.0
        res = scorer.score_cash_flow(cfo=Decimal("1000000000"), pat=Decimal("1000000000"))
        assert res.score == 100.0
        assert res.grade == "Excellent"
        assert res.deductions == []

    def test_moderate_cash_conversion(self, scorer):
        # CFO / PAT in [0.5, 1.0) -> linear between 60.0 and 100.0
        # CFO = 75 Cr, PAT = 100 Cr -> ratio = 0.75 -> 60 + (0.25 / 0.5) * 40 = 80.0
        res = scorer.score_cash_flow(cfo=Decimal("750000000"), pat=Decimal("1000000000"))
        assert res.score == 80.0
        assert res.grade == "Excellent"
        assert len(res.deductions) == 1
        assert "Cash flow conversion of 0.75x is below the 1.00x benchmark" in res.deductions[0]

        # CFO = 50 Cr, PAT = 100 Cr -> ratio = 0.50 -> 60.0
        res_half = scorer.score_cash_flow(cfo=Decimal("500000000"), pat=Decimal("1000000000"))
        assert res_half.score == 60.0
        assert res_half.grade == "Good"

    def test_weak_cash_conversion(self, scorer):
        # CFO / PAT in [0.0, 0.5) -> linear between 20.0 and 60.0
        # CFO = 25 Cr, PAT = 100 Cr -> ratio = 0.25 -> 20 + (0.25 / 0.5) * 40 = 40.0
        res = scorer.score_cash_flow(cfo=Decimal("250000000"), pat=Decimal("1000000000"))
        assert res.score == 40.0
        assert res.grade == "Fair"
        assert "Poor cash flow quality" in res.deductions[0]

        # CFO = 0 Cr, PAT = 100 Cr -> ratio = 0.0 -> 20.0
        res_zero = scorer.score_cash_flow(cfo=Decimal("0"), pat=Decimal("1000000000"))
        assert res_zero.score == 20.0
        assert res_zero.grade == "Poor"

    def test_severe_divergence_positive_pat_negative_cfo(self, scorer):
        # Positive Net Income (paper profit) but negative operating cash flow!
        res = scorer.score_cash_flow(cfo=Decimal("-300000000"), pat=Decimal("1000000000"))
        assert res.score == 0.0
        assert res.grade == "Poor"
        assert "Severe earnings quality red flag" in res.deductions[0]
        assert "negative operating cash flow" in res.deductions[0]

    def test_loss_making_company_with_positive_cfo(self, scorer):
        # PAT = -50 Cr, but CFO = +30 Cr (cash resilience despite accounting loss)
        res = scorer.score_cash_flow(cfo=Decimal("300000000"), pat=Decimal("-500000000"))
        assert res.score == 65.0
        assert res.grade == "Good"
        assert "operational cash resilience" in res.deductions[0]

    def test_dual_burn_negative_pat_and_negative_cfo(self, scorer):
        # Both PAT and CFO negative
        res = scorer.score_cash_flow(cfo=Decimal("-400000000"), pat=Decimal("-800000000"))
        assert res.score == 0.0
        assert res.grade == "Poor"
        assert "Operational cash burn" in res.deductions[0]

    def test_break_even_pat(self, scorer):
        # PAT == 0
        res_pos = scorer.score_cash_flow(cfo=Decimal("50000000"), pat=Decimal("0"))
        assert res_pos.score == 75.0
        assert res_pos.grade == "Good"

        res_neg = scorer.score_cash_flow(cfo=Decimal("-20000000"), pat=Decimal("0"))
        assert res_neg.score == 0.0
        assert res_neg.grade == "Poor"

    def test_none_metrics(self, scorer):
        res1 = scorer.score_cash_flow(cfo=None, pat=Decimal("1000000000"))
        assert res1.score == 0.0
        assert res1.grade == "Poor"
        assert "metric unavailable" in res1.deductions[0]

        res2 = scorer.score_cash_flow(cfo=Decimal("1000000000"), pat=None)
        assert res2.score == 0.0
        assert res2.grade == "Poor"

        res3 = scorer.score_cash_flow(cfo=None, pat=None)
        assert res3.score == 0.0
        assert res3.grade == "Poor"
