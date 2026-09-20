"""Unit tests for Growth and Profitability Scoring Engine (Module 8.1)."""

import pytest
from pydantic import ValidationError

from app.analytics import DimensionScoreDTO, GrowthProfitScorer


class TestDimensionScoreDTO:
    """Test suite for DimensionScoreDTO validation and contract compliance."""

    def test_valid_dto(self):
        dto = DimensionScoreDTO(
            score=85.5,
            grade="Excellent",
            deductions=["Minor revenue underperformance (-5.0 pts)."],
        )
        assert dto.score == 85.5
        assert dto.grade == "Excellent"
        assert len(dto.deductions) == 1

    def test_empty_deductions_default(self):
        dto = DimensionScoreDTO(score=100.0, grade="Excellent")
        assert dto.deductions == []

    def test_score_boundary_validation(self):
        # Score cannot be negative
        with pytest.raises(ValidationError):
            DimensionScoreDTO(score=-0.1, grade="Poor")

        # Score cannot exceed 100
        with pytest.raises(ValidationError):
            DimensionScoreDTO(score=100.1, grade="Excellent")


class TestGrowthScoring:
    """Test suite for Growth dimension scoring."""

    @pytest.fixture
    def scorer(self):
        return GrowthProfitScorer()

    def test_benchmark_exceeded(self, scorer):
        # Rev > 10% and PAT > 15%
        result = scorer.score_growth(rev_growth=15.0, pat_growth=25.0)
        assert result.score == 100.0
        assert result.grade == "Excellent"
        assert result.deductions == []

    def test_exact_benchmark(self, scorer):
        # Rev = 10% and PAT = 15%
        result = scorer.score_growth(rev_growth=10.0, pat_growth=15.0)
        assert result.score == 100.0
        assert result.grade == "Excellent"
        assert result.deductions == []

    def test_moderate_growth(self, scorer):
        # Rev = 5.0% (linear: 40 + 5/10 * 60 = 70.0)
        # PAT = 7.5% (linear: 40 + 7.5/15 * 60 = 70.0)
        result = scorer.score_growth(rev_growth=5.0, pat_growth=7.5)
        assert result.score == 70.0
        assert result.grade == "Good"
        assert len(result.deductions) == 2
        assert "below the 10.0% benchmark" in result.deductions[0]
        assert "below the 15.0% benchmark" in result.deductions[1]

    def test_low_positive_growth(self, scorer):
        # Rev = 2.0% (40 + 0.2*60 = 52.0)
        # PAT = 3.0% (40 + 0.2*60 = 52.0)
        result = scorer.score_growth(rev_growth=2.0, pat_growth=3.0)
        assert result.score == 52.0
        assert result.grade == "Fair"

    def test_revenue_and_pat_contraction(self, scorer):
        # Contraction between 0% and -20%
        # Rev = -10.0% (linear: max(0, 40 + (-10/20)*40) = 20.0)
        # PAT = -10.0% (linear: max(0, 40 + (-10/20)*40) = 20.0)
        result = scorer.score_growth(rev_growth=-10.0, pat_growth=-10.0)
        assert result.score == 20.0
        assert result.grade == "Poor"
        assert any("Revenue contraction" in d for d in result.deductions)
        assert any("PAT contraction" in d for d in result.deductions)

    def test_severe_contraction_zero_floor(self, scorer):
        # Contraction beyond -20%
        result = scorer.score_growth(rev_growth=-30.0, pat_growth=-25.0)
        assert result.score == 0.0
        assert result.grade == "Poor"
        assert any("Severe revenue contraction" in d for d in result.deductions)
        assert any("Severe PAT contraction" in d for d in result.deductions)

    def test_both_metrics_none(self, scorer):
        result = scorer.score_growth(rev_growth=None, pat_growth=None)
        assert result.score == 0.0
        assert result.grade == "Poor"
        assert len(result.deductions) == 2
        assert "YoY Revenue Growth metric unavailable" in result.deductions[0]
        assert "YoY PAT Growth metric unavailable" in result.deductions[1]

    def test_partial_metric_none(self, scorer):
        # Rev is 10.0% (100 pts), PAT is None (0 pts) -> 50.0 pts
        result = scorer.score_growth(rev_growth=10.0, pat_growth=None)
        assert result.score == 50.0
        assert result.grade == "Fair"
        assert len(result.deductions) == 1
        assert "YoY PAT Growth metric unavailable" in result.deductions[0]


class TestProfitabilityScoring:
    """Test suite for Profitability dimension scoring."""

    @pytest.fixture
    def scorer(self):
        return GrowthProfitScorer()

    def test_benchmark_exceeded(self, scorer):
        # OPM > 15% and NPM > 10%
        result = scorer.score_profitability(opm=20.0, npm=14.0)
        assert result.score == 100.0
        assert result.grade == "Excellent"
        assert result.deductions == []

    def test_exact_benchmark(self, scorer):
        result = scorer.score_profitability(opm=15.0, npm=10.0)
        assert result.score == 100.0
        assert result.grade == "Excellent"
        assert result.deductions == []

    def test_moderate_margins(self, scorer):
        # OPM = 7.5% (linear: 30 + 7.5/15 * 70 = 65.0)
        # NPM = 5.0% (linear: 30 + 5.0/10 * 70 = 65.0)
        result = scorer.score_profitability(opm=7.5, npm=5.0)
        assert result.score == 65.0
        assert result.grade == "Good"
        assert len(result.deductions) == 2
        assert "Operating margin of 7.50% is below the 15.0% benchmark" in result.deductions[0]
        assert "Net profit margin of 5.00% is below the 10.0% benchmark" in result.deductions[1]

    def test_low_positive_margins(self, scorer):
        # OPM = 3.0% (30 + 3/15 * 70 = 44.0)
        # NPM = 2.0% (30 + 2/10 * 70 = 44.0)
        result = scorer.score_profitability(opm=3.0, npm=2.0)
        assert result.score == 44.0
        assert result.grade == "Fair"

    def test_operating_and_net_loss(self, scorer):
        result = scorer.score_profitability(opm=-4.0, npm=-6.0)
        assert result.score == 0.0
        assert result.grade == "Poor"
        assert any("Negative operating margin" in d for d in result.deductions)
        assert any("Negative net profit margin" in d for d in result.deductions)

    def test_margin_contraction_penalty(self, scorer):
        # OPM positive (15.0% -> 100 pts), but NPM negative (-5.0% -> 0 pts)
        # Base: 0.5 * 100 + 0.5 * 0 = 50.0
        # Margin contraction penalty: -10.0 pts -> 40.0 pts
        result = scorer.score_profitability(opm=15.0, npm=-5.0)
        assert result.score == 40.0
        assert result.grade == "Fair"
        assert any("Severe margin contraction" in d for d in result.deductions)

    def test_both_margins_none(self, scorer):
        result = scorer.score_profitability(opm=None, npm=None)
        assert result.score == 0.0
        assert result.grade == "Poor"
        assert len(result.deductions) == 2
        assert "Operating Profit Margin (OPM) unavailable" in result.deductions[0]
        assert "Net Profit Margin (NPM) unavailable" in result.deductions[1]

    def test_partial_margin_none(self, scorer):
        # OPM is 15.0% (100 pts), NPM is None (0 pts) -> 50.0 pts
        result = scorer.score_profitability(opm=15.0, npm=None)
        assert result.score == 50.0
        assert result.grade == "Fair"
        assert len(result.deductions) == 1
        assert "Net Profit Margin (NPM) unavailable" in result.deductions[0]
