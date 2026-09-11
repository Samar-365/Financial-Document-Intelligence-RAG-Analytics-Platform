"""Unit tests for Composite Financial Health Score & Rationale Aggregator (Module 8.3)."""

import pytest
from pydantic import ValidationError

from app.analytics import (
    CorporateHealthReportDTO,
    DimensionScoreDTO,
    HealthScoreAggregator,
)


class TestCorporateHealthReportDTO:
    """Test suite for CorporateHealthReportDTO schema and constraints."""

    def test_valid_dto(self):
        growth = DimensionScoreDTO(score=90.0, grade="Excellent")
        dto = CorporateHealthReportDTO(
            overall_score=85.0,
            rating_category="Strong",
            dimension_scores={"growth": growth},
            summary_rationales=["Solid overall performance."],
            disclaimer="Custom disclaimer",
        )
        assert dto.overall_score == 85.0
        assert dto.rating_category == "Strong"
        assert dto.disclaimer == "Custom disclaimer"
        assert len(dto.summary_rationales) == 1

    def test_default_disclaimer(self):
        dto = CorporateHealthReportDTO(
            overall_score=70.0,
            rating_category="Stable",
            dimension_scores={},
        )
        assert "not a certified credit rating" in dto.disclaimer

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            CorporateHealthReportDTO(
                overall_score=-0.1,
                rating_category="Distressed",
                dimension_scores={},
            )

        with pytest.raises(ValidationError):
            CorporateHealthReportDTO(
                overall_score=100.1,
                rating_category="Strong",
                dimension_scores={},
            )


class TestHealthScoreAggregator:
    """Test suite for HealthScoreAggregator logic and weighting."""

    @pytest.fixture
    def aggregator(self):
        return HealthScoreAggregator()

    def test_perfect_scores_strong_rating(self, aggregator):
        g = DimensionScoreDTO(score=100.0, grade="Excellent")
        p = DimensionScoreDTO(score=100.0, grade="Excellent")
        l = DimensionScoreDTO(score=100.0, grade="Excellent")
        lev = DimensionScoreDTO(score=100.0, grade="Excellent")
        cf = DimensionScoreDTO(score=100.0, grade="Excellent")

        report = aggregator.aggregate(
            growth=g, profit=p, liquidity=l, leverage=lev, cash_flow=cf
        )

        assert report.overall_score == 100.0
        assert report.rating_category == "Strong"
        assert len(report.dimension_scores) == 5
        assert report.dimension_scores["growth"] == g
        assert report.dimension_scores["profitability"] == p
        assert report.dimension_scores["liquidity"] == l
        assert report.dimension_scores["leverage"] == lev
        assert report.dimension_scores["cash_flow"] == cf
        assert any("Robust Financial Health" in r for r in report.summary_rationales)
        assert any("Core Strengths" in r for r in report.summary_rationales)

    def test_weighted_score_calculation(self, aggregator):
        # Weights: Growth 20%, Profit 25%, Liquidity 20%, Leverage 20%, Cash Flow 15%
        # Growth: 80 * 0.20 = 16.0
        # Profit: 70 * 0.25 = 17.5
        # Liquidity: 60 * 0.20 = 12.0
        # Leverage: 90 * 0.20 = 18.0
        # Cash Flow: 80 * 0.15 = 12.0
        # Total = 16.0 + 17.5 + 12.0 + 18.0 + 12.0 = 75.50
        g = DimensionScoreDTO(score=80.0, grade="Excellent")
        p = DimensionScoreDTO(score=70.0, grade="Good")
        l = DimensionScoreDTO(score=60.0, grade="Good")
        lev = DimensionScoreDTO(score=90.0, grade="Excellent")
        cf = DimensionScoreDTO(score=80.0, grade="Excellent")

        report = aggregator.aggregate(
            growth=g, profit=p, liquidity=l, leverage=lev, cash_flow=cf
        )

        assert report.overall_score == 75.50
        assert report.rating_category == "Stable"
        assert any("Stable Financial Health" in r for r in report.summary_rationales)

    def test_moderate_rating_tier(self, aggregator):
        # Target score ~55.0 (Moderate: 50.0 to < 65.0)
        # All 55.0
        score_55 = DimensionScoreDTO(score=55.0, grade="Fair")
        report = aggregator.aggregate(
            growth=score_55,
            profit=score_55,
            liquidity=score_55,
            leverage=score_55,
            cash_flow=score_55,
        )

        assert report.overall_score == 55.0
        assert report.rating_category == "Moderate"
        assert any("Moderate Financial Health" in r for r in report.summary_rationales)

    def test_fragile_rating_tier(self, aggregator):
        # Target score ~40.0 (Fragile: 35.0 to < 50.0)
        score_40 = DimensionScoreDTO(score=40.0, grade="Fair")
        report = aggregator.aggregate(
            growth=score_40,
            profit=score_40,
            liquidity=score_40,
            leverage=score_40,
            cash_flow=score_40,
        )

        assert report.overall_score == 40.0
        assert report.rating_category == "Fragile"
        assert any("Fragile Financial Condition" in r for r in report.summary_rationales)

    def test_distressed_rating_tier(self, aggregator):
        # Target score < 35.0 (Distressed)
        score_20 = DimensionScoreDTO(score=20.0, grade="Poor")
        report = aggregator.aggregate(
            growth=score_20,
            profit=score_20,
            liquidity=score_20,
            leverage=score_20,
            cash_flow=score_20,
        )

        assert report.overall_score == 20.0
        assert report.rating_category == "Distressed"
        assert any("Distressed Financial Condition" in r for r in report.summary_rationales)
        assert any("Areas of Vulnerability" in r for r in report.summary_rationales)

    def test_all_zeros_distressed(self, aggregator):
        score_0 = DimensionScoreDTO(score=0.0, grade="Poor")
        report = aggregator.aggregate(
            growth=score_0,
            profit=score_0,
            liquidity=score_0,
            leverage=score_0,
            cash_flow=score_0,
        )

        assert report.overall_score == 0.0
        assert report.rating_category == "Distressed"

    def test_rating_boundary_thresholds(self, aggregator):
        assert aggregator.determine_rating(100.0) == "Strong"
        assert aggregator.determine_rating(80.0) == "Strong"
        assert aggregator.determine_rating(79.99) == "Stable"
        assert aggregator.determine_rating(65.0) == "Stable"
        assert aggregator.determine_rating(64.99) == "Moderate"
        assert aggregator.determine_rating(50.0) == "Moderate"
        assert aggregator.determine_rating(49.99) == "Fragile"
        assert aggregator.determine_rating(35.0) == "Fragile"
        assert aggregator.determine_rating(34.99) == "Distressed"
        assert aggregator.determine_rating(0.0) == "Distressed"

    def test_deductions_compiled_into_rationales(self, aggregator):
        g = DimensionScoreDTO(
            score=70.0,
            grade="Good",
            deductions=["Revenue growth below 10.0% benchmark (-30.0 pts)."],
        )
        p = DimensionScoreDTO(
            score=60.0,
            grade="Good",
            deductions=["Operating margin below 15.0% (-40.0 pts)."],
        )
        l = DimensionScoreDTO(
            score=50.0,
            grade="Fair",
            deductions=["Current ratio indicates negative working capital (-50.0 pts)."],
        )
        lev = DimensionScoreDTO(score=100.0, grade="Excellent", deductions=[])
        cf = DimensionScoreDTO(score=100.0, grade="Excellent", deductions=[])

        report = aggregator.aggregate(
            growth=g, profit=p, liquidity=l, leverage=lev, cash_flow=cf
        )

        # Check that dimensional deduction tags are present
        assert any("[Growth] Revenue growth below 10.0%" in r for r in report.summary_rationales)
        assert any("[Profitability] Operating margin below 15.0%" in r for r in report.summary_rationales)
        assert any("[Liquidity] Current ratio indicates negative working capital" in r for r in report.summary_rationales)

    def test_custom_disclaimer(self):
        custom_disc = "CONFIDENTIAL: Internal research only."
        agg = HealthScoreAggregator(disclaimer=custom_disc)
        dto = DimensionScoreDTO(score=80.0, grade="Excellent")
        report = agg.aggregate(growth=dto, profit=dto, liquidity=dto, leverage=dto, cash_flow=dto)

        assert report.disclaimer == custom_disc

    def test_type_error_on_invalid_arguments(self, aggregator):
        valid = DimensionScoreDTO(score=80.0, grade="Excellent")

        with pytest.raises(TypeError, match="Argument 'growth' must be an instance of DimensionScoreDTO"):
            aggregator.aggregate(
                growth="invalid",  # type: ignore
                profit=valid,
                liquidity=valid,
                leverage=valid,
                cash_flow=valid,
            )

        with pytest.raises(TypeError, match="Argument 'cash_flow' must be an instance of DimensionScoreDTO"):
            aggregator.aggregate(
                growth=valid,
                profit=valid,
                liquidity=valid,
                leverage=valid,
                cash_flow=85.0,  # type: ignore
            )
